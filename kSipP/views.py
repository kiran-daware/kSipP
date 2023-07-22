from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from .forms import ConfigForm, xmlForm
import configparser
import os
import subprocess

config_file = os.path.join(str(settings.BASE_DIR), 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)
configd = config['DEFAULT']



def index(request):
    return render(request, 'index.html')



def modifyXml(request):
    if request.method == 'POST':
        if 'submitType' in request.POST:
            submit_type = request.POST['submitType']
            if submit_type =='selectXml':
                modifyXmlForm = xmlForm(request.POST)
                scenario =  modifyXmlForm['selectUAS']
                return HttpResponse(f"Selected Scenario {scenario}")
            
        if 'xmlName' in request.POST:
            xmlName = request.POST.get('xmlName')
            modifyXml_script = str(settings.BASE_DIR / 'kSipP' / 'scripts' / 'modifyHeader.py')
            try:
                result = subprocess.run(['python', modifyXml_script], capture_output=True, text=True)
                return HttpResponse(result)
            except subprocess.CalledProcessError as e:
                # Handle any errors that may occur when running the script
                return HttpResponse(f"Error occurred: {e}")

    modifyXmlForm = xmlForm()
    return render(request, 'modify_xml.html', {'form': modifyXmlForm})



config_data = {
    'remoteAddr': configd.get('remoteAddr'),
    'remotePort': configd.get('remotePort'),
    'srcAddrUac': configd.get('srcAddrUac'),
    'srcPortUac': configd.get('srcPortUac'),
    'srcAddrUas': configd.get('srcAddrUas'),
    'srcPortUas': configd.get('srcPortUas'),
}


def write_config(request):
    if request.method == 'POST':
        form = ConfigForm(request.POST)
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
        form = ConfigForm(initial=config_data)

    return render(request, 'config_template.html', {'form': form})



def run_script_view(request):
    if request.method == 'POST':
        scriptName = request.POST.get('script')

        sipp = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'sipp.exe')
        uacXml = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'UAC.xml')
        uasXml = str(settings.BASE_DIR / 'kSipP' / 'sipp' / 'UAS.xml')
        remote=f"{config_data['remoteAddr']}:{config_data['remotePort']}"
        uacSrc=f"-i {config_data['srcAddrUac']} -p {config_data['srcPortUac']}"
        uasSrc=f"-i {config_data['srcAddrUas']} -p {config_data['srcPortUas']}"
        
        if scriptName == 'UAC':
            try:
                subprocess.Popen(["start", "cmd.exe", "/K", f"{sipp} -sf {uacXml} {remote} {uacSrc} -m 1"], shell=True)
            except Exception as e:
                print(f"Error: {e}")
            
        if scriptName =='UAS':
            try:
                subprocess.Popen(["start", "cmd.exe", "/K", f"{sipp} -sf {uasXml} {remote} {uasSrc}"], shell=True)
            except Exception as e:
                print(f"Error: {e}")
    
    return render(request, 'run_script_template.html')