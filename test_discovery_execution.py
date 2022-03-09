import os, fnmatch
import sys, inspect
import hashlib
import json
import importlib
import time
import subprocess
from subprocess import call
import unittest
from unittest import TestLoader
import yaml

test_dir = None

test_discovery = { 
    "testCases" : {},
    "testSuites": {}
}
test_execution = {
    "testCases" : {},
    "testSuites" : {}
}
test_discovery_json = ""
test_execution_json = ""

testCasesDisc = []
testSuitesDisc = []
testCasesExec = []
testSuitesExec = []
testSuiteMap = {}

class CallPy(object):  #for calling other files
    def __init__(self, path):
        self.path=path
    
    def call_python_file(self):
        start_time = time.time()
        call(self.path)
        total_time = (time.time() - start_time)
        return total_time 

def getHash(file): #evaluates hash of a python file
    return hashlib.sha256(str(file).encode('utf-8')).hexdigest()

def run_case(path):
    c = CallPy(path)
    return c.call_python_file()

def get_logs(cmd):
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr

def get_file(cls):
    return "%s.py" % (cls.__module__)

def get_class(cls):
    return "%s" % (cls.__qualname__)

def test_discovery_function(suite):
    if (isinstance(suite,unittest.TestCase)):
        file_name = get_file(suite.__class__)
        class_name = get_class(suite.__class__)
        test_name =  suite._testMethodName
        func_path = '.'.join([class_name,test_name])
        locator = func_path
        file = {
                "id": getHash(locator),
                "label": locator,
                "file": os.path.join(test_dir,file_name),
                "test-suites": class_name
            }
        suite = {
                "id": getHash(class_name),
                "label": class_name,
                "file": os.path.join(test_dir,file_name)
            }
        # print(file)
        if testSuiteMap.get(suite['id']) == None:
            testSuiteMap[suite['id']] = 1
            testSuitesDisc.append(suite)
        else:
            testSuiteMap[suite['id']] = testSuiteMap.get(suite['id']) + 1
        testCasesDisc.append(file)
        # print(type(suite))
        # cases.append(suite)
        return
    elif (isinstance(suite, unittest.TestSuite)):
        for x in suite:
            test_discovery_function(x)
    
def test_execution_function():
    for testCase in test_discovery['testCases']: # for test Cases
        os.system('export PYTHONPATH=$PWD')
        execute = ['python3'] + [testCase['file']] + [testCase['label']]
        # print(execute)
        exit_code, output, logs = get_logs(execute)
        # print(exit_code, logs)
        time_taken = run_case(execute)
        file = {
                "id": testCase['id'],
                "label": testCase['label'],
                "file": testCase['file'],
                "status": "passed" if exit_code==0 else "failed",
                "duration": time_taken,
                "failureMsg": logs.decode('utf-8') if exit_code==1 else "NA"
            }
        testCasesExec.append(file)
    # test_execution["testCases"]=testCasesExec

    for testSuite in test_discovery['testSuites']: # for test Suites
        os.system('export PYTHONPATH=$PWD')
        execute = ['python3'] + [testSuite['file']] + [testSuite['label']]
        exit_code, output, logs = get_logs(execute)
        time_taken = run_case(execute)
        file = {
                "id": testSuite['id'],
                "label": testSuite['label'],
                "file": testSuite['file'],
                "status": "passed" if exit_code==0 else "failed",
                "duration-ns": time_taken,
                "numTests": testSuiteMap.get(testSuite['id']),
                "failureMsg": logs.decode('utf-8') if exit_code==1 else "NA"
            }
        testSuitesExec.append(file)
    # test_execution["testSuites"]=testSuitesExec
    
def init_dir_and_pattern(data):
    curr_dir=data[0]
    pattern=data[1]
    return curr_dir,pattern

def start_discovery(pattern):
    gen_suite = TestLoader().discover(test_dir, pattern)  #Check for test* too
    test_discovery_function(gen_suite) 
    test_discovery["testCases"] = testCasesDisc
    test_discovery["testSuites"] = testSuitesDisc
    test_discovery_json = json.dumps(test_discovery, indent=2)
    # print(test_discovery_json) # Final test discovery json
    f = open('output_discovery.txt','w')
    print(test_discovery_json, file=f) # Python 3.x
    
def start_execution():
    test_execution_function()
    test_execution["testCases"] =  testCasesExec
    test_execution["testSuites"] = testSuitesExec
    test_execution_json = json.dumps(test_execution, indent=2)
    f = open('output_execution.txt','w')
    print(test_execution_json, file=f) # Python 3.x
    # print(test_execution_json) # final test execution json

def get_parsed_yaml_file(file):
    tas_yaml_file = open(file)
    parsed_yaml_file = yaml.load(tas_yaml_file, Loader=yaml.FullLoader)
    return parsed_yaml_file

if __name__ == "__main__":
    tas_yaml_file = get_parsed_yaml_file("input.yaml")
    for file in tas_yaml_file["inputs"]:
        test_dir = file['start_dir']
        pattern = file['pattern']
        start_discovery(pattern)
    start_execution()
    

