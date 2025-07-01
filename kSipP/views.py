from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import configForm, xmlForm, moreSippOptionsForm
from .forms import xmlUploadForm
from .models import AppConfig
from django.http import HttpResponseBadRequest
from django.urls import reverse
import xml.etree.ElementTree as ET
import os, time, signal
import subprocess, psutil
from .scripts.ksipp import get_sipp_processes, sipp_commands, cleanFilename
from .scripts.kstun import get_ip_info
from .scripts.modify import tmpXmlBehindNAT, modifynumberxmlpath
from .scripts.list import listXmlFiles
import logging
import shlex, socket

logger = logging.getLogger(__name__)


################### Index Page Functions #############################

@never_cache
def index(request):
    # Always fetch or create the single config instance
    config_obj, _ = AppConfig.objects.get_or_create(key='main')
    def update_config_data(): 
        config_data = {
            'select_uac': config_obj.select_uac,
            'select_uas': config_obj.select_uas,
            'uac_remote': config_obj.uac_remote,
            'uac_remote_port': config_obj.uac_remote_port,
            'uas_remote': config_obj.uas_remote,
            'uas_remote_port': config_obj.uas_remote_port,
            'local_addr': config_obj.local_addr,
            'src_port_uac': config_obj.src_port_uac,
            'src_port_uas': config_obj.src_port_uas,
            'protocol_uac': config_obj.protocol_uac,
            'protocol_uas': config_obj.protocol_uas,
            'called_party_number': config_obj.called_party_number,
            'calling_party_number': config_obj.calling_party_number,
            'total_no_of_calls': config_obj.total_no_of_calls,
            'cps': config_obj.cps,
            'stun_server': config_obj.stun_server,
        }
        return config_data

    # GET request: pre-fill forms with database values
    selectXml = xmlForm(instance=config_obj)
    ipConfig = configForm(instance=config_obj)
    moreOptionsForm = moreSippOptionsForm(instance=config_obj)

    config_data = update_config_data()
    print_uac_command, print_uas_command=sipp_commands(config_data)

    if request.method == 'POST' and 'submitType' in request.POST:
        # submit_type = request.POST['submitType']
        # if submit_type =='config' or submit_type == 'moreOptionsClose' or submit_type == 'moreOptions':
        selectXml = xmlForm(request.POST, instance=config_obj)
        ipConfig = configForm(request.POST, instance=config_obj)
        moreOptionsForm = moreSippOptionsForm(request.POST, instance=config_obj)

        if selectXml.is_valid() and ipConfig.is_valid() and moreOptionsForm.is_valid():
            # Save all parts to the same instance
            if selectXml.is_valid() and ipConfig.is_valid() and moreOptionsForm.is_valid():
                cd = {
                    **selectXml.cleaned_data,
                    **ipConfig.cleaned_data,
                    **moreOptionsForm.cleaned_data
                }
                # Update the config object
                for key, value in cd.items():
                    setattr(config_obj, key, value)
                config_obj.save()

            # Reload updated instance from DB
            config_obj.refresh_from_db()
            config_data=update_config_data()
            # Update script prints on homepage
            print_uac_command, print_uas_command=sipp_commands(config_data)
        
        elif not moreOptionsForm.is_valid():
            showMoreOptionsForm = True

    if request.method == 'POST' and 'runScript' in request.POST:
        uacXml = f'{config_data["select_uac"]}'
        uasXml = f'{config_data["select_uas"]}'
        uacSrcPort = int(f"{config_data['src_port_uac']}")
        protocol_uac = f'{config_data["protocol_uac"]}'
        uasSrcPort = int(f"{config_data['src_port_uas']}")
        protocol_uas = f'{config_data["protocol_uas"]}'
        noOfCalls = int(f"{config_data['total_no_of_calls']}")
        cps = int(f"{config_data['cps']}")

        dialed_number = f'{config_data["called_party_number"]}'
        calling_number = f'{config_data["calling_party_number"]}'
        stun_server = {config_data['stun_server']}

        sipp = str(settings.BASE_DIR / 'kSipP' / 'sipp')
        uacXmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / uacXml)
        uasXmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / uasXml)
        uac_remote=f"{config_data['uac_remote']}:{config_data['uac_remote_port']}"
        uas_remote=f"{config_data['uas_remote']}:{config_data['uas_remote_port']}"
        uacSrc=f"-i {config_data['local_addr']} -p {uacSrcPort}"
        uasSrc=f"-i {config_data['local_addr']} -p {uasSrcPort}"

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
        
        scriptName = request.POST.get('runScript')
        if scriptName == 'UAC':
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
                        last_lines = lines[-2:]
                        sipp_error = ''.join(last_lines)
                        logger.error(sipp_error)

            except Exception as e:
                sipp_error = f"Error: {e}"
                logger.exception('Exception occurred while trying to run sipp')
            
        if scriptName =='UAS':
            try:
                if any(stun_server):                    
                    stunnedPath = stun4nat(uasXml, uasSrcPort, stun_server)
                    if stunnedPath is not None:
                        uasXmlPath = stunnedPath

                    else: return HttpResponse(f'Stun server at {stun_server} is not responding!')

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
                        
            except Exception as e:
                sipp_error = f"Error: {e}"
                logger.exception('Exception occurred while trying to run sipp')


    if request.method == 'POST' and 'send_signal' in request.POST:
        send_signal = request.POST.get('send_signal')
        # Handle the POST request for killing the process here
        pid = request.POST.get('pid_to_kill')

        if send_signal == 'Kill':
            try:
                process = psutil.Process(int(pid))
                process.terminate()  # You can also use process.kill() for a more forceful termination
                process.wait(timeout=2)  # Wait for it to exit
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass  # The process with the given PID doesn't exist or already terminated
        
        elif send_signal == 'CheckOutput':
            try:
                script_name = request.POST.get('script_name')
                xml_wo_ext = script_name.rsplit(".", 1)[0]

                cport = request.POST.get('cport')
                mcalls = request.POST.get('mcalls')
                process = psutil.Process(int(pid))
                os.kill(process.pid, signal.SIGUSR2)
                # return redirect('display_sipp_screen', xml=xml_wo_ext, pid=pid, cport=cport)
                return redirect(f'{reverse("display_sipp_screen", kwargs={"xml": xml_wo_ext, "pid": process.pid})}?cp={cport}&m={mcalls}')

            

            except (psutil.NoSuchProcess, ProcessLookupError):
                return redirect('display_sipp_screen', xml=xml_wo_ext, pid=pid)

    
    sipp_processes = get_sipp_processes()
    context = {
        'config_data': config_data,
        'print_uac_command': print_uac_command,
        'print_uas_command': print_uas_command,
        'selectXml': selectXml,
        'ipConfig': ipConfig,
        'moreOptionsForm': moreOptionsForm,
        'sipp_processes': sipp_processes,
        'showMoreOptionsForm': showMoreOptionsForm if 'showMoreOptionsForm' in locals() else False,
        'sipp_error':sipp_error if 'sipp_error' in locals() else False
        }

    return render(request, 'index.html', context)


