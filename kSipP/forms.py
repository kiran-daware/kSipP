from django import forms
from django.conf import settings
import xml.etree.ElementTree as ET
import os
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError




class xmlForm(forms.Form):

    xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['select_uac'] = forms.ChoiceField(label='Select UAC', choices=self._get_xml_file_choices('uac'))
        self.fields['select_uas'] = forms.ChoiceField(label='Select UAS', choices=self._get_xml_file_choices('uas'))
    
    def _get_xml_file_choices(self, field_name):
        # Query the available XML files in the directory and generate choices dynamically
        choices = []
        for filename in os.listdir(self.xmlPath):
            if filename.endswith('.xml'):
                if field_name == 'uac' and filename.startswith('uac'):
                    choices.append((filename, filename))
                elif field_name == 'uas' and filename.startswith('uas'):
                    choices.append((filename, filename))

        sorted_choices = sorted(choices, key=lambda choice: choice[1])

        return sorted_choices


class moreSippOptionsForm(forms.Form):
    called_party_number = forms.CharField(label='Dialed Number', max_length=30, required=False, initial='1234',
                                          validators=[RegexValidator(r'^[a-zA-Z0-9]+$','Only alphanumeric characters are allowed.')])
    calling_party_number = forms.CharField(label='Calling Party Number', max_length=30, required=False, initial='9876',
                                           validators=[RegexValidator(r'^[a-zA-Z0-9]+$','Only alphanumeric characters are allowed.')] )
    total_no_of_calls = forms.IntegerField(label='No. of calls to send', min_value=1, max_value=9999, required=True, initial=1)
    cps = forms.IntegerField(label='Calls Per Second', min_value=1, max_value=100, required=True, initial=1) 
    stun_server = forms.GenericIPAddressField(label='Stun Server', protocol='IPv4', required=False, initial='')



class configForm(forms.Form):
    uac_remote = forms.GenericIPAddressField(label='UAC Remote Address', protocol='IPv4')
    uac_remote_port = forms.IntegerField(label='UAC Remote Port', min_value=1000, max_value=9999, initial=5060)
    uas_remote = forms.GenericIPAddressField(label='UAS Remote Address', protocol='IPv4')
    uas_remote_port = forms.IntegerField(label='UAS Remote Port', min_value=1000, max_value=9999, initial=5060)
    local_addr = forms.GenericIPAddressField(label='Local Address', protocol='IPv4')
    src_port_uac = forms.IntegerField(label='UAC Src Port', min_value=1000, max_value=9999, initial=5060)
    src_port_uas = forms.IntegerField(label='UAS Src Port', min_value=1000, max_value=9999, initial=5060)
    protocol_uac = forms.ChoiceField(label='', choices=[('u1', 'UDP'),('tn', 'TCP')])
    protocol_uas = forms.ChoiceField(label='', choices=[('u1', 'UDP'),('tn', 'TCP')])
    # Add more fields for other configuration settings as needed



class modifyHeaderForm(forms.Form):
    optHeader = [
        ('From:','From'),
        ('To:','To'),
        ('Contact:','Contact'),
    ]
    whichHeader = forms.ChoiceField(choices=optHeader, label='Select Header')




class modifySelectedHeaderForSipMsgs(forms.Form):
    def __init__(self, *args, **kwargs):
        dictionary = kwargs.pop('hbsm')
        super(modifySelectedHeaderForSipMsgs, self).__init__(*args, **kwargs)

        for sipMessage, header_value in dictionary.items():
            self.fields[sipMessage] = forms.CharField(
                initial='\n'.join(header_value),
                label=sipMessage,
                max_length=200,
                widget=forms.TextInput(attrs={'style': 'width: 500px;'}),
                required=False,
                )




class xmlUploadForm(forms.Form):
    file = forms.FileField(label='Select an XML file', help_text='File name should start with "uac" or "uas".',
                           widget=forms.ClearableFileInput(attrs={'accept': '.xml', 'max_upload_size': 102400}))

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if not uploaded_file.name.lower().startswith(('uac', 'uas')) or not uploaded_file.name.lower().endswith('.xml'):
            raise ValidationError('File name should start with "uac" or "uas" and have .xml extension.')
        max_upload_size = 102400  # 100 KB in bytes
        if uploaded_file.size > max_upload_size:
            raise ValidationError('File size exceeds the maximum allowed limit (250 KB).')
        return uploaded_file
