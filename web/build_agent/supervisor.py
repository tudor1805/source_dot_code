#!/usr/bin/python
#
# Supervisor based on python-ptrace package
#

from ptrace.debugger.debugger import PtraceDebugger
from ptrace.debugger import (ProcessExit, ProcessSignal, NewProcessEvent, ProcessExecution)
from ptrace.func_call import FunctionCallOptions
from ptrace.ctypes_tools import formatAddress
from ptrace.debugger.child import createChild
from ptrace.tools import locateProgram
from sys import stderr, argv, exit
from pprint import pprint
 
syscall_options = FunctionCallOptions(
    write_types=True,
    write_argname=True,
    string_max_length=8192,
    replace_socketcall=False,
    write_address=True,
    max_array_count=100,
)
 
def usage():
    print >>stderr, "usage: %s program [arg1 arg2 ...]" % argv[0]
    exit(1)

def get_syscall_name(process):
    state = process.syscall_state
    syscall = state.event(syscall_options)
    return syscall.name
 
def get_syscall_str(process):
    state = process.syscall_state
    syscall = state.event(syscall_options)
    if syscall and (syscall.result is not None):
        name = syscall.name
        text = syscall.format()
        prefix = []
        prefix.append("[%s]" % process.pid)
        text = ''.join(prefix) + ' ' + text
        return text
    else:
        return ""

def syscall_is_forbidden(process):
    forbidden_syscalls = ["socket", "socketcall", "reboot", "kill", "chdir", "pipe", "clone"]
    str = get_syscall_name(process)
    if str in forbidden_syscalls:
        return True
    return False
 
def loop(debugger):
    while True:
        try:
            event = debugger.waitSyscall()
        except ProcessExit, event:
            state = event.process.syscall_state
            if (state.next_event == "exit") and state.syscall:
                # print("[%d] exit() : exit process" % event.process.pid)
                debugger.deleteProcess(pid=event.process.pid)
            continue
        except ProcessSignal, event:
            # print("*** SIGNAL pid=%s ***" % event.process.pid)
            event.display()
            event.process.syscall(event.signum)
            continue
        except NewProcessEvent, event:
            # print("*** New process %s ***" % event.process.pid)
            event.process.syscall()
            continue
        except ProcessExecution, event:
            # print("*** Process %s execution ***" % event.process.pid)
            event.process.syscall()
            continue
        except:
            #print("all target processes finished...")
            return
        process = event.process

        # get syscall string
        #str = get_syscall_str(process)
        #str = get_syscall_name(process)
        #if len(str) > 0:
        #   print(str)

        #print "Syscall: " + get_syscall_name(process) + " executed "
        # prevent systemcall?
        if syscall_is_forbidden(process):
            print "Syscall: " + get_syscall_name(process) + " is forbidden!"
            #print "Syscall: " + get_syscall_str(process) + " is forbidden!"
            process.terminate(False)
            debugger.deleteProcess(pid=process.pid)
            continue
        else: 
            process.syscall()

def main():
    if len(argv) < 2: usage()
 
    # create process
    env = None
    arguments = argv[1:]
    arguments[0] = locateProgram(arguments[0])
    pid = createChild(arguments, False, env)
 
    # create debugger
    debugger = PtraceDebugger()
    debugger.enableSysgood()
    debugger.traceExec()
    debugger.traceFork()
 
    # attach process
    debugger.addProcess(pid, True)
    process = debugger[pid]
    process.syscall()
 
    # start event loop
    loop(debugger)
 
    debugger.quit()
 
if __name__ == "__main__":
    main()
