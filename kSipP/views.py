from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.sessions.models import Session
from .forms import configForm, xmlForm, modifyHeaderForm, moreSippOptionsForm, modifySelectedHeaderForSipMsgs
from .forms import xmlUploadForm
from django.http import HttpResponseBadRequest
import xml.etree.ElementTree as ET
import os, time, signal, re
import subprocess, psutil
from .scripts.ksipp import get_sipp_processes, fetch_config_data, save_config_data, sipp_commands
from .scripts.kstun import get_ip_info
from .scripts.showXmlFlow import showXmlFlowScript
from .scripts.modify import modifyHeaderScript, getHeadersFromSipMsgs, tmpXmlBehindNAT, modifynumberxmlpath


################### Index Page Functions #############################

@never_cache
def index(request):
    config_data = fetch_config_data()    
    print_uac_command, print_uas_command=sipp_commands(config_data)

    # loading xmlForm and configForm
    selectXml = xmlForm(initial=config_data)
    ipConfig = configForm(initial=config_data)
    moreOptionsForm = moreSippOptionsForm(initial=config_data)

    # Check XML file call Flow 
    if request.method =="POST" and 'submitType' in request.POST:
        submit_type = request.POST['submitType']
        if submit_type == 'checkFlow':
            selectXml = xmlForm(request.POST)
            if selectXml.is_valid():
                selectUAC = selectXml.cleaned_data['select_uac']
                selectUAS = selectXml.cleaned_data['select_uas']
                # xml_file_path = str(settings.BASE_DIR / 'kSipP' / 'xml' / 'uac.xml')

                uacflow = showXmlFlowScript(selectUAC)
                uasflow = showXmlFlowScript(selectUAS)
                return render(request, 'show_xml_flow.html', locals())
            

    if request.method == 'POST' and 'submitType' in request.POST:
        # submit_type = request.POST['submitType']
        # if submit_type =='config' or submit_type == 'moreOptionsClose' or submit_type == 'moreOptions':
        selectXml = xmlForm(request.POST)
        ipConfig = configForm(request.POST)
        moreOptionsForm = moreSippOptionsForm(request.POST)
        if selectXml.is_valid() and ipConfig.is_valid() and moreOptionsForm.is_valid():

            # update config_data dictionary
            config_data['select_uac'] = selectXml.cleaned_data['select_uac']
            config_data['select_uas'] = selectXml.cleaned_data['select_uas']
            
            config_data['uac_remote'] = ipConfig.cleaned_data['uac_remote']
            config_data['uac_remote_port'] = ipConfig.cleaned_data['uac_remote_port']
            config_data['uas_remote'] = ipConfig.cleaned_data['uas_remote']
            config_data['uas_remote_port'] = ipConfig.cleaned_data['uas_remote_port']
            config_data['local_addr'] = ipConfig.cleaned_data['local_addr']
            config_data['src_port_uac'] = ipConfig.cleaned_data['src_port_uac']
            config_data['src_port_uas'] = ipConfig.cleaned_data['src_port_uas']
            config_data['protocol_uac'] = ipConfig.cleaned_data['protocol_uac']
            config_data['protocol_uas'] = ipConfig.cleaned_data['protocol_uas']

            config_data['called_party_number'] = moreOptionsForm.cleaned_data['called_party_number']
            config_data['calling_party_number'] = moreOptionsForm.cleaned_data['calling_party_number']
            config_data['total_no_of_calls'] = moreOptionsForm.cleaned_data['total_no_of_calls']
            config_data['cps'] = moreOptionsForm.cleaned_data['cps']
            config_data['stun_server'] = moreOptionsForm.cleaned_data['stun_server']
            
            save_config_data(config_data)

            #update script prints on homepage
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

        sipp = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'sipp')
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
        
        def run_sipp_in_background(command, output_file):
            with open(output_file, 'w') as f:
                process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT,shell=True, text=True)
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
                # uacProc=subprocess.Popen(uacCommand,shell=True)
                time.sleep(0.4)
                # Check if Process has immediately exited
                return_code = uacProc.poll()
                if return_code != 0 and return_code != None:
                    outputFilePath = os.path.join(settings.BASE_DIR, outputFile)
                    with open(outputFilePath, 'r') as file:
                        lines = file.readlines()
                        # Extract the last 'num_lines' lines from the list
                        last_lines = lines[-15:]
                        sipp_error = '*****'.join(last_lines)

            except Exception as e:
                sipp_error = f"Error: {e}"
                # return HttpResponse(f"Error: {e}")
            
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
                        last_lines = lines[-15:]
                        sipp_error = '*****'.join(last_lines)
                        
            except Exception as e:
                sipp_error = f"Error: {e}"
                # return HttpResponse(f"Error: {e}")

    if request.method == 'POST' and 'send_signal' in request.POST:
        send_signal = request.POST.get('send_signal')
        # Handle the POST request for killing the process here
        pid_to_kill = request.POST.get('pid_to_kill')
        script_name = request.POST.get('script_name')

        xml_wo_ext = script_name.rsplit(".", 1)[0]

        if send_signal == 'Kill':
            try:
                process = psutil.Process(int(pid_to_kill))
                process.terminate()  # You can also use process.kill() for a more forceful termination
            except psutil.NoSuchProcess:
                pass  # The process with the given PID doesn't exist or already terminated
        
        elif send_signal == 'CheckOutput':
            try:
                process = psutil.Process(int(pid_to_kill))
                os.kill(process.pid, signal.SIGUSR2)
                return redirect('display_sipp_screen', xml=xml_wo_ext, pid=process.pid)

            except (psutil.NoSuchProcess, ProcessLookupError):
                return redirect('display_sipp_screen', xml=xml_wo_ext, pid=pid_to_kill)

    
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
######################## Modify XML funtion calls ###############################################

