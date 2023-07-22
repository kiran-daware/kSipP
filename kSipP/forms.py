from django import forms

class ConfigForm(forms.Form):
    remoteAddr = forms.GenericIPAddressField(label='Remote Address', protocol='IPv4')
    remotePort = forms.IntegerField(label='Remote Port', min_value=1000, max_value=9999, initial=5060)
    srcAddrUac = forms.GenericIPAddressField(label='UAC Source Address', protocol='IPv4')
    srcPortUac = forms.IntegerField(label='UAC Source Port', min_value=1000, max_value=9999, initial=5060)
    srcAddrUas = forms.GenericIPAddressField(label='UAS Source Address', protocol='IPv4')
    srcPortUas = forms.IntegerField(label='UAS Source Port', min_value=1000, max_value=9999, initial=5060)
    # Add more fields for other configuration settings as needed
