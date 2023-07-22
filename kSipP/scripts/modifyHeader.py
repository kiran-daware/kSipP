import lxml.etree as LE
import os
import configparser
import logging
cwd = os.path.dirname(os.path.abspath(__file__))
baseDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
modifyHeaderLog = os.path.join(baseDir, 'Logs', 'modifyHeader.log')
logging.basicConfig(filename= modifyHeaderLog, filemode='w', level=logging.DEBUG)

# Fetching Variables from Config File
config_file = os.path.join(baseDir, 'config.ini')
config = configparser.ConfigParser()
config.read(config_file)
configd = config['DEFAULT']


# Open SipP scenario.xml file
def openXML(xml_file):
    with open(xml_file, "r") as f:
        xml_data = f.read()

    # Parse the XML file
    logging.info("XML file name is %s", xml_file)
    parser = LE.XMLParser(strip_cdata=False)
    return(LE.XML(xml_data.encode(), parser))

# Modify Header in xml
def modifyHeader(xml_file, header, newHeader):
    root = openXML(xml_file)
    # Find the "send" element
    for send in root.iter("send"):
        send.text = LE.CDATA(send.text)
        cdata_element = send.text
        if cdata_element is not None:
            # Split the CDATA content into lines
            cdata_lines = cdata_element.strip().splitlines()
            # Find and replace the 'To:' line
            for i, line in enumerate(cdata_lines):
                if line.strip().startswith(header + ":"):
                    leading_whitespace = line[:line.find(header + ":")]
                    cdata_lines[i] = leading_whitespace +  header + ": " + newHeader
                    logging.info("modified" + (cdata_lines[i]))
                    break
            # Join the modified lines back into CDATA content
            modified_cdata_text = "\n".join(cdata_lines)
            send.text = None
            send.text=(LE.CDATA("\n\n" + leading_whitespace + modified_cdata_text + "\n\n"))

            
            # send.text = "\n<![CDATA[\n" + leading_whitespace + modified_cdata_text + "\n\n  ]]> \n" 
            LE.tostring(send, pretty_print=True).decode()
            # send.text = cdataSection
            # print(LE.tostring(send, encoding="unicode" pretty_print=True).decode())
        
        # Write the canonicalized XML back to the file
        with open(xml_file, "wb") as f:
            f.write(LE.tostring(root, encoding="utf-8", xml_declaration=True))
            # f.write(root, encoding="utf-8", xml_declaration=True)


#Modify Header 
xml_file_path = os.path.join(cwd, 'xml', 'Basic_UAC.xml')
new_xml_file = os.path.join(cwd, 'xml', 'Basic_UAC_new.xml')
header = "From"
newHeader = "kiran <sip:123@10.122.217.27:5060>"
modifyHeader(xml_file_path, header, newHeader)


#PrettyXml
with open(xml_file_path, 'r') as file:
    xml_content = file.read()

newLineBeforeCdata = xml_content.replace('<![CDATA[', '\n\n    <![CDATA[')
newLineAfterCdata = newLineBeforeCdata.replace(']]>', '    ]]>')
modifiedXML = newLineAfterCdata.replace('</send>', '\n\n  </send>')
# Write the modified XML content back to the same file
with open(new_xml_file, 'w') as file:
    file.write(modifiedXML)


