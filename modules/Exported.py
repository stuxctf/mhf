import os
import time
import sys
import tempfile
from xml.etree import ElementTree as ET
from tabulate import tabulate
from .Extract import extract_apk
from lib.Colors import RED, RESET

androtmp = ""
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_exported_components(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    
    activities = []
    services = []
    receivers = []
    providers = []

    for elem in root.iter():
        if 'activity' in elem.tag:
            if elem.attrib.get('{http://schemas.android.com/apk/res/android}exported') == 'true':
                activities.append(elem.attrib['{http://schemas.android.com/apk/res/android}name'])
        elif 'service' in elem.tag:
            if elem.attrib.get('{http://schemas.android.com/apk/res/android}exported') == 'true':
                services.append(elem.attrib['{http://schemas.android.com/apk/res/android}name'])
        elif 'receiver' in elem.tag:
            if elem.attrib.get('{http://schemas.android.com/apk/res/android}exported') == 'true':
                receivers.append(elem.attrib['{http://schemas.android.com/apk/res/android}name'])
        elif 'provider' in elem.tag:
            if elem.attrib.get('{http://schemas.android.com/apk/res/android}exported') == 'true':
                providers.append(elem.attrib['{http://schemas.android.com/apk/res/android}name'])

    return activities, services, receivers, providers

def search_manifest_path(androtmp):
    stdout_orig = sys.stdout
    stderr_orig = sys.stderr
    sys.stdout = tempfile.TemporaryFile(mode='w+')
    sys.stderr = sys.stdout

    try:
        extracted = extract_apk(androtmp)
    except Exception:
        extracted = None

    sys.stdout = stdout_orig
    sys.stderr = stderr_orig

    if extracted is not None:
        for root, dirs, files in os.walk(extracted):
            if "AndroidManifest.xml" in files:
                file_path = os.path.join(root, "AndroidManifest.xml")
                return file_path
    return None

def display_exported_components():
    manifest_path = search_manifest_path(androtmp)
    if os.path.exists(manifest_path) and manifest_path.endswith("AndroidManifest.xml"):
        activities, services, receivers, providers = get_exported_components(manifest_path)
        
        def create_table(title, items):
            headers = [title]
            table = [[item] for item in items] if items else [["None"]]
            return tabulate(table, headers=headers, tablefmt="fancy_grid")
        
        print(create_table("Exported Activities", activities))
        print(create_table("Exported Services", services))
        print(create_table("Exported Receivers", receivers))
        print(create_table("Exported Providers", providers))
    else:
        print(f"\n{current_time} [ERR] No valid AndroidManifest.xml file found for analysis")

if __name__ == "__main__":
    display_exported_components()