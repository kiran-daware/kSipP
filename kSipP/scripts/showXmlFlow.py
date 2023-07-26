import lxml.etree as LE
import os
import configparser
import logging

cwd = os.path.dirname(os.path.abspath(__file__))
baseDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
modifyHeaderLog = os.path.join(baseDir, 'Logs', 'modifyHeader.log')
logging.basicConfig(filename= modifyHeaderLog, filemode='w', level=logging.DEBUG)


def get_first_word_from_cdata(cdata):
    # Split the CDATA text and extract the first word
    words = cdata.split()
    if words:
        return words[0]
    return None


def showXmlFlowScript(xml_file_name):
    xml_file= os.path.join(baseDir, 'kSipP', 'xml', xml_file_name)
    with open(xml_file, "r") as f:
        xml_data = f.read()

    # Parse the XML file
    # logging.info("XML file name is %s", xml_file)
    parser = LE.XMLParser()
    root = LE.XML(xml_data.encode(), parser)

    callflow = []
    # check flow for UAC files
    if xml_file_name.startswith('uac'):
        for element in root.iter("send","recv"):
            if element.tag == "send":
                cdata_text = element.text
                if cdata_text:
                    # Remove leading/trailing whitespaces and get the first word from CDATA
                    first_word = get_first_word_from_cdata(cdata_text.strip())
                    callflow.append(f"   {first_word}  -----send----->   ")
            
            if element.tag == "recv":
                response = element.get("response")
                if response:
                    callflow.append(f"   {response}   <-----recv-----   ")

    if xml_file_name.startswith('uas'):
        for element in root.iter('send','recv'):
            if element.tag == 'send':
                cdata_text = element.text
                cdata_lines = cdata_text.splitlines()
                if len(cdata_lines) > 0:
                    first_line = next((line.replace('SIP/2.0', '').strip() for line in cdata_lines if line.strip()), None)
                    callflow.append(f"<-----send-----   {first_line}")

            if element.tag == 'recv':
                request = element.get("request")
                if request:
                    callflow.append(f"-----recv----->   {request}")
                    
    
    return callflow



        # cdata_element = send.text
        # if cdata_element is not None:
        #     # Split the CDATA content into lines
        #     cdata_lines = cdata_element.strip().splitlines()
        #     # Find and replace the 'To:' line
        #     for i, line in enumerate(cdata_lines):
        #         if line.strip().startswith(header + ":"):
        #             leading_whitespace = line[:line.find(header + ":")]
        #             cdata_lines[i] = leading_whitespace +  header + ": " + newHeader
        #             logging.info("modified" + (cdata_lines[i]))
        #             break
        #     # Join the modified lines back into CDATA content
        #     modified_cdata_text = "\n".join(cdata_lines)
        #     send.text = None
        #     send.text=(LE.CDATA("\n\n" + leading_whitespace + modified_cdata_text + "\n\n"))
