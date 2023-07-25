##### Options list

    # uac_files = [f for f in os.listdir(xmlPath) if f.startswith('uac')]
    # uas_files = [f for f in os.listdir(xmlPath) if f.startswith('uas')]

    # optsUAC = [(filename, filename) for filename in uac_files] 
    # selectUAC = forms.ChoiceField(choices=optsUAC, label='Select UAC scenario')

    # optsUAS = [(filename, filename) for filename in uas_files] 
    # # optsUAS = [
    # #     ('uas.xml', 'Basic'),
    # #     ('uas_Prack.xml', 'Receive Prack'),
    # #     ('uas_Media.xml', 'Send Media'),
    # # ]
    # selectUAS = forms.ChoiceField(choices=optsUAS, label='Select UAS scenario')  