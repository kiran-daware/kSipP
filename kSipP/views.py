from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.sessions.models import Session
from .forms import configForm, xmlForm, modifyHeaderForm, moreSippOptionsForm, modifySelectedHeaderForSipMsgs
import configparser
import os
import subprocess
import psutil
import signal
import re
import time

from .scripts.showXmlFlow import showXmlFlowScript
from .scripts.modifyHeader import modifyHeaderScript, getHeadersFromSipMsgs

# Read initial data from config file
config_file = os.path.join(str(settings.BASE_DIR), 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)
configd = config['DEFAULT']

#global variables
def fetch_config_data():
    # Read initial data from config file
    config_data = {
        'remote_addr': configd.get('remote_addr'),
        'remote_port': configd.get('remote_port'),
        'local_addr': configd.get('local_addr'),
        'src_port_uac': configd.get('src_port_uac'),
        'src_port_uas': configd.get('src_port_uas'),
        'called_party_number': configd.get('called_party_number'),
        'calling_party_number': configd.get('calling_party_number'),
        'total_no_of_calls': configd.get('total_no_of_calls'),
        'cps': configd.get('cps'),
        'select_uac':configd.get('select_uac'),
        'select_uas':configd.get('select_uas'),
        'is_behind_nat':configd.get('is_behind_nat')
    }
    return config_data



################### Index Page Functions #############################

