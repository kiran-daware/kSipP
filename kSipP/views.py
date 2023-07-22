from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from .forms import ConfigForm
import os
import subprocess

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def run_script_view(request):
    if request.method == 'POST':
        script_path = str(settings.BASE_DIR / 'kSipP' / 'scripts' / 'myScript.py')
        try:
            result = subprocess.check_output(['python', script_path]).decode('utf-8').strip()
            return HttpResponse(result)
        except subprocess.CalledProcessError as e:
            # Handle any errors that may occur when running the script
            return HttpResponse(f"Error occurred: {e}")
    
    return render(request, 'run_script_template.html')


def modifyXml(request):
    modifyXml_script = str(settings.BASE_DIR / 'kSipP' / 'scripts' / 'modifyHeader.py')
    try:
        result = subprocess.run(['python', modifyXml_script], capture_output=True, text=True)
        return HttpResponse(result)
    except subprocess.CalledProcessError as e:
        # Handle any errors that may occur when running the script
        return HttpResponse(f"Error occurred: {e}")



def write_config(request):
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            # Get the configuration data from the form
            remoteAddr = form.cleaned_data['remoteAddr']
            remotePort = form.cleaned_data['remotePort']
            srcAddr = form.cleaned_data['srcAddr']
            srcPort = form.cleaned_data['srcPort']

            # Get more settings from the form as needed

            # Create the configuration content
            config_content = f'''[DEFAULT]\n
remoteAddr = {remoteAddr}\nremotePort = {remotePort}
srcAddr = {srcAddr}\nsrcPort = {srcPort}'''

            # Add more settings to the config_content as needed

            # Define the path to the config file
            config_file_path = os.path.join(settings.BASE_DIR, 'config.ini')

            # Write the configuration to the file
            with open(config_file_path, 'w') as file:
                file.write(config_content)

            return render(request, 'success_template.html')
    else:
        form = ConfigForm()

    return render(request, 'config_template.html', {'form': form})


