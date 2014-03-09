import common
import socket
import pickle
from pprint import pprint

AGENT_HOST = '127.0.0.1'  # The remote host
PORT = 54321              # The same port as used by the server

class SubmitClient:
    # Variables
    socket = ''
    submit = ''
    result = ''

    def full_read(self):
        buff = ''
        try:
             while 1:
                  data = self.socket.recv(1024)
                  buff = buff + data
                  if not data:
                      break
        except:
             pass
        return buff

    def __init__(self, host, port, submit):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self.submit = submit
        self.send_file()

    def send_file(self):
        # Send Submit Code
        serial_repres = pickle.dumps(self.submit)
        self.socket.sendall(serial_repres)

        # Wait for Answer
        answ = self.full_read()
        self.result = pickle.loads(answ)
        self.socket.close()

############## Tester  ############## 

class ClientTester:
    def load_file(file_name):
        file = open(file_name, "rb")
        file_data = file.read()
        file.close()
        return file_data

    def __init__(self):
        file_name='hello.c'
        prog_language="C"
        codeSubmit = common.CodeSubmit(file_name, load_file(file_name), prog_language)
        SubmitClient(AGENT_HOST, PORT, codeSubmit)
