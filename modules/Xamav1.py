import os
import re
import subprocess
import plistlib
from lxml import etree
from lib.Colors import RED, CYAN, YELLOW, WHITE, RESET
from .Extract import extract_apk, extract_ipa
from .Permissions import display_dangerous_permissions
from .Deep import display_deep_links
from .Exported import display_exported_components
from .Protections import get_protections
from .Security import get_security

ipatmp = ""
androtmp = ""
header_expected_magic = b'XALZ'
xalz_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "Xamarin_XALZ_decompress.py"))

def analyze_manifest(extracted):
    packa = ""
    for file in os.listdir(extracted):
        file_path = os.path.join(extracted, file)
        if os.path.isfile(file_path) and file == 'AndroidManifest.xml':
            tree = etree.parse(file_path)
            root = tree.getroot()
            package_name = root.attrib['package']
            last_dot_index = package_name.rfind('.')
            if last_dot_index != -1 and last_dot_index < len(package_name) - 1:
                packa = package_name[last_dot_index+1:last_dot_index+5]
    return packa

def analyze_plist(extracted):
    blunde = ""
    for root, dirs, files in os.walk(extracted):
        for file in files:
            if file == 'Info.plist':
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as infile:
                    plist = plistlib.load(infile)
                    blunde = plist.get('CFBundleDisplayName', None)
                    return blunde[:3]
    return None

def search_dll(extracted):
    dll_content = []
    file_paths = []
    for root, dirs, files in os.walk(extracted):    
        for file in files:
            if file.endswith(".dll"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        dll_content.append(f.read())
                        file_paths.append(file_path)
                except UnicodeDecodeError:
                    continue
    return dll_content, file_paths

def detect_xalz(file_path):
    with open(file_path, "rb") as dll_file:
        data = dll_file.read(4) 
        if data != header_expected_magic:
            return False
    return True

def xamabunlde(extracted):
    bundle_paths = []
    for root, dirs, files in os.walk(extracted):
        for file in files:
            if file == 'libmonodroid_bundle_app.so':
                file_path = os.path.join(root, file)
                bundle_paths.append(file_path)
    return bundle_paths

def xama_andorid():
        search = input("\nDo you want get DLL information? (Y/n): ")
        if search.lower() != "n":
            extracted = extract_apk(androtmp)
            bundle_paths = xamabunlde(extracted)
            if bundle_paths:
                print(f"{RED}\n\t[!] APK compiled in mode Bundled Build")
                print(f"{RED}\tThe package builder bundles .dll assemblies into native code, in the file: {RESET}")
                print(f"\n\tBundle path:")
                for bundle_path in bundle_paths:
                    print(f"\t{bundle_path}")
                print(f"{RED}\n\tFor extraction of the .dll assemblies use: https://github.com/cihansol/XamAsmUnZ {RESET}")
            else:
                print(f"{RED}\n\t[!] APK compiled in mode Unbundled Build")
                print(f"{RED}\tThe package builder will utilize LZ4 Compression and create files with the .dll extension {RESET}")
                content, file_paths = search_dll(extracted)
                packa = analyze_manifest(extracted)
                pattern = fr"(?i){packa}"
                print(f"{YELLOW}\n[!] To reverse engineer the DLL files, use external tools: {RESET}")
                print("\tWindows: ILSpy -> https://github.com/icsharpcode/ILSpy/releases")
                print("\tWindows: Dotpeek -> https://www.jetbrains.com/es-es/decompiler/")
                print("\tLinux/MAC: Use ILSpy extension for VSCODE -> https://github.com/icsharpcode/ILSpy/releases\n")

                display_deep_links()
                display_dangerous_permissions()
                display_exported_components()

                
                dll_files = []
                xalz_files = []
            
                for file_path, dll_file_content in zip(file_paths, content):
                    file_name = os.path.basename(file_path)
                    if re.search(pattern, file_name):
                        dll_files.append(file_path)
                    if detect_xalz(file_path):
                        xalz_files.append(file_path)
                
                print(f"{CYAN}\nPossible main dll file:\n {RESET}")
                for file_path in dll_files:
                    print(f"{file_path}")
                print(f"{CYAN}\nDLL Compresed with XALZ:\n {RESET}")
                if not xalz_files:
                    print(f"{WHITE}\tFiles not compressed with XALZ. {RESET}")        
                for file_path in xalz_files:
                    print(f"{file_path}")

                #Run Decompress Xamarin XALZ

                decom = input(f"{CYAN}\nDo you want decompress XALZ dll files (Y/n) {RESET}: ")
                if decom.lower() != "n":
                    file_dll = input("Enter the path dll file to decompress: ")
                    xalz_cmd = ["python", xalz_path, file_dll, file_dll]
                    subprocess.run(xalz_cmd)
                    print(f"Result written to file in: {file_dll}")

def xama_ios():
    search = input("\nDo you want get DLL information? (Y/n): ")
    if search.lower() != "n":
        extracted = extract_ipa(ipatmp)
        content, file_paths = search_dll(extracted)       
        cfbundle = analyze_plist(extracted)
        pattern = fr"(?i){cfbundle}"
        print(f"{YELLOW}\n[!] To reverse engineer the DLL files, use external tools: {RESET}")
        print("\tWindows: ILSpy -> https://github.com/icsharpcode/ILSpy/releases")
        print("\tWindows: Dotpeek -> https://www.jetbrains.com/es-es/decompiler/")
        print("\tLinux/MAC: Use ILSpy extension for VSCODE -> https://github.com/icsharpcode/ILSpy/releases")

        dll_files = []
        xalz_files = []
    
        for file_path, dll_file_content in zip(file_paths, content):
            file_name = os.path.basename(file_path)
            if re.search(pattern, file_name):
                dll_files.append(file_path)
            if detect_xalz(file_path):
                xalz_files.append(file_path)

        print(f"{CYAN}\nPossible main dll file:\n {RESET}")
        for file_path in dll_files:
            print(f"{file_path}")
        print(f"{CYAN}\nDLL Compresed with XALZ:\n {RESET}")
        if not xalz_files:
            print(f"{WHITE}\tFiles not compressed with XALZ. {RESET}")        
        for file_path in xalz_files:
            print(f"{file_path}")
