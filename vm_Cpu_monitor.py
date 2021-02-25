# -*- coding: utf-8 -*-

import json
import sys
import argparse
import getpass
import ssl
import string
import atexit
import argparse
import getpass
import ssl

from pyVim.commands.commands import help
from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL, Disconnect

isPrtg = True

if isPrtg:
    from prtg.sensor.result import CustomSensorResult
    from prtg.sensor.units import ValueUnit

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

if __name__ == "__main__":
    try:
        data = json.loads(sys.argv[1])
        if isPrtg:
            csr = CustomSensorResult(text="This sensor runs on %s" % data["host"])

            #handle parameters
            params = data["params"].split()
            host = params[0]
            user = params[1]
            password = params[2]
        else:
            GetArgs()

        vmHeaderName = ' '.join(params[3:])

        # connect to vcenter
        try:
            if isPrtg:
                si = SmartConnectNoSSL(
                    host=host,
                    user=user,
                    pwd=password)
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
            if child.summary.config.name.startswith(vmHeaderName + "-("):
                vms.append(child)

        if isPrtg:
            #check if there are any vms with this header name to avoid firs time error
            if len(vms) != 0:
                for vm in vms:
                    csr.add_channel(name=vm.summary.config.name,
                                    value=round(vm.summary.quickStats.overallCpuUsage/1000, 3),
                                    unit="GHz",
                                    is_float=True)
                                    #is_limit_mode=True,
                                    #limit_min_error=10,
                                    #limit_max_error=80,
                                    #limit_error_msg="Percentage too high")
            else:
                csr.add_channel(name="No Vm's",
                                value=0,
                                unit="GHz",
                                is_float=False)

        else:
            print("Host: " + vm.summary.guest.guestFullName + "CPU: " + round(vm.summary.quickStats.overallCpuUsage/1000, 3) + " GHz")

        print(csr.json_result)
    except Exception as e:
        csr = CustomSensorResult(text="Python Script execution error")
        csr.error = "Python Script execution error: %s" % str(e)
        print(csr.json_result)
