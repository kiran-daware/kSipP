from django import forms
from django.conf import settings
import xml.etree.ElementTree as ET
import os
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import AppConfig

class xmlForm(forms.ModelForm):
    select_uac = forms.ChoiceField(label='Select UAC')  # override explicitly
    select_uas = forms.ChoiceField(label='Select UAS')

    class Meta:
        model = AppConfig
        fields = ['select_uac', 'select_uas']

    xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['select_uac'].choices = self._get_xml_file_choices('uac')
        self.fields['select_uas'].choices = self._get_xml_file_choices('uas')

    def _get_xml_file_choices(self, prefix):
        try:
            return sorted([
                (f, f) for f in os.listdir(self.xmlPath)
                if f.endswith('.xml') and f.startswith(prefix)
            ])
        except FileNotFoundError:
            return []


class configForm(forms.ModelForm):
    class Meta:
        model = AppConfig
        fields = [
            'uac_remote', 'uac_remote_port',
            'uas_remote', 'uas_remote_port',
            'local_addr', 'src_port_uac', 'src_port_uas',
            'protocol_uac', 'protocol_uas'
        ]


class moreSippOptionsForm(forms.ModelForm):
    called_party_number = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^[a-zA-Z0-9]+$', 'Only alphanumeric characters are allowed.')])
    calling_party_number = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^[a-zA-Z0-9]+$', 'Only alphanumeric characters are allowed.')])

    class Meta:
        model = AppConfig
        fields = ['called_party_number', 'calling_party_number', 'total_no_of_calls', 'cps', 'stun_server']


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
