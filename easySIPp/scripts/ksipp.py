from django.conf import settings
from django.http import HttpResponse
import os, shlex, socket, time
import subprocess
from .kstun import get_ip_info
from .modify import tmpXmlBehindNAT, modifynumberxmlpath
import psutil, os, re
import logging

logger = logging.getLogger(__name__)

sipp = str(settings.BASE_DIR / 'easySIPp' / 'sipp')

######## For behind NAT sipp
def stun4nat(xmlName, srcPort, stunServer):
    stun_host_str = ''.join(stunServer)
    nat_type, external_ip, external_port = get_ip_info(stun_host=stun_host_str, source_port=int(srcPort))
    if external_ip is not None and external_port is not None:
        newXmlPath = tmpXmlBehindNAT(xmlName, external_ip, external_port)
    else:
        return None
    return newXmlPath

# get free udp port for controlling sipp through -cp
def get_free_control_port(start=8888, end=8948):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free UDP port available")


def run_sipp_in_background(command, output_file):
    with open(output_file, 'w') as f:
        cport = get_free_control_port()
        args = shlex.split(command)
        args.extend(["-cp", str(cport)])
        process = subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT)
    return process


def run_uac(uac_config):
    uacXml = uac_config.select_uac
    uacSrcPort = int(uac_config.src_port_uac)
    protocol_uac = uac_config.protocol_uac
    noOfCalls = int(uac_config.total_no_of_calls)
    cps = int(uac_config.cps)
    dialed_number = uac_config.called_party_number
    calling_number = uac_config.calling_party_number
    stun_server = uac_config.stun_server
    uacXmlPath = str(settings.BASE_DIR / 'easySIPp' / 'xml' / uacXml)
    uac_remote = f"{uac_config.uac_remote}:{uac_config.uac_remote_port}"
    uacSrc = f"-i {uac_config.uac_local_addr} -p {uacSrcPort}"

    try:
        if any(stun_server):
            stunnedPath = stun4nat(uacXml, uacSrcPort, stun_server)
            if stunnedPath is not None:
                uacXmlPath = stunnedPath
            else: return HttpResponse(f'Stun server at {stun_server} is not responding!')

        if dialed_number or calling_number:
            uacXmlPath = modifynumberxmlpath(uacXmlPath, calling_number, dialed_number)

        uacCommand = f"{sipp} -sf {uacXmlPath} {uac_remote} {uacSrc} -m {noOfCalls} -r {cps} -t {protocol_uac}"
        outputFile = f'{uacXml}.log'
        uacProc = run_sipp_in_background(uacCommand, outputFile)
        time.sleep(0.4)
        # Check if Process has immediately exited
        return_code = uacProc.poll()

        if return_code != 0 and return_code != None:
            outputFilePath = os.path.join(settings.BASE_DIR, outputFile)
            with open(outputFilePath, 'r') as file:
                lines = file.readlines()
                last_lines = lines[-8:]
                sipp_error = ''.join(last_lines)
                logger.error(sipp_error)
                return sipp_error

    except Exception as e:
        sipp_error = f"Error: {e}"
        logger.exception('Exception occurred while trying to run sipp')


def run_uas(uas_config):
    uasXml = uas_config.select_uas
    uasSrcPort = int(uas_config.src_port_uas)
    protocol_uas = uas_config.protocol_uas
    uasXmlPath = str(settings.BASE_DIR / 'easySIPp' / 'xml' / uasXml)
    uas_remote = f"{uas_config.uas_remote}:{uas_config.uas_remote_port}"
    uasSrc = f"-i {uas_config.uas_local_addr} -p {uasSrcPort}"

    try:
        # if any(stun_server):                    
        #     stunnedPath = stun4nat(uasXml, uasSrcPort, stun_server)
        #     if stunnedPath is not None:
        #         uasXmlPath = stunnedPath

        #     else: return HttpResponse(f'Stun server at {stun_server} is not responding!')

        uasCommand = f"{sipp} -sf {uasXmlPath} {uas_remote} {uasSrc} -t {protocol_uas}"
        outputFile = f'{uasXml}.log'
        uasProc=run_sipp_in_background(uasCommand, outputFile)
        time.sleep(0.4)
        # Check if Process has immediately exited
        return_code = uasProc.poll()
        if return_code != 0 and return_code != None:
            outputFilePath = os.path.join(settings.BASE_DIR, outputFile)
            with open(outputFilePath, 'r') as file:
                lines = file.readlines()
                # Extract the last 'num_lines' lines from the list
                last_lines = lines[-14:]
                sipp_error = ''.join(last_lines)
                return sipp_error
            
    except Exception as e:
        sipp_error = f"Error: {e}"
        logger.exception('Exception occurred while trying to run sipp')


############ function to get running Sipp Process ######################################
def get_sipp_processes():
    sipp_processes = []
    sipp_pattern = r"sipp"  # Regular expression to match "sipp" in the command-line
    shell_name = r"(bash|sh)"  # Regular expression to match shell names

    mcalls = False

    for process in psutil.process_iter(['pid', 'cmdline']):
        if process.info['cmdline']:
            cmdline = ' '.join(process.info['cmdline'])
            cmdraw = process.info['cmdline']
            if re.search(sipp_pattern, cmdline) and not re.search(shell_name, cmdline):
                arguments = ' '.join(os.path.basename(arg) if os.path.isabs(arg) else arg for arg in process.info['cmdline'][1:])
                # Look for -sf and -cp arguments
                for i, arg in enumerate(cmdraw):
                    if arg == "-sf" and i + 1 < len(cmdraw):
                        script_name = os.path.basename(cmdraw[i + 1])
                    if arg == "-cp" and i + 1 < len(cmdraw):
                        control_port = cmdraw[i + 1]
                    if arg == "-m" and i + 1 < len(cmdraw):
                        mcalls = int(cmdraw[i + 1])

                sipp_processes.append({
                    'pid': process.info['pid'],
                    'command_line': f"./sipp {arguments}",
                    'script_name' : script_name,
                    'cport' : control_port,
                    'mcalls' : mcalls,
                })

    sorted_sipp_processes = sorted(sipp_processes, key=lambda x: x['pid'], reverse=True)
    return sorted_sipp_processes

def cleanFilename(filename):
    # Replace spaces with underscores
    cleaned_filename = filename.replace(' ', '_')
    # Remove any characters that are not alphanumeric, underscores, hyphens, or periods
    cleaned_filename = re.sub(r'[^\w\-\.]', '', cleaned_filename)
    return cleaned_filename


