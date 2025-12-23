class FrameWork:
    REACT_NATIVE = "React Native"
    REACT_NATIVE_IOS = "React Native iOS"
    CORDOVA = "Cordova"
    FLUTTER = "Flutter"
    FLUTTER_IOS = "Flutter iOS"
    XAMARIN = "Xamarin"
    XAMARIN_IOS = "Xamarin iOS"
    NATIVESCRIPT = "NativeScript"
    NATIVE = "Native (Java/Kotlin)"
    NATIVE_IOS = "Native (Objective-C/Swift)"
    XAMARIN_BLOB = "Xamarin "
    XAMARIN_BLOB_SO =  "Xamarin  "


class Technology:
    def __init__(self, framework, directories):
        self.framework = framework
        self.directories = directories


tech_list = [
    Technology(
        framework=FrameWork.REACT_NATIVE,
        directories=[
            "libreactnativejni.so",
            "index.android.bundle",
        ]
    ),
    Technology(
        framework=FrameWork.REACT_NATIVE_IOS,
        directories=[
            "main.jsbundle",
        ]
    ),    
    Technology(
        framework=FrameWork.CORDOVA,
        directories=[
            "index.html",
            "cordova.js",
            "cordova_plugins.js"
        ]
    ),
    Technology(
        framework=FrameWork.FLUTTER,
        directories=[
            "libflutter.so"
        ]
    ),
    Technology(
        framework=FrameWork.FLUTTER_IOS,
        directories=[
            "Flutter.framework/Flutter"
        ]
    ),
    Technology(
        framework=FrameWork.XAMARIN,
        directories=[
            "Mono.Android.dll",
            "libmonodroid.so",
            "libmonosgen-2.0.so",
        ]
    ),
    Technology(
        framework=FrameWork.XAMARIN_BLOB,
        directories=[
            "assemblies.blob",
            "assemblies.manifest",
        ]
    ),
    Technology(
        framework=FrameWork.XAMARIN_BLOB_SO,
        directories=[
            "libassemblie1s.arm64-v8a.blob.so",
            "libassemblies.armeabi-v7a.blob.so",
            "libassemblies.x86.blob.so",
            "libassemblies.x86_64.blob.so",
            "libxamarin-app.so",
        ]
    ),
    Technology(
        framework=FrameWork.XAMARIN_IOS,
        directories=[
            "Xamarin.iOS.dll",
        ]
    ),
    Technology(
        framework=FrameWork.NATIVESCRIPT,
        directories=[
            "libNativeScript.so",
            "bundle.js",
            "runtime.js",
            "vendor.js",
        ]
    ),
]