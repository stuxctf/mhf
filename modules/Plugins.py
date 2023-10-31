import os
import json
import re
from modules.Extract import extract_apk, extract_ipa
from lib.Colors import RED, CYAN, RESET

ipatmp = ""
androtmp = ""

def extract_plugins_info(js_path):
    if not js_path is None:
        with open(js_path, "r", encoding="utf-8") as js_file:
            js_content = js_file.read()
        plugin_pattern = r'module\.exports\.metadata\s*=\s*{([^}]+)}'
        match = re.search(plugin_pattern, js_content, re.DOTALL)

        if match:
            metadata_section = match.group(1)
            metadata_dict = json.loads("{" + metadata_section + "}")
            return metadata_dict
    return None


def search_jspath(androtmp, ipatmp):
    extracted = extract_apk(androtmp) or extract_ipa(ipatmp)
    for root, dirs, files in os.walk(extracted):
        if "cordova_plugins.js" in files:
            file_path = os.path.join(root, "cordova_plugins.js")
            return file_path
    return None

def get_plugins_info():
    js_path = search_jspath(androtmp, ipatmp) 
    plugins_info = extract_plugins_info(js_path)

    if plugins_info:
        print(f"{CYAN}\n==>>Obtaining plugin details from the application\n {RESET}")
        print("{:<40} {:<20}".format("Plugin Name", "Version"))
        print("-" * 60)
        for plugin_name, version in plugins_info.items():
            print("{:<40} {:<20}".format(plugin_name, version))
    else:
        print(f"{RED} No plugin information found in the file {RESET}")