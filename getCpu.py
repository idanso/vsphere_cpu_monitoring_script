from pyVim.commands.commands import help
from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL, Disconnect
import atexit
import sys
import argparse
import getpass
import ssl
import time
import string

isPrtg = False
testing = False

#if isPrtg:
   # from prtg.sensor.result import CustomSensorResult
   # from prtg.sensor.units import ValueUnit

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(
       description='Process args for retrieving all the Virtual Machines')
   parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
   parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
   parser.add_argument('-v', '--vm', required=True, action='store',
                       help='header vm to monitor')
   parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
   args = parser.parse_args()
   return args


def main():

    testargs = "-s 10.251.0.200 -u administrator@vsphere.local -p Radware10? -v \"Defense Flow\""
    usertest = testargs.split()
    print(usertest[0])

    print(usertest)
    if isPrtg:
        data = json.loads(sys.argv[1])
    else:
        args = GetArgs()
    #vm header name
    headerName = args.vm


    # Connect to the host without SSL signing
    try:
        if isPrtg:
            si = SmartConnectNoSSL(
                host=args.host,
                user=args.user,
                pwd=args.password,
                port=int(args.port))
        else:
            si = SmartConnectNoSSL(
                host=args.host,
                user=args.user,
                pwd=args.password,
                port=int(args.port))
        atexit.register(Disconnect, si)

    except IOError as e:
        pass

    if not si:
        raise SystemExit("Unable to connect to host with supplied info.")

    content = si.RetrieveContent()
    perfManager = content.perfManager

    #print(perfManager.perfCounter)
    #for c in perfManager.perfCounter:
     #   if c.groupInfo.key == "cpu" and c.nameInfo.key == "usagemhz":
      #      print(c)

# create a list of vim.VirtualMachine objects so
    # that we can query them for statistics
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True

    containerView = content.viewManager.CreateContainerView(container,
                                                            viewType,
                                                            recursive)
    children = containerView.view

    vms = []
    # Loop through all the VMs
    for child in children:
        if child.summary.config.name.startswith(headerName):
            vms.append(child)

    for vm in vms:
        print("name:  " + vm.summary.config.name + "\ncpu usage:  " + str(vm.summary.quickStats.overallCpuUsage))



if __name__ == "__main__":
    main()