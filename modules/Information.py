import os
from androguard.core.bytecodes.apk import APK
from tabulate import tabulate
from contextlib import redirect_stderr
from lib.Args import ArgsParse

def extract_apk_info(apk_path):
    try:
        with open(os.devnull, 'w') as devnull, redirect_stderr(devnull):
            apk = APK(apk_path)
        
        app_name = apk.get_app_name()
        package_name = apk.get_package()
        main_activity = apk.get_main_activity()
        target_sdk = apk.get_target_sdk_version()
        min_sdk = apk.get_min_sdk_version()
        max_sdk = apk.get_max_sdk_version()
        version_name = apk.get_androidversion_name()
        version_code = apk.get_androidversion_code()

        data = [
            ["App Name", app_name],
            ["Package Name", package_name],
            ["Main Activity", main_activity],
            ["Target SDK", target_sdk],
            ["Min SDK", min_sdk],
            ["Max SDK", max_sdk],
            ["Android Version Name", version_name],
            ["Android Version Code", version_code],
        ]

        print("\n")
        print(tabulate(data, tablefmt="fancy_grid"))

    except Exception as e:
        print(f"\nError: {e}")

def get_information():
    parse = ArgsParse()
    args = parse.getArgs()
    app = args.app_name

    # Check if the provided file is an APK
    if app.endswith('.apk') or app.endswith('.APK'):
        extract_apk_info(app)

if __name__ == "__main__":
    get_information()