def modifyXml(request):
    config_data = fetch_config_data()
    modifyXmlForm = xmlForm(initial=config_data)

    if 'modifyXml' not in request.session:
        request.session['modifyXml'] = None
    modifyXml = request.session['modifyXml']

    if request.method == 'POST' and 'selectXml' in request.POST:
        selectXml = request.POST['selectXml']
        modifyXmlForm = xmlForm(request.POST)
        if modifyXmlForm.is_valid():
            if selectXml == 'modifyUAC':
                modifyXml = modifyXmlForm.cleaned_data['select_uac']
            elif selectXml == 'modifyUAS':
                modifyXml = modifyXmlForm.cleaned_data['select_uas']

        request.session['modifyXml'] = modifyXml #store var in session            
        modifyHeaderFormData = modifyHeaderForm() #load modify header form after selecting xml file

    if modifyXml is not None:
        if request.method == 'POST' and 'modifyXmlSubmit' in request.POST:
            modifyXmlSubmit = request.POST['modifyXmlSubmit']
            if modifyXmlSubmit == 'headerToModify':
                modifyHeaderFormData = modifyHeaderForm(request.POST)
                if modifyHeaderFormData.is_valid():
                    selectedHeader = modifyHeaderFormData.cleaned_data['whichHeader']
                    headersBySipMessage = getHeadersFromSipMsgs(modifyXml, selectedHeader)
                    request.session['headersBySipMessage']=headersBySipMessage
                    request.session['selectedHeader']=selectedHeader
                    modifySelectedHeaderForSipMsgsForm = modifySelectedHeaderForSipMsgs(hbsm=headersBySipMessage)
                    modifyXml_noext = modifyXml.rsplit(".", 1)[0]
                    return render(request, 'modify_xml.html', locals())
                

            if modifyXmlSubmit == 'doneModify':
                request.session['modifyXml'] = None
                modifyXml = None
                return render(request, 'modify_xml.html', locals())

            if modifyXmlSubmit == 'xmlEditor':

                modXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', modifyXml)
                modifyXml_noext = modifyXml.rsplit(".", 1)[0]
                with open(modXmlPath, 'r') as file:
                    xml_content = file.read()
                
                return render(request, 'xml_editor.html', {'xml_content':xml_content, 'xml_name':modifyXml_noext})

                    
        if request.method == 'POST' and 'modifiedHeaderDone' in request.POST:
            modifiedHeaderDone = request.POST['modifiedHeaderDone']
            newXmlFileName = None
            if modifiedHeaderDone == 'modifiedHeaderDoneNewFile':
                newXmlFileName = request.POST['new_xml_name']

            # modifyXml_noext = modifyXml.rsplit(".", 1)[0]
            uacuas = 'uac' if modifyXml.startswith('uac') else ('uas' if modifyXml.startswith('uas') else None)
            headersBySipMessage = request.session['headersBySipMessage']
            selectedHeader = request.session['selectedHeader']
            modifySelectedHeaderForSipMsgsForm = modifySelectedHeaderForSipMsgs(request.POST, hbsm=headersBySipMessage)
            if modifySelectedHeaderForSipMsgsForm.is_valid():
                modified_headers = {}

                if newXmlFileName is not None:
                    # delete if already a file exists with xml_name_modified.xml to avoid conflicts after editing
                    modXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', f'{uacuas}_{newXmlFileName}.xml')                    
                    if os.path.exists(modXmlPath):
                        try:
                            os.remove(modXmlPath)
                        except:
                            pass

                for sipMessage, header_value in modifySelectedHeaderForSipMsgsForm.cleaned_data.items():
                    modified_headers[sipMessage] = header_value

                    if newXmlFileName is not None:
                        modifyHeaderScript(modifyXml, sipMessage, selectedHeader, header_value, newXmlFileName)
                        # update session with new modified xml file name (statically defined in modifyHeader.py)
                        request.session['modifyXml'] = f'{uacuas}_{newXmlFileName}.xml'
                        successM = f'{uacuas}_{newXmlFileName}.xml'

                    else:
                        modifyHeaderScript(modifyXml, sipMessage, selectedHeader, header_value)
                        successM = modifyXml

    return render(request, 'modify_xml.html', locals())



