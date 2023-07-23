from django import forms
from django.conf import settings
import os

class configForm(forms.Form):
    remoteAddr = forms.GenericIPAddressField(label='Remote Address', protocol='IPv4')
    remotePort = forms.IntegerField(label='Remote Port', min_value=1000, max_value=9999, initial=5060)
    localAddr = forms.GenericIPAddressField(label='Local Address', protocol='IPv4')
    srcPortUac = forms.IntegerField(label='UAC Source Port', min_value=1000, max_value=9999, initial=5060)
    srcPortUas = forms.IntegerField(label='UAS Source Port', min_value=1000, max_value=9999, initial=5060)
    # Add more fields for other configuration settings as needed


class xmlForm(forms.Form):

    xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml')
    uac_files = [f for f in os.listdir(xmlPath) if f.startswith('uac')]
    uas_files = [f for f in os.listdir(xmlPath) if f.startswith('uas')]

    optsUAC = [(filename, filename) for filename in uac_files] 
    # optsUAC = [
    #     ('uac.xml', 'Basic'),
    #     ('uac_Prack.xml', 'Send Prack'),
    #     ('uac_Media.xml', 'Send Media'),
    # ]
    selectUAC = forms.ChoiceField(choices=optsUAC, label='Select UAC scenario')

    optsUAS = [(filename, filename) for filename in uas_files] 
    # optsUAS = [
    #     ('uas.xml', 'Basic'),
    #     ('uas_Prack.xml', 'Receive Prack'),
    #     ('uas_Media.xml', 'Send Media'),
    # ]
    selectUAS = forms.ChoiceField(choices=optsUAS, label='Select UAS scenario')  