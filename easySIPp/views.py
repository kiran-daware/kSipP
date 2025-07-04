from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .forms import UACForm, UASForm
from .forms import xmlUploadForm
from .models import UacAppConfig, UasAppConfig
from django.urls import reverse
import xml.etree.ElementTree as ET
import os, time, signal
import psutil
from .scripts.ksipp import get_sipp_processes, cleanFilename, run_uac, run_uas
from .scripts.list import listXmlFiles
import logging


logger = logging.getLogger(__name__)


################### Index Page Functions #############################

@never_cache
def index(request):
    showMoreOptionsForm = False
    uac_form = None
    uas_form = None

    if request.method == 'POST':
        if 'selected_key' in request.POST:
            selected_key = request.POST['selected_key']
            print(selected_key)
            try:
                if selected_key.startswith('uac'):
                    uac_config = UacAppConfig.objects.get(uac_key=selected_key)
                    uac_config.is_active_config = True
                    uac_config.save()

                elif selected_key.startswith('uas'):
                    uas_config = UasAppConfig.objects.get(uas_key=selected_key)
                    uas_config.is_active_config = True
                    uas_config.save()

            except Exception as e:
                logger.exception("Unhandled exception:", e)
            
            return redirect('index')


        elif 'save_conf' in request.POST:
            save_conf = request.POST['save_conf']

            if save_conf in ['save_uac', 'save_run_uac']:
                selected_uac_key = request.POST.get('uac_key')
                if selected_uac_key:
                    uac_config = UacAppConfig.objects.get(uac_key=selected_uac_key)
                    uac_form = UACForm(request.POST, instance=uac_config)
                    if uac_form.is_valid():
                        uac_form.save()
                        if save_conf == 'save_run_uac':
                            sipp_error = run_uac(uac_config)
                            # Only redirect if no error
                            if sipp_error:
                                messages.error(request, sipp_error)
                                return redirect('index')
                        
                        return redirect('index')

                    else:
                        fields_to_check = ['called_party_number', 'calling_party_number', 'stun_server',
                                           'total_no_of_calls', 'cps']
                        showMoreOptionsForm = any(field in uac_form.errors for field in fields_to_check)


            elif save_conf in ['save_uas', 'save_run_uas']:
                selected_uas_key = request.POST.get('uas_key')
                if selected_uas_key:
                    uas_config = UasAppConfig.objects.get(uas_key=selected_uas_key)
                    uas_form = UASForm(request.POST, instance=uas_config)      
                    if uas_form.is_valid():
                        uas_form.save()                        
                        if save_conf == 'save_run_uas':
                            sipp_error = run_uas(uas_config)
                            if sipp_error:
                                messages.error(request, sipp_error)
                                return redirect('index')
                        
                        return redirect('index')


        elif 'send_signal' in request.POST:
            send_signal = request.POST.get('send_signal')
            pid = request.POST.get('pid_to_kill')

            if send_signal == 'Kill':
                try:
                    process = psutil.Process(int(pid))
                    process.terminate()  # You can also use process.kill() for a more forceful termination
                    process.wait(timeout=2)  # Wait for it to exit
                except (psutil.NoSuchProcess, psutil.TimeoutExpired) as e:
                    logger.exception(e)
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


    # To make sure to form was not already loaded and avoid refreshing despite form errors
    if not uac_form:
        uac_config = UacAppConfig.objects.get(is_active_config=True)
        uac_form = UACForm(instance=uac_config)
    if not uas_form:
        uas_config = UasAppConfig.objects.get(is_active_config=True)
        uas_form = UASForm(instance=uas_config)

    uac_xml = uac_config.select_uac
    uas_xml = uas_config.select_uas

    print_uac_command = f""
    print_uas_command = f""

    sipp_processes = get_sipp_processes()
    context = {
        'uac_xml': uac_xml,
        'uas_xml': uas_xml,
        'print_uac_command': print_uac_command,
        'print_uas_command': print_uas_command,
        'UACForm': uac_form,
        'UASForm': uas_form,
        'sipp_processes': sipp_processes,
        'showMoreOptionsForm': showMoreOptionsForm if 'showMoreOptionsForm' in locals() else False,
        'sipp_error': sipp_error if 'sipp_error' in locals() else False
        }

    return render(request, 'index.html', context)

######## Index End ############


def serveXmlFile(request, xmlname):
    xmlPath = str(settings.BASE_DIR / 'easySIPp' / 'xml' / xmlname)
    with open(xmlPath, 'r') as file:
        xmlContent = file.read()
    return HttpResponse(xmlContent, content_type='text/plain')


def xmlEditor(request):
    if request.method == 'GET':
        xmlName=request.GET.get('xml')
        referer=request.GET.get('back', 'index')
        if xmlName is None:
            return HttpResponse('No xml selected <a href="/xml-management/">Select here!</a>')
        xmlPath = str(settings.BASE_DIR / 'easySIPp' / 'xml' / xmlName)
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

        with open(os.path.join(settings.BASE_DIR, 'easySIPp', 'xml', savingXmlName), 'w', encoding='utf-8') as file:
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
        with open(os.path.join(settings.BASE_DIR, 'easySIPp', 'xml', cleanedFilename), 'w', encoding='utf-8') as file:
            file.write(xmlContent)
    
    context = {
        'xml_content':xmlContent if 'xmlContent' in locals() else False,
        'xml_name':fileName if 'fileName' in locals() else False,
    }

    return render(request, 'create_scenario_xml.html', context)


def xml_mgmt_view(request):
    xmlDir = os.path.join(settings.BASE_DIR, 'easySIPp', 'xml')
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
