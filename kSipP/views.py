from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.conf import settings
from .forms import configForm, xmlForm
import configparser
import os
import subprocess


# Read initial data from config file
config_file = os.path.join(str(settings.BASE_DIR), 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)
configd = config['DEFAULT']
configx = config['XML']

#global variables
config_data = {}
xml_data = {}


@never_cache
def index(request):

    global config_data
    config_data = {
        'remoteAddr': configd.get('remote_address'),
        'remotePort': configd.get('remote_port'),
        'localAddr': configd.get('local_address'),
        'srcPortUac': configd.get('uac_port'),
        'srcPortUas': configd.get('uas_port'),
    }
    global xml_data
    xml_data = {
        'selectUAC':configx.get('uac_script'),
        'selectUAS':configx.get('uas_script')
    }
    
    remote=f"{config_data['remoteAddr']}:{config_data['remotePort']}"
    uacSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUac']}"
    uasSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUas']}"
    print_uac_command = f"sipp -sf {xml_data['selectUAC']} {remote} {uacSrc} -m 1"
    print_uas_command = f"sipp -sf {xml_data['selectUAS']} {remote} {uasSrc}"

    selectXml = xmlForm(initial=xml_data)
    ipConfig = configForm(initial=config_data)
    if request.method == 'POST':
        if 'submitType' in request.POST:
            submit_type = request.POST['submitType']
            if submit_type =='config':
                selectXml = xmlForm(request.POST)
                ipConfig = configForm(request.POST)
                if selectXml.is_valid() & ipConfig.is_valid():

                    selectUAC = selectXml.cleaned_data['selectUAC']
                    selectUAS = selectXml.cleaned_data['selectUAS']
                    config.set('XML','uac_script', selectUAC)
                    config.set('XML','uas_script', selectUAS)

                    remoteAddr = ipConfig.cleaned_data['remoteAddr']
                    remotePort = ipConfig.cleaned_data['remotePort']
                    localAddr = ipConfig.cleaned_data['localAddr']
                    srcPortUac = ipConfig.cleaned_data['srcPortUac']
                    srcPortUas = ipConfig.cleaned_data['srcPortUas']

                    config.set('DEFAULT', 'remote_address', remoteAddr)
                    config.set('DEFAULT', 'remote_port', str(remotePort))
                    config.set('DEFAULT', 'local_address', localAddr)
                    config.set('DEFAULT', 'uac_port', str(srcPortUac))
                    config.set('DEFAULT', 'uas_port', str(srcPortUas))
                    
                    # Update the config file
                    ConfigFile = os.path.join(settings.BASE_DIR, 'config.ini')
                    with open(ConfigFile, 'w') as configfile:
                        config.write(configfile)

                    return render(request, 'index.html', locals())

    return render(request, 'index.html', locals())





def modifyXml(request):
    if request.method == 'POST':
        if 'submitType' in request.POST:
            submit_type = request.POST['submitType']
            if submit_type =='selectXml':
                modifyXmlForm = xmlForm(request.POST)
                if modifyXmlForm.is_valid():
                    selectUAC = modifyXmlForm.cleaned_data['selectUAC']
                    selectUAS = modifyXmlForm.cleaned_data['selectUAS']
                    xmlContent = f'''[DEFAULT]\n
UAC = {selectUAC}
UAS = {selectUAS}
'''
                    xmlConfigFile = os.path.join(settings.BASE_DIR, 'xml.ini')
                    with open(xmlConfigFile, 'w') as file:
                        file.write(xmlContent)
                    return render(request, 'modify_xml.html', {'form': modifyXmlForm})
            
        if 'xmlName' in request.POST:
            xmlName = request.POST.get('xmlName')
            if xmlName.is_valid():
                

                modifyXml_script = str(settings.BASE_DIR / 'kSipP' / 'scripts' / 'modifyHeader.py')
            try:
                result = subprocess.run(['python', modifyXml_script], capture_output=True, text=True)
                return HttpResponse(result)
            except subprocess.CalledProcessError as e:
                # Handle any errors that may occur when running the script
                return HttpResponse(f"Error occurred: {e}")

    modifyXmlForm = xmlForm()
    return render(request, 'modify_xml.html', {'form': modifyXmlForm})





#def write_config(request):
    if request.method == 'POST':
        form = configForm(request.POST)
        if form.is_valid():
            # Get the configuration data from the form
            remoteAddr = form.cleaned_data['remoteAddr']
            remotePort = form.cleaned_data['remotePort']
            srcAddrUac = form.cleaned_data['srcAddrUac']
            srcPortUac = form.cleaned_data['srcPortUac']
            srcAddrUas = form.cleaned_data['srcAddrUas']
            srcPortUas = form.cleaned_data['srcPortUas']

            # Get more settings from the form as needed

            # Create the configuration content
            config_content = f'''[DEFAULT]\n
remoteAddr = {remoteAddr}\nremotePort = {remotePort}
srcAddrUac = {srcAddrUac}\nsrcPortUac = {srcPortUac}
srcAddrUas = {srcAddrUas}\nsrcPortUAS = {srcPortUas}'''

            # Add more settings to the config_content as needed

            # Define the path to the config file
            config_file_path = os.path.join(settings.BASE_DIR, 'config.ini')

            # Write the configuration to the file
            with open(config_file_path, 'w') as file:
                file.write(config_content)

            return render(request, 'success_template.html')
    else:
        form = configForm(initial=config_data)

    return render(request, 'config_template.html', {'form': form})



def run_script_view(request):

    sipp = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'sipp.exe')
    uacXml = str(settings.BASE_DIR / 'kSipP' / 'xml' / f'{xml_data["selectUAC"]}')
    uasXml = str(settings.BASE_DIR / 'kSipP' / 'xml' / f'{xml_data["selectUAS"]}')
    remote=f"{config_data['remoteAddr']}:{config_data['remotePort']}"
    uacSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUac']}"
    uasSrc=f"-i {config_data['localAddr']} -p {config_data['srcPortUas']}"

    print_uac_command = f"sipp -sf {xml_data['selectUAC']} {remote} {uacSrc} -m 1"
    print_uas_command = f"sipp -sf {xml_data['selectUAS']} {remote} {uasSrc}"

    if request.method == 'POST':
        scriptName = request.POST.get('script')
        if scriptName == 'UAC':
            try:
                uacCommand = f"{sipp} -sf {uacXml} {remote} {uacSrc} -m 1"
                subprocess.Popen(["start", "cmd.exe", "/K", uacCommand], shell=True)
            except Exception as e:
                print(f"Error: {e}")
            
        if scriptName =='UAS':
            try:
                uasCommand = f"{sipp} -sf {uasXml} {remote} {uasSrc}"
                subprocess.Popen(["start", "cmd.exe", "/K", uasCommand], shell=True)
            except Exception as e:
                print(f"Error: {e}")

    return render(request, 'run_script_template.html', locals())