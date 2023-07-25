from django import forms
from django.conf import settings
from collections import OrderedDict
import xml.etree.ElementTree as ET
import os




class xmlForm(forms.Form):

    xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selectUAC'] = forms.ChoiceField(label='Select UAC', choices=self._get_xml_file_choices('uac'))
        self.fields['selectUAS'] = forms.ChoiceField(label='Select UAS', choices=self._get_xml_file_choices('uas'))
    
    def _get_xml_file_choices(self, field_name):
        # Query the available XML files in the directory and generate choices dynamically
        choices = []
        for filename in os.listdir(self.xmlPath):
            if filename.endswith('.xml'):
                if field_name == 'uac' and filename.startswith('uac'):
                    choices.append((filename, filename))
                elif field_name == 'uas' and filename.startswith('uas'):
                    choices.append((filename, filename))

        return choices


class moreSippOptionsForm(forms.Form):
    calledPartyNumber = forms.CharField(label='Called Party Number', max_length=30, required=False, initial='1234')
    callingPartyNumber = forms.CharField(label='Calling Party Number', max_length=30, required=False, initial='9876')
    totalNoOfCalls = forms.IntegerField(label='No. of calls to send', min_value=1, max_value=9999, required=False, initial=1)
    cps = forms.IntegerField(label='Calls Per Second', min_value=1, max_value=100, required=False, initial=1) 



class configForm(forms.Form):
    remoteAddr = forms.GenericIPAddressField(label='Remote Address', protocol='IPv4')
    remotePort = forms.IntegerField(label='Remote Port', min_value=1000, max_value=9999, initial=5060)
    localAddr = forms.GenericIPAddressField(label='Local Address', protocol='IPv4')
    srcPortUac = forms.IntegerField(label='UAC Source Port', min_value=1000, max_value=9999, initial=5060)
    srcPortUas = forms.IntegerField(label='UAS Source Port', min_value=1000, max_value=9999, initial=5060)
    # Add more fields for other configuration settings as needed



class modifyHeaderForm(forms.Form):
    optHeader = [
        ('From:','From'),
        ('To:','To'),
        ('Contact:','Contact'),
    ]
    whichHeader = forms.ChoiceField(choices=optHeader, label='Select Header')

    modifyHeader = forms.CharField(
        label='Modify Header',
        max_length=200,  # You can set the maximum length for the text input.
        widget=forms.TextInput(attrs={'style': 'width: 500px;'}),
    )




class modifyHeaderFormNew(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        scenario_file = xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / 'uac.xml')  # Replace with the path to your SIPp scenario file.
        headers_by_send_element = self.get_available_headers(scenario_file)
        
        for message_name, headers in headers_by_send_element.items():
            for header_name in headers:
                self.fields[header_name] = forms.CharField(
                    label=message_name,
                    initial=header_name,
                    max_length=200,
                    widget=forms.TextInput(attrs={'style': 'width: 500px;'}),
                    required=False,  # Optional, set to True if modification is mandatory.
                )

    def get_available_headers(self, scenario_file):
        headers_by_send_element = OrderedDict()
        if os.path.exists(scenario_file):
            tree = ET.parse(scenario_file)
            root = tree.getroot()
            for element in root.iter("send"):
                if element.tag == "send":
                    cdata_element = element.text
                    if cdata_element is not None:
                        # Split the CDATA content into lines
                        message_name = cdata_element.strip().split(" ", 1)[0]
                        cdata_lines = cdata_element.strip().splitlines()
                        headers = []
                        for line in cdata_lines:
                            if line.strip():
                                header_name = line.strip()
                                
                                headers.append(header_name)
                        headers_by_send_element[message_name] = headers

        return headers_by_send_element

    
                    # Remove leading/trailing whitespaces and get the first word from CDATA
                        # header_name = (cdata_text.strip())


                        # header_name = header_element
                        
        # return headers

