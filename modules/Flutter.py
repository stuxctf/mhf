import os
import subprocess
from lib.Args import ArgsParse
from lib.Colors import WHITE, RESET
signer_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "uber-apk-signer-1.2.1.jar"))

def patch_apk():
	global args
	parse = ArgsParse()
	args=parse.getArgs()
	app = args.app_name
	if app.endswith('.apk'):
		search = input("\nDo you want patch apk file with reflutter? (Y/n): ")
		if search.lower() != "n":
			reflutter_cmd = ["reflutter", app]
			subprocess.run(reflutter_cmd, shell=False)
            
			search = input("\nDo you want patch signing apk file? (y/n) ")
			if search.lower() != "n":
				signer_cmd = ["java", "-jar", signer_path , "--apk", "./release.RE.apk"]
				subprocess.run(signer_cmd, shell=False)
		else:
			print("\nLeaving...")
	else:
		print(f"{WHITE}\nPatch no supported for iOS in Windows/Linux in this tool {RESET}")