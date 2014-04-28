#!/usr/bin/env python

# multiRun.py
#
# Jens Dede, 2014
# jd@comnets.uni-bremen.de
#
# App to run jar files several times for example for a montecarlo simulation.
#
# I wrote this script to execute an exported cooja simulation (--> contiki)
# several times using multiple processor cores.
#

import argparse
import threading
import Queue
import subprocess
import datetime
import os
import sys
import shutil
import time

class executeThread(threading.Thread):
    ## \brief Worker thread
    #
    # Execute jar file in separate thread.

    commands = Queue.Queue()
    printLock = threading.Lock()

    breakSimulationLock = threading.Lock()
    breakSimulation = False

    def run(self):
        while True:
            # Check if we should break all simulation runs
            breakLoop = False
            executeThread.breakSimulationLock.acquire()
            breakLoop = executeThread.breakSimulation
            executeThread.breakSimulationLock.release()

            if breakLoop:
                break

            # Get new command from the queue, execute and mark as done
            command = executeThread.commands.get()
            self.executeCommand(command)
            executeThread.commands.task_done()

    def executeCommand(self, cmd):
        ## \brief Execute command
        #
        # Execute jar file, into stdout and stderr into files inside working
        # dir. Use command "java -jar <cmd>"
        #
        # \param cmd    Dict with command, working dir, ...

        try:
            # If breakSimulation set: Skip remaining simulation runs
            executeThread.breakSimulationLock.acquire()
            if executeThread.breakSimulation:
                executeThread.breakSimulationLock.release()
                return
            executeThread.breakSimulationLock.release()

            # Output files for stdout and stderr output of executed file
            stdoutFileName = os.path.join(cmd["path"], "stdout.log")
            stderrFileName = os.path.join(cmd["path"], "stderr.log")
            stdoutFile = open(stdoutFileName, "w")
            stderrFile = open(stderrFileName, "w")

            self.log("Starting execution of \"" + cmd['cmd'] + \
                    "\" in path \"" + cmd['path'] + "\"")

            # Start process
            proc = subprocess.Popen(['java', '-jar', cmd['cmd']],
                    stdout=stdoutFile, stderr=stderrFile, cwd=cmd['path'])

            proc.wait()
            ret = proc.returncode

            # Remove simulation file. Copy available in the base directory
            os.remove(os.path.join(cmd['path'], cmd['cmd']))

            # Return value indicated error and user marked that this breaks
            # execution of remaining simulations
            if ret and cmd["break"]:
                executeThread.breakSimulationLock.acquire()
                executeThread.breakSimulation = True
                executeThread.breakSimulationLock.release()

            self.log("Path \"" + cmd["path"] + "\" done, return code: " + \
                    str(ret))

        except KeyboardInterrupt:
            # Inform others that a problem occured
            executeThread.breakSimulationLock.acquire()
            executeThread.breakSimulation = True
            executeThread.breakSimulationLock.release()

        finally:
            try:
                # Release lock, we could have
                executeThread.breakSimulationLock.release()
                executeThread.printLock.release()
            except threading.ThreadError:
                # Catch errors caused by not having a lock
                pass
            stdoutFile.close()
            stderrFile.close()

    def log(self, msg):
        ## \brief Log function
        #
        # Convenience function for logging
        #
        # \param msg    Log message to print

        # Ensure only one threat at time prints to screen using lock
        executeThread.printLock.acquire()
        print "(" + threading.current_thread().name + ") " + \
            datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + \
            ": " + str(msg)
        executeThread.printLock.release()


##
# Main App
##

parser = argparse.ArgumentParser(
        description='Run multiple jar files in separate directories and' +\
                'threads using the command "java -jar <progname>"')
parser.add_argument('progname', help='Name of jar file')
parser.add_argument('--max_threads', type=int, default=4, dest='max_threads',
        help='Number of maximum concurrent threads')
parser.add_argument('--runs', type=int, default=10, dest='runs', metavar="N",
        help='Run given jar file RUNS times (montecarlo simulation)')
parser.add_argument('--break', dest='break_runs', action='store_const',
        const=True, default=False,
        help='Break remaining runs in case of return value is not 0')
parser.add_argument('--execute', dest='exe', metavar="<program name>",
        default=None, help="Execute command when script has finished")

args = parser.parse_args()

print "Number of runs: ", args.runs
print "Number of threads:", args.max_threads
if args.exe:
    print "Executing \"" + args.exe + "\" when done"

if not os.path.isfile(args.progname):
    print "File not found:", args.progname
    sys.exit(1)

# Place each run in separate folder including date
simulationFolderName=datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

if os.path.exists(simulationFolderName):
    print "Simulation folder exists! Aborting"
    sys.exit(1)

os.makedirs(simulationFolderName)

print "Storing results into", simulationFolderName

# Start threads
threads = [executeThread() for i in range(args.max_threads)]
for thread in threads:
    thread.setDaemon(True)
    thread.start()

cmds = []

# Copy one version of the app to the base directory. The other copies can be
# removed later
shutil.copy(args.progname, os.path.join(os.path.abspath("."), simulationFolderName))

# Generate a separate command for each simulation run. Create corresponding
# folder, execute output inside this folder
for i in range(args.runs):
    progpath = os.path.join(os.path.abspath("."), simulationFolderName, "run_" + str(i+1))
    os.makedirs(progpath)
    shutil.copy(args.progname, progpath)
    metainfo = {}
    metainfo["cmd"] = args.progname
    metainfo["path"] = progpath
    metainfo["break"] = args.break_runs
    cmds.append(metainfo)

# Enqueue commands. Worker thread will take commands out of this queue
for cmd in cmds:
    executeThread.commands.put(cmd)


while (True):
    time.sleep(1)
    # Check if we should break the simulation
    breakEverything = False
    executeThread.breakSimulationLock.acquire()
    breakEverything = executeThread.breakSimulation
    executeThread.breakSimulationLock.release()

    if executeThread.commands.empty():
        # Wait until all threads are done
        executeThread.commands.join()
        break

    if breakEverything:
        break

if args.exe != None:
    print "Executing \"" + args.exe + "\""
    os.system(args.exe)
