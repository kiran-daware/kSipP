from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.sessions.models import Session
from .forms import configForm, xmlForm, modifyHeaderForm, modifyHeaderFormNew, moreSippOptionsForm, modifySelectedHeaderForSipMsgs
import configparser
import os
import subprocess
# import psutil


from .scripts.showXmlFlow import showXmlFlowScript
from .scripts.modifyHeader import modifyHeaderScript, getHeadersFromSipMsgs

# Read initial data from config file
config_file = os.path.join(str(settings.BASE_DIR), 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)
configd = config['DEFAULT']
configx = config['XML']

#global variables
config_data = {}
xml_data = {}


################### Index Page Functions #############################

@never_cache
def index(request):

    global config_data
    config_data = {
        'remoteAddr': configd.get('remoteAddr'),
        'remotePort': configd.get('remotePort'),
        'localAddr': configd.get('localAddr'),
        'srcPortUac': configd.get('srcPortUac'),
        'srcPortUas': configd.get('srcPortUas'),
    }
    global xml_data
    xml_data = {
        'selectUAC':configx.get('selectUAC'),
        'selectUAS':configx.get('selectUAS')
    }
    

    remote=f"{config_data['remoteAddr']}:{config_data['remotePort']}"
    uacSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUac']}"
    uasSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUas']}"

    # below vars used on index.html
    print_uac_command = f"sipp -sf {xml_data['selectUAC']} {remote} {uacSrc} -m 1"
    print_uas_command = f"sipp -sf {xml_data['selectUAS']} {remote} {uasSrc}"

    # # fetching xml files from directory each time page refreshes.
    # xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml')
    # uac_files = [f for f in os.listdir(xmlPath) if f.startswith('uac')]
    # uas_files = [f for f in os.listdir(xmlPath) if f.startswith('uas')]

    # loading xmlForm and configForm
    selectXml = xmlForm(initial=xml_data)
    ipConfig = configForm(initial=config_data)

    # Check XML file call Flow 
    if request.method =="POST":
        if 'submitType' in request.POST:
            submit_type = request.POST['submitType']
            if submit_type == 'checkFlow':
                selectXml = xmlForm(request.POST)
                if selectXml.is_valid():
                    selectUAC = selectXml.cleaned_data['selectUAC']
                    selectUAS = selectXml.cleaned_data['selectUAS']
                    # xml_file_path = str(settings.BASE_DIR / 'kSipP' / 'xml' / 'uac.xml')

                    uacflow = showXmlFlowScript(selectUAC)
                    uasflow = showXmlFlowScript(selectUAS)
                    return render(request, 'show_xml_flow.html', locals())
            
            if submit_type == 'moreOptions':
                # Load moreSippOptionsForm
                showMoreOptionsForm = True
                moreOptionsForm = moreSippOptionsForm()


    if request.method == 'POST':
        if 'submitType' in request.POST:
            submit_type = request.POST['submitType']
            if submit_type =='config':
                selectXml = xmlForm(request.POST)
                ipConfig = configForm(request.POST)
                moreOptionsForm = moreSippOptionsForm(request.POST)
                if selectXml.is_valid() & ipConfig.is_valid() & moreOptionsForm.is_valid():

                    xml_data['selectUAC'] = selectXml.cleaned_data['selectUAC']
                    xml_data['selectUAS'] = selectXml.cleaned_data['selectUAS']
                    config.set('XML','selectUAC', str(xml_data['selectUAC']))
                    config.set('XML','selectUAS', str(xml_data['selectUAS']))
                    
                    # update config_data dictionary
                    config_data['remoteAddr'] = ipConfig.cleaned_data['remoteAddr']
                    config_data['remotePort'] = ipConfig.cleaned_data['remotePort']
                    config_data['localAddr'] = ipConfig.cleaned_data['localAddr']
                    config_data['srcPortUac'] = ipConfig.cleaned_data['srcPortUac']
                    config_data['srcPortUas'] = ipConfig.cleaned_data['srcPortUas']
                    config_data['calledPartyNumber'] = moreOptionsForm.cleaned_data['calledPartyNumber']
                    config_data['callingPartyNumber'] = moreOptionsForm.cleaned_data['callingPartyNumber']
                    config_data['totalNoOfCalls'] = moreOptionsForm.cleaned_data['totalNoOfCalls']
                    config_data['cps'] = moreOptionsForm.cleaned_data['cps']
                    
                    # config set for saving in config.ini
                    for configKey, configValue in config_data.items():
                        config.set('DEFAULT', configKey, str(configValue))


                    # remoteAddr = ipConfig.cleaned_data['remoteAddr']
                    # remotePort = ipConfig.cleaned_data['remotePort']
                    # localAddr = ipConfig.cleaned_data['localAddr']
                    # srcPortUac = ipConfig.cleaned_data['srcPortUac']
                    # srcPortUas = ipConfig.cleaned_data['srcPortUas']

                    # config.set('DEFAULT', 'remote_address', remoteAddr)
                    # config.set('DEFAULT', 'remote_port', str(remotePort))
                    # config.set('DEFAULT', 'local_address', localAddr)
                    # config.set('DEFAULT', 'uac_port', str(srcPortUac))
                    # config.set('DEFAULT', 'uas_port', str(srcPortUas))

                    
                    # calledPartyNumber = moreOptionsForm.cleaned_data['calledPartyNumber']
                    # callingPartyNumber = moreOptionsForm.cleaned_data['callingPartyNumber']
                    # totalNoOfCalls = moreOptionsForm.cleaned_data['totalNoOfCalls']
                    # cps = moreOptionsForm.cleaned_data['cps']

                    # config.set('DEFAULT', 'called_Party_Number', calledPartyNumber)
                    # config.set('DEFAULT', 'calling_Party_Number', callingPartyNumber)
                    # config.set('DEFAULT', 'total_no_of_calls', str(totalNoOfCalls))
                    # config.set('DEFAULT', 'cps', str(cps))
                    


                    # Update the config file after config.set
                    ConfigFile = os.path.join(settings.BASE_DIR, 'config.ini')
                    with open(ConfigFile, 'w') as configfile:
                        config.write(configfile)
                    


                    #update script prints on homepage
                    remote=f"{config_data['remoteAddr']}:{config_data['remotePort']}"
                    uacSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUac']}"
                    uasSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUas']}"

                    # below vars used on index.html
                    print_uac_command = f"sipp -sf {xml_data['selectUAC']} {remote} {uacSrc} -m 1"
                    print_uas_command = f"sipp -sf {xml_data['selectUAS']} {remote} {uasSrc}"

                    return render(request, 'index.html', locals())

    return render(request, 'index.html', locals())