def aceXmlEditor(request):
    xml_content = None
    if request.method == 'POST':
        xml_content = request.POST.get('xml_content')
        xml_name = request.POST.get('xml_name')
        new_xml_name = request.POST.get('new_xml_name')
        save_type = request.POST.get('save')
        # Replace double line breaks with single line breaks
        xml_content = xml_content.replace('\r\n', '\n')

        if save_type == 'save': savingXmlName = xml_name
        elif save_type == 'save_as': 
            uacuas = 'uac' if xml_name.startswith('uac') else ('uas' if xml_name.startswith('uas') else None)
            savingXmlName = f'{uacuas}_{new_xml_name}'
        else: return redirect('modify-xml')
        
        with open(os.path.join(settings.BASE_DIR, 'kSipP', 'xml', f'{savingXmlName}.xml'), 'w', encoding='utf-8') as file:
            file.write(xml_content)
    
    if xml_content is None:
        return HttpResponse('No xml selected <a href="/modify-xml">Select here!</a>')

    return render(request, 'xml_editor.html', {'xml_content':xml_content, 'xml_name':savingXmlName, 'save':save_type})









########################## Run SipP Scripts ##########################

def run_script_view(request):

    config_data = fetch_config_data()

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

    sipp = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'sipp')
    uacXmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / uacXml)
    uasXmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / uasXml)
    uac_remote=f"{config_data['uac_remote']}:{config_data['uac_remote_port']}"
    uas_remote=f"{config_data['uas_remote']}:{config_data['uas_remote_port']}"
    uacSrc=f"-i {config_data['local_addr']} -p {uacSrcPort}"
    uasSrc=f"-i {config_data['local_addr']} -p {uasSrcPort}"

    print_uac_command = f"sipp -sf {uacXml} {uac_remote} {uacSrc} -m {noOfCalls}"
    if cps > 1: print_uac_command += f" -r {cps}"
    if protocol_uac == 'tn' : print_uac_command += f" -t {protocol_uac}"

    print_uas_command = f"sipp -sf {uasXml} {uas_remote} {uasSrc}"
    if protocol_uas == 'tn': print_uas_command += f" -t {protocol_uas}"



    
    ######## For behind NAT sipp
    def stun4nat(xmlName, srcPort, stunServer):
        stun_host_str = ''.join(stunServer)
        nat_type, external_ip, external_port = get_ip_info(stun_host=stun_host_str, source_port=int(srcPort))
        if external_ip is not None and external_port is not None:
            newXmlPath = tmpXmlBehindNAT(xmlName, external_ip, external_port)
        else:
            return None
        return newXmlPath
    

    if request.method == 'POST':

        def run_sipp_in_background(command, output_file):
            with open(output_file, 'w') as f:
                process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT,shell=True, text=True)
            return process

        scriptName = request.POST.get('script')
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
                # uacProc=subprocess.Popen(uacCommand,shell=True)
                time.sleep(0.3)
                # Check if Process has immediately exited
                return_code = uacProc.poll()
                if return_code != 0:
                    outputFilePath = os.path.join(settings.BASE_DIR, outputFile)
                    with open(outputFilePath, 'r') as file:
                        lines = file.readlines()
                        # Extract the last 'num_lines' lines from the list
                        last_lines = lines[-15:]
                        sipp_error = '*****'.join(last_lines)

            except Exception as e:
                sipp_error = f"Error: {e}"
                # return HttpResponse(f"Error: {e}")
            
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
                time.sleep(0.3)
                # Check if Process has immediately exited
                return_code = uasProc.poll()
                if return_code != 0:
                    outputFilePath = os.path.join(settings.BASE_DIR, outputFile)
                    with open(outputFilePath, 'r') as file:
                        lines = file.readlines()
                        # Extract the last 'num_lines' lines from the list
                        last_lines = lines[-15:]
                        sipp_error = '*****'.join(last_lines)
                        
            except Exception as e:
                sipp_error = f"Error: {e}"
                # return HttpResponse(f"Error: {e}")

    if request.method == 'POST' and 'send_signal' in request.POST:
        send_signal = request.POST.get('send_signal')
        # Handle the POST request for killing the process here
        pid_to_kill = request.POST.get('pid_to_kill')
        script_name = request.POST.get('script_name')

        xml_wo_ext = script_name.rsplit(".", 1)[0]

        if send_signal == 'Kill':
            try:
                process = psutil.Process(int(pid_to_kill))
                process.terminate()  # You can also use process.kill() for a more forceful termination
            except psutil.NoSuchProcess:
                pass  # The process with the given PID doesn't exist or already terminated
        
        elif send_signal == 'CheckOutput':
            try:
                process = psutil.Process(int(pid_to_kill))
                os.kill(process.pid, signal.SIGUSR2)
                return redirect('display_sipp_screen', xml=xml_wo_ext, pid=process.pid)

            except (psutil.NoSuchProcess, ProcessLookupError):
                return redirect('display_sipp_screen', xml=xml_wo_ext, pid=pid_to_kill)

    sipp_processes = get_sipp_processes()

    return render(request, 'run_script_template.html', locals())




