from django import forms
from django.conf import settings
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

        sorted_choices = sorted(choices, key=lambda choice: choice[1])

        return sorted_choices


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

    # modifyHeader = forms.CharField(
    #     label='Modify Header',
    #     max_length=200,  # You can set the maximum length for the text input.
    #     widget=forms.TextInput(attrs={'style': 'width: 500px;'}),
    # )




# class modifySelectedHeaderForSipMsgs(forms.Form):
#     def __init__(self, headersBySipMessage, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         for sipMessage, header in headersBySipMessage.items():
#             self.fields[sipMessage] = forms.CharField(
#                 label=sipMessage,
#                 initial='\n'.join(header),
#                 max_length=200,
#                 widget=forms.TextInput(attrs={'style': 'width: 500px;'}),
#                 required=False,  # Optional, set to True if modification is mandatory.
#             )
#             self.fields[sipMessage].widget = forms.TextInput(attrs={'value': sipMessage})




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




# class modifySelectedHeaderForSipMsgs(forms.Form):
#     def __init__(self, headersBySipMessage, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         for sipMessage, header in headersBySipMessage.items():
#             label_value = sipMessage
#             field_name = f"{sipMessage}_field"  # Create a unique field name for each label
#             self.fields[field_name] = forms.CharField(
#                 initial='\n'.join(header),
#                 widget=forms.TextInput(attrs={'style': 'width: 500px;'}),
#                 required=False,  # Optional, set to True if modification is mandatory.
#             )
#             # Add a hidden input field for the label
#             self.fields[field_name].label = False
#             self.fields[field_name].widget = forms.HiddenInput(attrs={'value': label_value})