######## Index End ############

def serveXmlFile(request, xmlname):
    xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / xmlname)
    with open(xmlPath, 'r') as file:
        xmlContent = file.read()
    return HttpResponse(xmlContent, content_type='text/plain')



def xmlEditor(request):
    if request.method == 'GET':
        xmlName=request.GET.get('xml')
        referer=request.GET.get('back', 'index')
        if xmlName is None:
            return HttpResponse('No xml selected <a href="/xml-management/">Select here!</a>')
        xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / xmlName)
        with open(xmlPath, 'r') as file:
            xmlContent = file.read()

    if request.method == 'POST':
        xmlContent = request.POST.get('xml_content')
        xmlName = request.POST.get('xml_name')
        new_xml_name = request.POST.get('new_xml_name')
        save_type = request.POST.get('save')
        referer = request.POST.get('exit')
        # Replace double line breaks with single line breaks
        xmlContent = xmlContent.replace('\r\n', '\n')

        if save_type == 'save': savingXmlName = xmlName
        elif save_type == 'save_as': 
            uacuas = 'uac' if xmlName.startswith('uac') else ('uas' if xmlName.startswith('uas') else None)
            savingXmlName = f'{uacuas}_{new_xml_name}.xml'
            savingXmlName = cleanFilename(savingXmlName)
        else:  return redirect(referer)

        with open(os.path.join(settings.BASE_DIR, 'kSipP', 'xml', savingXmlName), 'w', encoding='utf-8') as file:
            file.write(xmlContent)

        xmlName = savingXmlName

    
    context = {
        'xml_content':xmlContent,
        'xml_name':xmlName,
        'save': save_type if 'save_type' in locals() else False,
        'referer': referer if 'referer' in locals() else False,
    }
    return render(request, 'xml_editor.html', context)


def sipp_screen(request, pid, xml):
    cport = request.GET.get('cp')
    mcalls = request.GET.get('m')
    context = {
        'xml':xml,
        'pid':pid,
        'cport':cport,
        'mcalls': mcalls,
        }
    return render(request, 'sipp_screen.html', context)

    


def create_scenario_xml_view(request):
    if request.method == 'POST':
        xmlContent=request.POST.get('xml_content')
        fileName=request.POST.get('file_name')
        cleanedFilename = cleanFilename(fileName)
        with open(os.path.join(settings.BASE_DIR, 'kSipP', 'xml', cleanedFilename), 'w', encoding='utf-8') as file:
            file.write(xmlContent)
    
    context = {
        'xml_content':xmlContent if 'xmlContent' in locals() else False,
        'xml_name':fileName if 'fileName' in locals() else False,
    }

    return render(request, 'create_scenario_xml.html', context)


def xml_mgmt_view(request):
    xmlDir = os.path.join(settings.BASE_DIR, 'kSipP', 'xml')
    xmlUploadF = xmlUploadForm()

    if request.method == 'POST' and 'submitType' in request.POST:
        submitType = request.POST.get('submitType')
        if submitType == 'upload':
            xmlUploadF = xmlUploadForm(request.POST, request.FILES)
            if xmlUploadF.is_valid():
                uploaded_file = request.FILES['file']
                cleaned_filename = cleanFilename(uploaded_file.name)
                file_path = os.path.join(xmlDir, cleaned_filename)
                
                # Validate the uploaded XML file
                try:
                    with open(file_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    tree = ET.parse(file_path)
                    uploadMsg = f"File '{cleaned_filename}' uploaded successfully."
                    
                except ET.ParseError as e:
                    os.remove(file_path)  # Remove the invalid file
                    uploadMsg = f"Invalid XML file '{uploaded_file.name}': {e}"


    if request.method =='GET' and 'delete' in request.GET:
        deleteXmlName=request.GET.get('delete')
        deleteXmlPath = os.path.join(xmlDir, deleteXmlName)
        if os.path.exists(deleteXmlPath):
            os.remove(deleteXmlPath)
        
    uacList, uasList = listXmlFiles(xmlDir)
    context = {
        'uac_list':uacList, 'uas_list':uasList,
        'xml_upload_form': xmlUploadF,
        'upload_msg': uploadMsg if 'uploadMsg' in locals() else False,
        }
    
    return render(request, 'xml_management.html', context)
