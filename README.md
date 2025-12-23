# Mobile Helper Framework

is a tool that automates the process of identifying the framework/technology used to create a mobile application. Additionally, it assists in finding sensitive information or provides suggestions for working with the identified platform.

## How work?

The tool searches for files associated with the technologies used in mobile application development, such as configuration files, resource files, and source code files.

## Example

### Cordova

Search files:

```
index.html
cordova.js
cordova_plugins.js
```
### React Native Android & iOS

Search file

```
Andorid files:

libreactnativejni.so
index.android.bundle

iOS files:

main.jsbundle
```

## Installation

❗A minimum of Java 8 is required to run Apktool. 

`pip install -r requirements.txt`

## Usage

`python3 mhf.py app.apk|ipa|aab`

### Examples

```
python3 mobile_helper_framework.py file.apk

[+] App was written in React Native

Do you want analizy the application (y/n) y

Output directory already exists. Skipping decompilation.

Beauty the react code? (y/n) n

Search any info? (y/n) y

==>>Searching possible internal IPs in the file

results.........

==>>Searching possible emails in the file

results.........

==>>Searching possible interesting words in the file

results.........

==>>Searching Private Keys in the file

results.........

==>>Searching high confidential secrets

results.........

==>>Searching possible sensitive URLs in js files

results.........

==>>Searching possible endpoints in js files results.........
```

## Features

This tool uses Apktool for decompilation of Android applications.

This tool renames the .ipa file of iOS applications to .zip and extracts the contents. 

| Feature | Note | Cordova | React Native | Native JavaScript | Flutter | Xamarin
| :---: | --- | ---: | ---: | ---: | ---: | ---: |
| JavaScript beautifier | Use this for the first few occasions to see better results. | ✅ | ✅ | ✅ | 
| Identifying multiple sensitive information | IPs, Private Keys, API Keys, Emails, URLs | ✅ | ✅ | ✅ | ❌
| Cryptographic Functions |  | ✅ | ✅ | ✅ | ❌| ❌ | ❌ |
| Endpoint extractor | | ✅ | ✅ | ✅ | ❌ | ❌
| Automatically detects if the  code has been beautified. | | ❌ | ❌ | ❌ |
| Extracts automatically apk of devices/emulator | | ❌ | ❌ | ❌ | ❌ | ❌ | 
| Patching apk | |  |  |  | ✅ |  
| Extract an APK from a bundle file.|  | ✅ |✅ |✅ |✅ |✅ |
| Detect if JS files are encrypted | | ❌ |  | ❌ 
| Detect if the resources are compressed. | | ❌ | Hermes✅| ❌ | ❌ | XALZ✅
| Detect if the app is split | | ❌ | ❌ | ❌ | ❌ | ❌ | 

`What is patching apk:` This tool uses Reflutter, a framework that assists with reverse engineering of Flutter apps using a patched version of the Flutter library.

More information: https://github.com/Impact-I/reFlutter
<hr/>

`Split APKs` is a technique used by Android to reduce the size of an application and allow users to download and use only the necessary parts of the application.

Instead of downloading a complete application in a single APK file, Split APKs divide the application into several smaller APK files, each of which contains only a part of the application such as resources, code libraries, assets, and configuration files.

```
adb shell pm path com.package
package:/data/app/com.package-NW8ZbgI5VPzvSZ1NgMa4CQ==/base.apk
package:/data/app/com.package-NW8ZbgI5VPzvSZ1NgMa4CQ==/split_config.arm64_v8a.apk
package:/data/app/com.package-NW8ZbgI5VPzvSZ1NgMa4CQ==/split_config.en.apk
package:/data/app/com.package-NW8ZbgI5VPzvSZ1NgMa4CQ==/split_config.xxhdpi.apk
```
For example, in Flutter if the application is a Split it's necessary patch split_config.arm64_v8a.apk, this file contains libflutter.so 


## Credits

- This tool use a secrets-patterns-db repositorty created by [mazen160](https://github.com/mazen160/secrets-patterns-db)
- This tool use a regular expresion created by [Gerben_Javado](https://github.com/mazen160/https://github.com/GerbenJavado/LinkFinder/blob/master/linkfinder.py) for extract endpoints
- This tools use reflutter for flutter actions 

## Changelog

### 0.7 (Christmas Release)

- Improved Flutter detection with deeper Dart analysis.
- Support for the new .dll compression used in .NET MAUI 9 for Android applications

### 0.6 (Dojoconfpa Release)

- Bug fixes
- Get App information
- APKiD integration for identify (compilers, packers, obfuscators) - (experimental)
- Possible identification of protections (root, sslpinning, Emulator, Hooking) - BETA
- Extract dangerous permissions - (experimental)
- Extract deeplinks information - (experimental)
- Extract browseable components - (experimental)

### 0.5

- Public release
- Bug fixes

### 0.4

- Added plugins information in Cordova apps
- Added Xamarin actions
- Added NativeScript actions
- Bug fixes

### 0.3
- Added NativeScript app detection
- Added signing option when the apk extracted of aab file is not signed

### 0.2
- Fixed issues with commands on Linux.

### 0.1
- Initial version release.

## License

- This work is licensed under a Creative Commons Attribution 4.0 International License.

## Autors

[Cesar Calderon](https://twitter.com/__stux)
[Marco Almaguer](https://websec.mx/)
