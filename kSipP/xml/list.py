import os

def list_files_in_directory(directory='.', exclude_file='list.py'):
    try:
        uac_files = []
        uas_files = []
        
        files = [file for file in os.listdir(directory) if file != exclude_file]
        
        for file in files:
            if file.startswith('uac'):
                uac_files.append(file)
            elif file.startswith('uas'):
                uas_files.append(file)
        
        # Sort the lists of files
        uac_files.sort()
        uas_files.sort()
        
        formatted_uac_files = "[\n" + ",\n".join(f" '{file}'" for file in uac_files) + "\n]"
        formatted_uas_files = "[\n" + ",\n".join(f" '{file}'" for file in uas_files) + "\n]"
        
        return formatted_uac_files, formatted_uas_files
    except FileNotFoundError:
        return "Directory not found.", "Directory not found."

directory_path = '.'  # Current directory
uac_list, uas_list = list_files_in_directory(directory_path)

print("const uacXmlFiles=")
print(uac_list)

print("const uasXmlFiles=")
print(uas_list)
