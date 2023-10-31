import argparse

class SingeltonArgsParse(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ArgsParse(metaclass=SingeltonArgsParse):

    def __init__(self):
        self.parser=argparse.ArgumentParser("mhf.py")
        self.parser.add_argument("app_name", help=".APK|.IPA|.AAB file to verify")
        self.args = self.parser.parse_args()

    def getArgs(self):
        return self.args