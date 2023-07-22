from django import forms

class ConfigForm(forms.Form):
    remoteAddr = forms.GenericIPAddressField(label='Remote Address', protocol='IPv4')
    remotePort = forms.IntegerField(label='Remote Port', min_value=1000, max_value=9999, initial=5060)
    srcAddr = forms.GenericIPAddressField(label='Source Address', protocol='IPv4')
    srcPort = forms.IntegerField(label='Source Port', min_value=1000, max_value=9999, initial=5060)
    # Add more fields for other configuration settings as needed
