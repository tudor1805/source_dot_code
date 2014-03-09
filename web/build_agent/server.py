#!/usr/bin/python

import subprocess
import pickle
import inspect
import asyncore, socket
import time
import os
from os import stat, chmod

import common
import supervisor

# Debug
from pprint import pprint

from threading import Thread
from subprocess import Popen, PIPE
import signal

AGENT_HOST = '127.0.0.1'
AGENT_PORT = 54321

from shutil import copyfile
from stat import *

class Job:
    # Variables
    code_submit   = ''
    submit_result = ''
    job_root_dir  = 'builds'
    job_dir       = ''
    job_process   = ''
    job_done      = False

    def save_file(self):
        # Create job folder
        dir = os.path.dirname(self.job_dir)
        if not os.path.exists(self.job_dir):
           os.makedirs(self.job_dir)

        # Write file to disk
        file_path = self.job_dir + '/' + self.code_submit.file_name
        print  "[ Saving file: " + file_path + " ]"

        file = open(file_path, "w")
        file.write(self.code_submit.file_data)
        file.close()

    def execute_Python(self):
         self.job_done = False
         warnings = ''

         file_name = self.code_submit.file_name

         print "[ Executing Program " + file_name + " ]"
         self.job_process = subprocess.Popen(["./supervisor.py", "python", file_name], stdout=PIPE, stderr=PIPE)
         stdout, stderr = self.job_process.communicate()
         self.submit_result = common.SubmitResult(warnings, "0" , stdout)
         self.job_done = True
         print "[ Executing Done ]" 

    def execute_CPP(self):
         self.job_done = False
         warnings = ''
         try:
             file_name = self.code_submit.file_name
             exe_file  = file_name + ".exe"

             # Compile the program
             print "[ Compiling Program " + exe_file + " ]"
             warnings = subprocess.check_output(["g++", file_name,
                                                 "-o", exe_file],
                                                 stderr=subprocess.STDOUT)

         except subprocess.CalledProcessError as ex:
             print "Compilation failed"
             print "==========="
             print ex.output
             print "==========="
             warnings = ex.output
             self.submit_result = common.SubmitResult(warnings, str(ex), '')
             self.job_done = True
             return

         print "[ Executing Program " + exe_file + " ]"
         self.job_process = subprocess.Popen(["./supervisor.py", exe_file], stdout=PIPE, stderr=PIPE)
         #self.job_process = subprocess.Popen(["./" + exe_file], stdout=PIPE, stderr=PIPE)
         stdout, stderr = self.job_process.communicate()
         self.submit_result = common.SubmitResult(warnings, "0" , stdout)
         self.job_done = True
         print "[ Executing Done ]" 

    def execute_C(self):
         self.job_done = False
         warnings = ''
         try:
             file_name = self.code_submit.file_name
             exe_file  = file_name + ".exe"

             # Compile the program
             print "[ Compiling Program " + exe_file + " ]"
             warnings = subprocess.check_output(["gcc", file_name,
                                                 "-o", exe_file],
                                                 stderr=subprocess.STDOUT)

         except subprocess.CalledProcessError as ex:
             print "Compilation failed"
             print "==========="
             print ex.output
             print "==========="
             warnings = ex.output
             self.submit_result = common.SubmitResult(warnings, str(ex), '')
             self.job_done = True
             return

         print "[ Executing Program " + exe_file + " ]"
         self.job_process = subprocess.Popen(["./supervisor.py", exe_file], stdout=PIPE, stderr=PIPE)
         stdout, stderr = self.job_process.communicate()
         self.submit_result = common.SubmitResult(warnings, "0" , stdout)
         self.job_done = True
         print "[ Executing Done ]" 

    def execute_program(self):
         os.system("chmod +x supervisor.py") 
         if   self.code_submit.prog_language == "C":
            thread = Thread(target = self.execute_C)
            thread.start()
         elif self.code_submit.prog_language == "C++":
            thread = Thread(target = self.execute_CPP)
            thread.start()
         elif self.code_submit.prog_language == "Python":
            thread = Thread(target = self.execute_Python)
            thread.start()

         # Wait for the job to finish, or terminate it
         # if it exceeds a timeout
         sec_elapsed = 0
         timeout = 5
         start = time.time()
         print "Waiting for job to complete"
         while 1:
             end = time.time()
             if end - start > 1:
                 sec_elapsed += 1
                 start = end
                 print str(sec_elapsed) + " seconds elapsed"
                 if (sec_elapsed > 10):
                     print "Attempting to kill process"
                     os.kill(self.job_process.pid, signal.SIGKILL)
                     self.submit_result = common.SubmitResult('', '0', "Timeout")
                     break
                 if self.job_done:
                     break

    def process(self):
         # Save the job file
         file_path = self.job_dir + '/' + self.code_submit.file_name
         self.save_file()

         # Go into the build directory
         cwd = os.getcwd()
         copyfile('supervisor.py', self.job_dir + '/supervisor.py')
         os.chdir(self.job_dir)
         self.execute_program()
         os.chdir(cwd)
         # Job is Done

    def __init__(self, code_submit):
        # Set the job directory
        self.job_dir     = self.job_root_dir + '/' + code_submit.file_name + "_" + str(time.time())
        self.code_submit = code_submit

# Asynchronous server
class Server(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        print "[ Started ]"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        print "[ Created Socket ]"
        self.bind((host, port))
        print "[ Bind Successfully ]"
        self.listen(1)
        print "[ Listening ]"

    def handle_accept(self):
        socket, address = self.accept()
        print 'Connection by', address
        AgentHandler(socket)

class AgentHandler(asyncore.dispatcher_with_send):

    def full_read(self):
        buff = ''
        try:
             while 1:
                  data = self.recv(1024)
                  buff = buff + data
                  if not data:
                      break
        except:
             pass
        return buff

    def handle_cmd(self):
        try:
             # Read and de-serialize Submit object
             buff = self.full_read()

             print "====== Received ======"
             #submit = pickle.loads(buff, fix_imports=True)
             submit = pickle.loads(buff)
             print "====== Unpickled ======"

             # Process Job 
             job = Job(submit)
             job.process()

             # Return Answer
             result = pickle.dumps(job.submit_result)

             print "====== Send ======" 
             self.sendall(result)
             self.close()
        except pickle.UnpicklingError:
             self.close()
             print "Unpickle error"

    def handle_read(self):
        # Parse Command
        self.handle_cmd()

################### BEGIN ###################

Server(AGENT_HOST, AGENT_PORT)
asyncore.loop()

