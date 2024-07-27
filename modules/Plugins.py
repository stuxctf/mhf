import os
import json
import re
import time
import sys
import tempfile
from modules.Extract import extract_apk, extract_ipa
from lib.Colors import RED, CYAN, RESET


ipatmp = ""
androtmp = ""
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

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
    stdout_orig = sys.stdout
    stderr_orig = sys.stderr
    sys.stdout = tempfile.TemporaryFile(mode='w+')
    sys.stderr = sys.stdout

    try:
        extracted = extract_apk(androtmp) or extract_ipa(ipatmp)
    except Exception:
        extracted = None
    
    sys.stdout = stdout_orig
    sys.stderr = stderr_orig

    if extracted is not None:
        for root, dirs, files in os.walk(extracted):
            if "cordova_plugins.js" in files:
                file_path = os.path.join(root, "cordova_plugins.js")
                return file_path
    return None

def get_plugins_info():
    js_path = search_jspath(androtmp, ipatmp) 
    plugins_info = extract_plugins_info(js_path)

    if plugins_info:
        print(f"\n{current_time} {CYAN}[CHK] Obtaining plugin details from the application\n {RESET}")
        print("{:<40} {:<20}".format("Plugin Name", "Version"))
        print("-" * 60)
        for plugin_name, version in plugins_info.items():
            print("{:<40} {:<20}".format(plugin_name, version))
    else:
        print(f"\n{current_time} {RED}[ERR] No plugin information found in the file {RESET}")
