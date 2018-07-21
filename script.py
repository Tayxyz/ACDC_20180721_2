import re,json

class script():
    def __init__(self,script_name):
        json_str = ''
        with open(script_name) as f:
            for line in f:
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                else:
                    json_str = json_str + line  # read script
        # print repr(json_str)
        self.script_obj = json.loads(json_str, strict=False) # string to dict

    def get_all(self):
        return self.script_obj

    def get_initial(self):
        return self.script_obj['initial']

    def get_locks(self):
        try:
            return self.script_obj['locks']
        except:
            return []

    def get_barriers(self):
        try:
            return self.script_obj['barriers']
        except:
            return []

    def get_monopoly(self):
        try:
            return self.script_obj['monopoly']
        except:
            return []

    def get_process(self):
        return self.script_obj['process']