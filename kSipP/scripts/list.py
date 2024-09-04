import os

def listXmlFiles(directory):
    try:
        uac_files = []
        uas_files = []
        
        files = [file for file in os.listdir(directory)]
        
        for file in files:
            if file.startswith('uac'):
                uac_files.append(file)
            elif file.startswith('uas'):
                uas_files.append(file)
        
        # Sort the lists of files
        uac_files.sort()
        uas_files.sort()
        
        return uac_files, uas_files
    except FileNotFoundError:
        return "Directory not found.", "Directory not found."