######## Index End ############

######################## Modify XML funtion calls ###############################################

def modifyXml(request):
    if request.method == 'POST':

        if 'modifyXml' not in request.session:
            request.session['modifyXml'] = None

        modifyXml = request.session['modifyXml']

        if 'selectXml' in request.POST:
            selectXml = request.POST['selectXml']
            modifyXmlForm = xmlForm(request.POST)
            if modifyXmlForm.is_valid():
                if selectXml == 'modifyUAC':
                    modifyXml = modifyXmlForm.cleaned_data['selectUAC']
                elif selectXml == 'modifyUAS':
                    modifyXml = modifyXmlForm.cleaned_data['selectUAS']

            request.session['modifyXml'] = modifyXml #store var in session            
            modifyHeaderFormData = modifyHeaderForm() #load modify header form


            # modifyHeaderFormDataNew = modifyHeaderFormNew()


        # if modifyXml is not None:
        #     if 'modifyXmlSubmit' in request.POST:
        #         modifyXmlSubmit = request.POST['modifyXmlSubmit']
        #         modifyHeaderFormData = modifyHeaderForm(request.POST)
        #         if modifyXmlSubmit == 'newHeader':
        #             if modifyHeaderFormData.is_valid():
        #                 selectedHeader = modifyHeaderFormData.cleaned_data['whichHeader']
        #                 newHeader = modifyHeaderFormData.cleaned_data['modifyHeader']
        #                 modifyHeaderScript(modifyXml, selectedHeader, newHeader)



        if modifyXml is not None:
            if 'modifyXmlSubmit' in request.POST:
                modifyXmlSubmit = request.POST['modifyXmlSubmit']
                if modifyXmlSubmit == 'headerToModify':
                    modifyHeaderFormData = modifyHeaderForm(request.POST)
                    if modifyHeaderFormData.is_valid():
                        selectedHeader = modifyHeaderFormData.cleaned_data['whichHeader']
                        headersBySipMessage = getHeadersFromSipMsgs(modifyXml, selectedHeader)
                        modifySelectedHeaderForSipMsgsForm = modifySelectedHeaderForSipMsgs(headersBySipMessage)

                        






                        
                if modifyXmlSubmit == 'doneModify':
                    request.session['modifyXml'] = None

                if modifyXmlSubmit == 'xmlEditor':

                    modXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', modifyXml)
                    newModXmlPath = os.path.join(settings.BASE_DIR, 'kSipP', 'xml', 'uas_kiran.xml')

                    with open(modXmlPath, 'r') as file:
                        xml_content = file.read()
                    
                    return render(request, 'xml_editor.html', {'xml_content':xml_content})


    modifyXmlForm = xmlForm(initial=xml_data)
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





########################## Run SipP Scripts ##########################

def run_script_view(request):

    # cwd = os.path.dirname(os.path.abspath(__file__))
    # baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # sipp = os.path.join(baseDir, 'kSipP', 'sipp', 'sipp')
    sipp = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'sipp')
    # uacXml = str(settings.BASE_DIR / 'kSipP' / 'xml' / f'{xml_data["selectUAC"]}')
    # uasXml = str(settings.BASE_DIR / 'kSipP' / 'xml' / f'{xml_data["selectUAS"]}')
    # remote=f"{config_data['remoteAddr']}:{config_data['remotePort']}"
    # uacSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUac']}"
    # uasSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUas']}"

    # print_uac_command = f"sipp -sf {xml_data['selectUAC']} {remote} {uacSrc} -m 1"
    # print_uas_command = f"sipp -sf {xml_data['selectUAS']} {remote} {uasSrc}"

    if request.method == 'POST':
        scriptName = request.POST.get('script')

        if scriptName == 'UAC':
            try:
                uacCommand = f"{sipp} -sn uac 1.1.1.1 -m 1"
                uacProc=subprocess.Popen(uacCommand,shell=True)
                sipp_pid = None
                for process in psutil.process_iter(['pid', 'cmdline']):
                    if process.info['cmdline'] and ' '.join(process.info['cmdline']) == uacCommand:
                        sipp_pid = process.info['pid']
                        break
                return HttpResponse(f"shell pid = {uacProc.pid} and sipp pid = {sipp_pid} ")
                
            except Exception as e:
                print(f"Error: {e}")
            
            # while uacProc.poll() is None:
            #     uacStatus=f"UAC script is running"
            
        if scriptName =='UAS':
            env = os.environ.copy()
            env["PATH"] += os.pathsep + sipp
            try:
                uasCommand = f"{sipp} -sn uas"
                uasProc=subprocess.Popen(uasCommand, shell=False)
            except Exception as e:
                print(f"Error: {e}")
            
            # while uasProc.poll() is None:
            #     uasStatus=f"UAS script is running"

    return render(request, 'run_script_template.html', locals())
