import os
import re
from django.conf import settings
import logging

# cwd = os.path.dirname(os.path.abspath(__file__))
baseDir = xmlPath = str(settings.BASE_DIR)
modifyPy_log = os.path.join(baseDir, 'modifyHeader.log')
logging.basicConfig(filename=modifyPy_log, filemode='w', level=logging.DEBUG)


def tmpXmlBehindNAT(xml, externalIp, externalPort):
    xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / xml)
    with open(xmlPath, 'r') as file:
        xml_content = file.read()
    
    replaceExtIp = xml_content.replace('[local_ip]', externalIp)

    if xml.startswith("uac"):
        modifiedXML = replaceExtIp.replace('[local_port]',str(externalPort))
        # newXml = 'uac.xml'
    else: 
        modifiedXML = replaceExtIp #Not changing the NAT port for UAS 
        # newXml = 'uas.xml'
    tmpXmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / 'tmp' / xml)

    with open(tmpXmlPath, 'w') as file:
        file.write(modifiedXML)
        
    return tmpXmlPath


# code for modifying Calling party number and dialed number if any one is present

def modifynumberxmlpath(xmlPath, calling_number="sipp", dialed_number="[service]"):
    if not calling_number: calling_number = "sipp"
    if not dialed_number: dialed_number = "[service]"
    calling_display=f'"{calling_number}" '
    dailed_display=f'"{dialed_number}" '

    with open(xmlPath, 'r') as file:
        xml_content = file.read()
    
    logging.debug("Opened xml for modifying number = %s", xmlPath)

    from_pattern = r'(?i)\bFrom\b\:\s*"?(\w*)"?\s*(<?sip:)([^@\:\;\n]+)@'
    updated_xml = re.sub(from_pattern, lambda m: f'From: {calling_display if m.group(1) else ""}{m.group(2)}{calling_number}@', xml_content)

    contact_pattern = r'(?i)\bContact\b\:\s*"?(\w*)"?\s*(<?sip:)([^@\:\;\n]+)@'
    updated_xml = re.sub(contact_pattern, lambda m: f'Contact: {calling_display if m.group(1) else ""}{m.group(2)}{calling_number}@', updated_xml)

    ruri_pattern = r'(INVITE|ACK|BYE|CANCEL|OPTIONS|REGISTER)\s*sip:([^@\:\;\n]+)@'
    updated_xml = re.sub(ruri_pattern, r'\1 sip:'+ dialed_number +'@', updated_xml)

    to_pattern = r'(?i)\bTo\b\:\s*(\[|"?)(\w*)(\]|"?)\s*(<?sip:)([^@\:\;\n]+)@'
    updated_xml = re.sub(to_pattern, lambda m: f'To: {dailed_display if m.group(2) else ""}{m.group(4)}{dialed_number}@', updated_xml)
    
    xmlName = os.path.basename(xmlPath)
    tmpXmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / 'tmp' / xmlName)
    
    with open(tmpXmlPath, 'w') as file:
        file.write(updated_xml)
        
    return tmpXmlPath