@never_cache
def index(request):

    config_data = fetch_config_data()
    
    remote=f"{config_data['remote_addr']}:{config_data['remote_port']}"
    uacSrc=f"-i {config_data['local_addr']} -p {config_data['src_port_uac']}"
    uasSrc=f"-i {config_data['local_addr']} -p {config_data['src_port_uas']}"

    # below vars used on index.html
    print_uac_command = f"sipp -sf {config_data['select_uac']} {remote} {uacSrc} -m 1"
    print_uas_command = f"sipp -sf {config_data['select_uas']} {remote} {uasSrc}"

    # loading xmlForm and configForm
    selectXml = xmlForm(initial=config_data)
    ipConfig = configForm(initial=config_data)
    moreOptionsForm = moreSippOptionsForm(initial=config_data)

    # Check XML file call Flow 
    if request.method =="POST":
        if 'submitType' in request.POST:
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
            
            if submit_type == 'moreOptions':
                # Load moreSippOptionsForm
                showMoreOptionsForm = True


    if request.method == 'POST':
        if 'submitType' in request.POST:
            # submit_type = request.POST['submitType']
            # if submit_type =='config' or submit_type == 'moreOptionsClose' or submit_type == 'moreOptions':
            selectXml = xmlForm(request.POST)
            ipConfig = configForm(request.POST)
            moreOptionsForm = moreSippOptionsForm(request.POST)
            if selectXml.is_valid() & ipConfig.is_valid() & moreOptionsForm.is_valid():

                # update config_data dictionary
                config_data['select_uac'] = selectXml.cleaned_data['select_uac']
                config_data['select_uas'] = selectXml.cleaned_data['select_uas']
                
                config_data['remote_addr'] = ipConfig.cleaned_data['remote_addr']
                config_data['remote_port'] = ipConfig.cleaned_data['remote_port']
                config_data['local_addr'] = ipConfig.cleaned_data['local_addr']
                config_data['src_port_uac'] = ipConfig.cleaned_data['src_port_uac']
                config_data['src_port_uas'] = ipConfig.cleaned_data['src_port_uas']
                config_data['called_party_number'] = moreOptionsForm.cleaned_data['called_party_number']
                config_data['calling_party_number'] = moreOptionsForm.cleaned_data['calling_party_number']
                config_data['total_no_of_calls'] = moreOptionsForm.cleaned_data['total_no_of_calls']
                config_data['cps'] = moreOptionsForm.cleaned_data['cps']
                config_data['is_behind_nat'] = moreOptionsForm.cleaned_data['is_behind_nat']
                
                # config set for saving in config.ini
                for configKey, configValue in config_data.items():
                    config.set('DEFAULT', configKey, str(configValue))

                
                # Update the config file after config.set
                ConfigFile = os.path.join(settings.BASE_DIR, 'config.ini')
                with open(ConfigFile, 'w') as configfile:
                    config.write(configfile)
                


                #update script prints on homepage
                remote=f"{config_data['remote_addr']}:{config_data['remote_port']}"
                uacSrc=f"-i {config_data['local_addr']} -p {config_data['src_port_uac']}"
                uasSrc=f"-i {config_data['local_addr']} -p {config_data['src_port_uas']}"

                # below vars used on index.html
                print_uac_command = f"sipp -sf {config_data['select_uac']} {remote} {uacSrc} -m 1"
                print_uas_command = f"sipp -sf {config_data['select_uas']} {remote} {uasSrc}"

                sipp_processes = get_sipp_processes()
                return render(request, 'index.html', locals())
    
    sipp_processes = get_sipp_processes()
    return render(request, 'index.html', locals())



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
                # newModXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', 'uas_kiran.xml')
                with open(modXmlPath, 'r') as file:
                    xml_content = file.read()
                
                return render(request, 'xml_editor.html', {'xml_content':xml_content, 'modifyXml':modifyXml})

                    
        if request.method == 'POST' and 'modifiedHeaderDone' in request.POST:
            modifiedHeaderDone = request.POST['modifiedHeaderDone']
            newXmlFileName = None
            if modifiedHeaderDone == 'modifiedHeaderDoneNewFile':
                newXmlFileName = request.POST['newXmlFileName']

            modifyXml_noext = modifyXml.rsplit(".", 1)[0]
            headersBySipMessage = request.session['headersBySipMessage']
            selectedHeader = request.session['selectedHeader']
            modifySelectedHeaderForSipMsgsForm = modifySelectedHeaderForSipMsgs(request.POST, hbsm=headersBySipMessage)
            if modifySelectedHeaderForSipMsgsForm.is_valid():
                modified_headers = {}

                if newXmlFileName is not None:
                    # delete if already a file exists with xml_name_modified.xml to avoid conflicts after editing
                    modXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', f'{modifyXml_noext}_{newXmlFileName}.xml')                    
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
                        request.session['modifyXml'] = f'{modifyXml_noext}_{newXmlFileName}.xml'

                    else:
                        modifyHeaderScript(modifyXml, sipMessage, selectedHeader, header_value)


                    
            # if modifyXmlSubmit == 'doneModify':
            #     request.session['modifyXml'] = None

            # if modifyXmlSubmit == 'xmlEditor':

            #     modXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', modifyXml)
            #     newModXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', 'uas_kiran.xml')

            #     with open(modXmlPath, 'r') as file:
            #         xml_content = file.read()
                
            #     return render(request, 'xml_editor.html', {'xml_content':xml_content})


    
    return render(request, 'modify_xml.html', locals())



def aceXmlEditor(request):
    if request.method == 'POST':
        xml_content = request.POST.get('xml_content')
        # Replace double line breaks with single line breaks
        xml_content = xml_content.replace('\r\n', '\n')
        with open(os.path.join(settings.BASE_DIR, 'kSipP', 'xml', 'uas_kiran.xml'), 'w', encoding='utf-8') as file:
            file.write(xml_content)

    return render(request, 'xml_editor.html', {'xml_content':xml_content})

    # return HttpResponse('XML content saved successfully.')


                        # if submit_type == 'save':
                        #     xml_content = request.POST.get('xml_content')

                        #     with open(newmodxml, 'w', encoding='utf-8') as file:
                        #         file.write(xml_content)
                        
                        # else:
                        #     with open(modxml, 'r') as file:
                        #         xml_content = file.read()
                        

            # return render(request, 'xml_editor.html', {'xml_content':xml_content})



        # printSelectedXml = f"Select Header to modify in {modifyXml}"
        # modifyHeaderForm = modifyHeader(request.POST)

        # # Handle form submissions here
        # if selectXml == 'newHeader':
        #     if modifyHeaderForm.is_valid():
        #         selectedHeader = modifyHeaderForm.cleaned_data['selectHeader']
        #         newHeader = modifyHeaderForm.cleaned_data['modifyHeader']
        # elif selectXml == 'doneModify':
        #     pass  # Handle the doneModify action if needed




                # printSelectedXml = f"Select Header to modify in {modifyXml}"
                # modifyHeaderForm = modifyHeader(request.POST)
                # submit_type == request.POST['submitType']
                # if submit_type == 'newHeader':
                #     if modifyHeaderForm.is_valid():
                #         selectedHeader = modifyHeaderForm.cleaned_data['selectHeader']
                #         newHeader = modifyHeaderForm.cleaned_data['modifyHeader']


                        # if submit_type == 'save':
                        #     xml_content = request.POST.get('xml_content')

                        #     with open(newmodxml, 'w', encoding='utf-8') as file:
                        #         file.write(xml_content)
                        
                        # else:
                        #     with open(modxml, 'r') as file:
                        #         xml_content = file.read()
                        

                        # return render(request, 'xml_editor.html', {'xml_content':xml_content})


                
            

                    
                    
                    
                    