################### Show Sipp Screen ###############

def read_sipp_screen(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def display_sipp_screen(request, xml, pid):
    sipp_processes = get_sipp_processes()
    log_name = f"{xml}_{pid}_screen.log"
    log1 = os.path.join(settings.BASE_DIR, log_name)
    log2 = os.path.join(settings.BASE_DIR, f'{xml}.xml.log')

    if psutil.pid_exists(pid) & os.path.isfile(log1):
        file_path=log1
    else:
        file_path=log2
        try:
            os.remove(log1)
        except:
            pass

    # file_path = log1 if os.path.isfile(log1) else log2

    lines = read_sipp_screen(file_path)
    content = ''.join(lines)
    context = {
        'content': content, 
        'sipp_processes':sipp_processes,
        'xml':xml,
        'pid':pid,
        'file_path':file_path,
        'log_name':log_name,
        }

    if request.method == 'POST' and 'send_signal' in request.POST:
        send_signal = request.POST.get('send_signal')
        # Handle the POST request for killing the process here
        pid_to_kill = request.POST.get('pid_to_kill')        
        if send_signal == 'Kill':
            try:
                process = psutil.Process(int(pid_to_kill))
                process.terminate()  # use process.kill() for a more forceful termination
            except psutil.NoSuchProcess:
                return HttpResponse("The SipP process with the given PID doesn't exist or already terminated")
        
        elif send_signal == 'CheckOutput':
            try:
                os.kill(pid, signal.SIGUSR2)
                time.sleep(0.2)

                lines = read_sipp_screen(file_path)
                content = ''.join(lines)
                context['content'] = content
                return render(request, 'sipp_log.html', context)
            except (psutil.NoSuchProcess, ProcessLookupError):
                file_path = os.path.join(settings.BASE_DIR, f'{xml}.xml.log')
                if file_path:
                    lines = read_sipp_screen(file_path)
                    content = ''.join(lines)
    

    return render(request, 'sipp_log.html', context)






def xml_management(request):
    xml_upload_form = xmlUploadForm()
    xml_dir = os.path.join(settings.BASE_DIR, 'kSipP', 'xml')
    xml_files = [file for file in os.listdir(xml_dir) if file.endswith(".xml")]
    xml_list = sorted(xml_files)

    if request.method == 'POST' and 'submitType' in request.POST:
        submitType = request.POST.get('submitType')
        if submitType == 'upload':
            upload_success = False
            xml_upload_form = xmlUploadForm(request.POST, request.FILES)
            if xml_upload_form.is_valid():
                uploaded_file = request.FILES['file']
                file_path = os.path.join(xml_dir, uploaded_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Validate the uploaded XML file
                try:
                    tree = ET.parse(file_path)
                except ET.ParseError as e:
                    os.remove(file_path)  # Remove the invalid file
                    return HttpResponseBadRequest(f"Invalid XML file :** {uploaded_file.name} **: {e} <br><br> <b><a href='/xml-management'>Return to upload</a></b>")

                upload_success = True
                xml_files = [file for file in os.listdir(xml_dir) if file.endswith(".xml")]
                xml_list = sorted(xml_files)
            return render(request, 'xml_management.html', {'xml_upload_form': xml_upload_form,
                                                           'xml_list': xml_list,
                                                           'upload_success': upload_success})
            
        if submitType == 'delete':
            xml_name = request.POST.get('xml_name')
            xml_path = os.path.join(xml_dir, xml_name)
            if os.path.exists(xml_path):
                os.remove(xml_path)

            xml_files = [file for file in os.listdir(xml_dir) if file.endswith(".xml")]
            xml_list = sorted(xml_files)


    return render(request, 'xml_management.html', {'xml_upload_form': xml_upload_form, 'xml_list': xml_list})


def create_scenario_xml_view(request):
    if request.method == 'POST':
        xmlContent=request.POST.get('xml_content')
        fileName=request.POST.get('file_name')
        with open(os.path.join(settings.BASE_DIR, 'kSipP', 'xml', fileName), 'w', encoding='utf-8') as file:
            file.write(xmlContent)

    return render(request, 'create_scenario_xml.html')


def xml_list_view(request):

    return render(request, 'xml_list.html')
