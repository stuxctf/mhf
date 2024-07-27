import os
import sys
import time
import io
from lib.Args import ArgsParse
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
from tabulate import tabulate
from lib.Colors import YELLOW, CYAN, MAGENTA, RESET, WHITE, GREEN
from contextlib import redirect_stderr

def check_root_detection(apk):
    """Check if the APK contains root detection"""
    root_detection_methods = [
        "checkForSuBinary",
        "checkForSu",
        "detectRootCloakingApps",
        "detectRootManagementApps",
        "detectTestKeys",
        "detectPotentiallyDangerousApps",
        "checkForDangerousProps",
        "checkForRWPaths",
        "checkForRootNative",
        "checkForMagiskBinary",
        "isRooted",
        "isRootedWithoutBusyBoxCheck",
        "isRootedWithoutBusyBoxAndSuBinaryCheck",
        "areDangerousPropsPresent",
        "areRootCloakingAppsPresent",
        "areRootManagementAppsPresent",
        "areTestKeysPresent",
        "arePotentiallyDangerousAppsPresent",
        "isSelinuxPermissive",
        "isSelinuxFlagInEnabledPermissive"
    ]

    detected_root_methods = []

    for dex in apk.get_all_dex():
        dvm = DalvikVMFormat(dex)
        if dvm:
            for method in root_detection_methods:
                for m in dvm.get_methods():
                    if method.lower() in str(m.get_name()).lower() and method not in detected_root_methods:
                        detected_root_methods.append(method)

    return detected_root_methods

def check_emulator_detection(apk):
    """Check if the APK contains emulator detection"""
    emulator_detection_strings = [
        "sdk_google_phone_x86",
        "google_sdk",
        "emulator",
        "goldfish",
        "virtualbox",
        "vbox",
        "google/sdk_gphone_",
        "release-keys",
        "sdk_gphone",
        "generic",
        "unknown",
        "goldfish",
        "ranchu",
        "Emulator",
        "Android SDK built for x86",
        "Genymotion",
        "Build2",
        "sdk_google",
        "sdk",
        "sdk_x86",
        "vbox86p",
        "simulator",
    ]

    detected_emulator_strings = []

    for dex in apk.get_all_dex():
        dvm = DalvikVMFormat(dex)
        if dvm:
            for string in emulator_detection_strings:
                for m in dvm.get_strings():
                    if string.lower() in str(m).lower() and string not in detected_emulator_strings:
                        detected_emulator_strings.append(string)

    return detected_emulator_strings

def check_hooking_frameworks(apk):
    """Check if the APK detect hooking frameworks"""
    hooking_frameworks_methods = [
        "XposedBridge",
        "Frida",
        "CydiaSubstrate",
        "Substrate",
        "Dexposed",
        "ReDex",
        "MSHook",
        "MSHookFunction",
        "InlineHook",
        "Intercept",
        "ptrace",
        "PTRACE_ATTACH",
        "PTRACE_DETACH",
    ]

    detected_hooking_frameworks_methods = []

    for dex in apk.get_all_dex():
        dvm = DalvikVMFormat(dex)
        if dvm:
            for method in hooking_frameworks_methods:
                for m in dvm.get_methods():
                    if method.lower() in str(m.get_code()).lower() and method not in detected_hooking_frameworks_methods:
                        detected_hooking_frameworks_methods.append(method)

    return detected_hooking_frameworks_methods

def check_ssl_pinning(apk):
    """Check if the APK contains SSL Pinning"""
    ssl_pinning_methods = [
        'getPinnedOkHttpClient',
        'CertificateFactory',
        'TrustKit.initializeWithNetworkSecurityConfiguration',
        'CertificatePinner',      
    ]

    detected_ssl_pinning_methods = []

    for dex in apk.get_all_dex():
        dvm = DalvikVMFormat(dex)
        if dvm:
            for string in ssl_pinning_methods:
                for m in dvm.get_strings():
                    if string.lower() in str(m).lower() and string not in detected_ssl_pinning_methods:
                        detected_ssl_pinning_methods.append(string)

    return detected_ssl_pinning_methods

def check_insecure_settings(apk):
    """Check if the APK contains checks for insecure device settings"""
    insecure_settings_methods = [
        "isDebuggingEnabled",
        "isDeveloperModeEnabled",
        "hasInsecurePermissions",
    ]

    detected_insecure_settings_methods = []

    for dex in apk.get_all_dex():
        dvm = DalvikVMFormat(dex)
        if dvm:
            for method in insecure_settings_methods:
                for m in dvm.get_methods():
                    if method.lower() in str(m.get_code()).lower() and method not in detected_insecure_settings_methods:
                        detected_insecure_settings_methods.append(method)

    return detected_insecure_settings_methods

def get_protections():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"\n{current_time} {CYAN}[CHK] Getting possible security protections{RESET}")
    global args
    parse = ArgsParse()
    args=parse.getArgs()
    app = args.app_name

    app_name = args.app_name
    if not app_name.endswith('.apk'):
        print(f"{current_time} {RED}[ERR] Not a valid APK file: {app_name}")
        return

    with io.StringIO() as stderr_buffer:
        with redirect_stderr(stderr_buffer):
            try:
                apk = APK(app_name)
            except Exception as e:
                pass

    detected_root_methods = check_root_detection(apk) or ["none"]
    detected_emulator_strings = check_emulator_detection(apk) or ["none"]
    detected_hooking_frameworks_methods = check_hooking_frameworks(apk) or ["none"]
    detected_ssl_pinning_methods = check_ssl_pinning(apk) or ["none"]
    detected_insecure_settings_methods = check_insecure_settings(apk) or ["none"]

    max_len = max(
        len(detected_root_methods),
        len(detected_emulator_strings),
        len(detected_hooking_frameworks_methods),
        len(detected_ssl_pinning_methods),
        len(detected_insecure_settings_methods)
    )

    root_methods = detected_root_methods if detected_root_methods != ["none"] else ["none"]
    emulator_strings = detected_emulator_strings if detected_emulator_strings != ["none"] else ["none"]
    hooking_methods = detected_hooking_frameworks_methods if detected_hooking_frameworks_methods != ["none"] else ["none"]
    ssl_pinning_methods = detected_ssl_pinning_methods if detected_ssl_pinning_methods != ["none"] else ["none"]
    insecure_settings_methods = detected_insecure_settings_methods if detected_insecure_settings_methods != ["none"] else ["none"]

    table = []
    for i in range(max_len):
        table.append([
            root_methods[i] if i < len(root_methods) else "",
            emulator_strings[i] if i < len(emulator_strings) else "",
            hooking_methods[i] if i < len(hooking_methods) else "",
            ssl_pinning_methods[i] if i < len(ssl_pinning_methods) else "",
            insecure_settings_methods[i] if i < len(insecure_settings_methods) else ""
        ])

    print(tabulate(table, headers=["Root Detection", "Emulator Detection", "Hooking Frameworks", "SSL Pinning", "Insecure Settings"], tablefmt="fancy_grid"))

