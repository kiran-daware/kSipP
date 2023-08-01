import lxml.etree as LE
import os
import configparser
import pprint
from django.conf import settings
import logging

# cwd = os.path.dirname(os.path.abspath(__file__))
baseDir = xmlPath = str(settings.BASE_DIR)
modifyHeaderLogNew = os.path.join(baseDir, 'modifyHeader.log')
# logging.basicConfig(filename=modifyHeaderLogNew, filemode='w', level=logging.DEBUG)

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
    logging.info("XML file name is %s", xml_file)
    parser = LE.XMLParser(strip_cdata=False)
    return(LE.XML(xml_data.encode(), parser))


def getHeadersFromSipMsgs(xml_file, header):
    headersBySipMessage = {}
    root = openXML(xml_file)
    # Find the "send" element
    for send in root.iter("send"):
        send.text = LE.CDATA(send.text)
        cdata_element = send.text
        logging.info(cdata_element)
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

    pprint.pprint(headersBySipMessage)
    return headersBySipMessage




# Modify Header in xml
def modifyHeaderScript(xml_file, sipMessage, header, newHeader):
    logging.info(xml_file + sipMessage + header + newHeader)
    xml_file_noExt = xml_file.rsplit(".", 1)[0]
    new_xml_file = os.path.join(baseDir, 'kSipP', 'xml', f'{xml_file_noExt}_modified.xml')
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
                        logging.info("modified" + sipMessage + (cdata_lines[i]))

                        # Join the modified lines back into CDATA content
                        modified_cdata_text = "\n".join(cdata_lines)
                        send.text = None
                        send.text=(LE.CDATA("\n\n" + leading_whitespace + modified_cdata_text + "\n\n"))
                        logging.info(modified_cdata_text)                        
                        
                        # LE.tostring(send, pretty_print=True).decode()
                        with open(new_xml_file, "wb") as f:
                            f.write(LE.tostring(root, encoding="utf-8", xml_declaration=True))
                            
                        break

       


    # #PrettyXml
    # with open(new_xml_file, 'r') as file:
    #     xml_content = file.read()

    # newLineBeforeCdata = xml_content.replace('<![CDATA[', '\n    <![CDATA[')
    # newLineAfterCdata = newLineBeforeCdata.replace(']]>', '    ]]>')
    # modifiedXML = newLineAfterCdata.replace('</send>', '\n  </send>')
    # # Write the modified XML content back to the same file
    # with open(new_xml_file, 'w') as file:
    #     file.write(modifiedXML)


#Modify Header 
# xml_file_path = os.path.join(baseDir, 'kSipP', 'xml', 'UAC_orig.xml')
# new_xml_file = os.path.join(baseDir, 'kSipP', 'xml','UAC.xml')
# header = "From"
# newHeader = "kiran <sip:123@10.122.217.27:5060>"
# modifyHeader(xml_file_path, header, newHeader)


# #PrettyXml
# with open(xml_file_path, 'r') as file:
#     xml_content = file.read()

# newLineBeforeCdata = xml_content.replace('<![CDATA[', '\n\n    <![CDATA[')
# newLineAfterCdata = newLineBeforeCdata.replace(']]>', '    ]]>')
# modifiedXML = newLineAfterCdata.replace('</send>', '\n\n  </send>')
# # Write the modified XML content back to the same file
# with open(new_xml_file, 'w') as file:
#     file.write(modifiedXML)