#                 xmlContent = f'''[DEFAULT]\n
# UAC = {selectUAC}
# UAS = {selectUAS}
# '''
#                 xmlConfigFile = os.path.join(settings.BASE_DIR, 'xml.ini')
#                 with open(xmlConfigFile, 'w') as file:
#                     file.write(xmlContent)
#                 return render(request, 'modify_xml.html', {'form': modifyXmlForm})
            
        # if 'xmlName' in request.POST:
        #     xmlName = request.POST.get('xmlName')
        #     if xmlName.is_valid():
                

        #         modifyXml_script = str(settings.BASE_DIR / 'kSipP' / 'scripts' / 'modifyHeader.py')
        #     try:
        #         result = subprocess.run(['python', modifyXml_script], capture_output=True, text=True)
        #         return HttpResponse(result)
        #     except subprocess.CalledProcessError as e:
        #         # Handle any errors that may occur when running the script
        #         return HttpResponse(f"Error occurred: {e}")


    # modifyXmlForm = xmlForm()
    # return render(request, 'modify_xml.html', locals())





############# function to get running Sipp Process

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




########################## Run SipP Scripts ##########################

def run_script_view(request):

    config_data = fetch_config_data()

    sipp = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'sipp')
    uacXml = str(settings.BASE_DIR / 'kSipP' / 'xml' / f'{config_data["select_uac"]}')
    uasXml = str(settings.BASE_DIR / 'kSipP' / 'xml' / f'{config_data["select_uas"]}')
    remote=f"{config_data['remote_addr']}:{config_data['remote_port']}"
    uacSrc=f"-i {config_data['local_addr']} -p {config_data['src_port_uac']}"
    uasSrc=f"-i {config_data['local_addr']} -p {config_data['src_port_uas']}"

    print_uac_command = f"sipp -sf {config_data['select_uac']} {remote} {uacSrc} -m 1"
    print_uas_command = f"sipp -sf {config_data['select_uas']} {remote} {uasSrc}"

    if request.method == 'POST':

        def run_sipp_in_background(command, output_file):
            with open(output_file, 'w') as f:
                process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT,shell=True, text=True)
            return process

        scriptName = request.POST.get('script')
        if scriptName == 'UAC':
            try:
                uacCommand = f"{sipp} -sf {uacXml} {remote} {uacSrc} -m 1"
                outputFile = f'{config_data["select_uac"]}.log'
                uacProc = run_sipp_in_background(uacCommand, outputFile)
                # uacProc=subprocess.Popen(uacCommand,shell=True)
                time.sleep(0.2)
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
                return HttpResponse(f"Error: {e}")
            
        if scriptName =='UAS':
            try:
                uasCommand = f"{sipp} -sf {uasXml} {remote} {uasSrc} -t t1"
                outputFile = f'{config_data["select_uas"]}.log'
                uasProc=run_sipp_in_background(uasCommand, outputFile)
                time.sleep(0.2)
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
                return HttpResponse(f"Error: {e}")

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



def sbc_api(request):
    return render(request, 'sbc_api.html')

