import lxml.etree as LE
import os
import configparser
import re, pprint
from django.conf import settings
import logging

# cwd = os.path.dirname(os.path.abspath(__file__))
baseDir = xmlPath = str(settings.BASE_DIR)
modifyHeaderLogNew = os.path.join(baseDir, 'modifyHeader.log')
logging.basicConfig(filename=modifyHeaderLogNew, filemode='w', level=logging.DEBUG)

# Fetching Variables from Config File
# config_file = os.path.join(baseDir, 'config.ini')
# config = configparser.ConfigParser()
# config.read(config_file)
# configd = config['DEFAULT']

# Open SipP scenario.xml file
def openXML(xml_file):
    xml_file_path = os.path.join(baseDir, 'kSipP', 'xml', xml_file)

    with open(xml_file_path, "r") as f:
        xml_data = f.read()

    # Parse the XML file
    logging.info("XML file opened for modifying header. Xml filename is %s", xml_file)
    parser = LE.XMLParser(strip_cdata=False)
    return(LE.XML(xml_data.encode(), parser))


def getHeadersFromSipMsgs(xml_file, header):
    headersBySipMessage = {}
    root = openXML(xml_file)
    # Find the "send" element
    for send in root.iter("send"):
        send.text = LE.CDATA(send.text)
        cdata_element = send.text
        logging.debug(cdata_element)
        if cdata_element is not None:
            # Split the CDATA content into lines
            cdata_lines = cdata_element.strip().splitlines()
            # headerLine = [line.strip() for line in cdata_lines if line.strip().startswith(header)]
            headerLine = [line.strip()[len(header)+1:] for line in cdata_lines if line.strip().startswith(header)]


            if headerLine:
                sipMessage = cdata_element.strip().split(" ", 1)[0]
                if sipMessage.startswith("SIP"):
                    sipMessage = cdata_lines[0].split(maxsplit=1)[1]
            
                headersBySipMessage[sipMessage] = headerLine

    # pprint.pprint(headersBySipMessage)
    return headersBySipMessage




# Modify Header in xml
def modifyHeaderScript(xml_file, sipMessage, header, newHeader, newXmlFileName = None):
    logging.info(xml_file + sipMessage + header + newHeader)
    # xml_file_noExt = xml_file.rsplit(".", 1)[0]
    uacuas = 'uac' if xml_file.startswith('uac') else ('uas' if xml_file.startswith('uas') else None)
    if newXmlFileName is not None:
        new_xml_file = os.path.join(baseDir, 'kSipP', 'xml', f'{uacuas}_{newXmlFileName}.xml')
    else:
        new_xml_file = os.path.join(baseDir, 'kSipP', 'xml', f'{xml_file}')

    if os.path.isfile(new_xml_file):
        root = openXML(new_xml_file)
    else: 
        root = openXML(xml_file)
    # Find the "send" element
    for send in root.iter("send"):
        send.text = LE.CDATA(send.text)
        cdata_element = send.text
        if cdata_element is not None:
            # Split the CDATA content into lines
            cdata_lines = cdata_element.strip().splitlines()
            sipMessageHere = cdata_element.strip().split(" ", 1)[0]

            if sipMessageHere.startswith("SIP"):
                sipMessageHere = cdata_lines[0].split(maxsplit=1)[1]

            if sipMessageHere == sipMessage:
                # Find and replace the 'To:' line
                for i, line in enumerate(cdata_lines):
                    if line.strip().startswith(header):
                        leading_whitespace = line[:line.find(header)]
                        cdata_lines[i] = leading_whitespace +  header + " " + newHeader
                        logging.debug("modified" + sipMessage + (cdata_lines[i]))

                        # Join the modified lines back into CDATA content
                        modified_cdata_text = "\n".join(cdata_lines)
                        send.text = None
                        send.text=(LE.CDATA("\n\n" + leading_whitespace + modified_cdata_text + "\n\n"))
                        logging.debug(modified_cdata_text)                        
                        
                        # LE.tostring(send, pretty_print=True).decode()
                        with open(new_xml_file, "wb") as f:
                            f.write(LE.tostring(root, encoding="utf-8", xml_declaration=True))
                            
                        break

       


# #PrettyXml
# with open(xml_file_path, 'r') as file:
#     xml_content = file.read()

# newLineBeforeCdata = xml_content.replace('<![CDATA[', '\n\n    <![CDATA[')
# newLineAfterCdata = newLineBeforeCdata.replace(']]>', '    ]]>')
# modifiedXML = newLineAfterCdata.replace('</send>', '\n\n  </send>')
# # Write the modified XML content back to the same file
# with open(new_xml_file, 'w') as file:
#     file.write(modifiedXML)




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


# code for modifying Calling party number and dialed number is any one is present

def modifynumberxmlpath(xml, calling_number="sipp", dialed_number="[service]"):
    if not calling_number: calling_number = "sipp"
    if not dialed_number: dialed_number = "[service]"
    calling_display=f'"{calling_number}" '
    dailed_display=f'"{dialed_number}" '

    xmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / xml)
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
    
    tmpXmlPath = str(settings.BASE_DIR / 'kSipP' / 'xml' / 'tmp' / xml)
    with open(tmpXmlPath, 'w') as file:
        file.write(updated_xml)
        
    return tmpXmlPath