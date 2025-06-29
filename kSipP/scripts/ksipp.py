import psutil, os, re
from django.conf import settings

############# Get Sipp Commands ######################################
def sipp_commands(config_data):    
    uacXml = f'{config_data["select_uac"]}'
    uasXml = f'{config_data["select_uas"]}'
    uacSrcPort = int(f"{config_data['src_port_uac']}")
    protocol_uac = f'{config_data["protocol_uac"]}'
    uasSrcPort = int(f"{config_data['src_port_uas']}")
    protocol_uas = f'{config_data["protocol_uas"]}'
    noOfCalls = int(f"{config_data['total_no_of_calls']}")
    cps = int(f"{config_data['cps']}")

    uac_remote=f"{config_data['uac_remote']}:{config_data['uac_remote_port']}"
    uas_remote=f"{config_data['uas_remote']}:{config_data['uas_remote_port']}"
    uacSrc=f"-i {config_data['local_addr']} -p {uacSrcPort}"
    uasSrc=f"-i {config_data['local_addr']} -p {uasSrcPort}"

    # below vars used on index.html
    print_uac_command = f"sipp -sf {uacXml} {uac_remote} {uacSrc} -m {noOfCalls}"
    if cps > 1: print_uac_command += f" -r {cps}"
    if protocol_uac == 'tn' : print_uac_command += f" -t {protocol_uac}"

    print_uas_command = f"sipp -sf {uasXml} {uas_remote} {uasSrc}"
    if protocol_uas == 'tn': print_uas_command += f" -t {protocol_uas}"

    return print_uac_command, print_uas_command
#########################################################################################
############# function to get running Sipp Process ######################################
def get_sipp_processes():
    sipp_processes = []
    sipp_pattern = r"sipp"  # Regular expression to match "sipp" in the command-line
    shell_name = r"(bash|sh)"  # Regular expression to match shell names

    for process in psutil.process_iter(['pid', 'cmdline']):
        if process.info['cmdline']:
            cmdline = ' '.join(process.info['cmdline'])
            if re.search(sipp_pattern, cmdline) and not re.search(shell_name, cmdline):
                sipp = os.path.basename(process.info['cmdline'][0])
                arguments = ' '.join(os.path.basename(arg) if os.path.isabs(arg) else arg for arg in process.info['cmdline'][1:])
                uac_uas_arg =''.join(os.path.basename(process.info['cmdline'][2]))

                sipp_processes.append({
                    'pid': process.info['pid'],
                    'command_line': f"{sipp} {arguments}",
                    'script_name' : f"{uac_uas_arg}"
                })
    sorted_sipp_processes = sorted(sipp_processes, key=lambda x: x['pid'], reverse=True)
    return sorted_sipp_processes
#########################################################################################

def cleanFilename(filename):
    # Replace spaces with underscores
    cleaned_filename = filename.replace(' ', '_')
    # Remove any characters that are not alphanumeric, underscores, hyphens, or periods
    cleaned_filename = re.sub(r'[^\w\-\.]', '', cleaned_filename)
    return cleaned_filename
