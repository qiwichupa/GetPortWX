import os
import yaml

class YamlConfig():
    def __init__(self, configfile):
        self.configfile = configfile
        # check|create dir
        try:
            os.makedirs(os.path.dirname(self.configfile),exist_ok=True)
        except Exception as e:
            print(e)
        # check|create file
        try:
            with open(self.configfile) as f:
                self.settings = yaml.load(f, Loader=yaml.FullLoader)
        except:
            with open(self.configfile, 'w') as f:
                f.write('')

    def __readconf__(self):
        with open(self.configfile) as f:
            self.settings = yaml.load(f, Loader=yaml.FullLoader)
        if type(self.settings) is not dict:
            self.settings = {}

    def value(self, option):
        self.__readconf__()
        try:
            type(self.settings[option])
        except:
            return(None)
        else:
            return (self.settings[option])

    def setValue(self, option, value):
        self.__readconf__()
        self.settings[option] = value
        with open(self.configfile, 'w') as f:
            self.settings = yaml.dump(self.settings, stream=f,
                               default_flow_style=False, sort_keys=False, allow_unicode=True)