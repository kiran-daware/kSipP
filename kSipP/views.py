from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
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



