# -*- coding: utf-8 -*-

import json
import sys
import getpass
import string
import getpass
import datetime
import requests

from Vm_Stats_Handler import *

from prtg.sensor.result import CustomSensorResult
from prtg.sensor.units import ValueUnit


def create_esxi_list(csv_mat):
    esxi_dict = {}
    cols = 2
    while cols < len(csv_mat[0]) - 2:
        # index 0: total data count 1: total above limit
        esxi_dict[csv_mat[0][cols]] = [0, 0]
        cols += 2

    return esxi_dict


if __name__ == "__main__":
    try:
        data = json.loads(sys.argv[1])

        #handle parameters
        params = data["params"].split()
        host_ip = params[0]
        user = params[1]
        password = params[2]
        limit = float(params[3])
        days_range = int(params[4])
        cluster_id = params[5]

        csr = CustomSensorResult(text="percent time above " + str(limit) + "% for the last %s days " % params[4])

        # get response from server
        device_response = requests.get("http://10.250.0.187/api/table.json?username=prtgadmin&password=prtgadmin")

        # get string of current date
        now = datetime.datetime.now()
        e_time = now.strftime("%Y-%m-%d-%H-%M-%S")
        s_time = now - datetime.timedelta(days=days_range)
        s_time = s_time.strftime("%Y-%m-%d-%H-%M-%S")
        print("time before x days: " + str(s_time))

        # check successful connection to prtg server
        if str(device_response) != "<Response [200]>":
            raise SystemExit("Unable to connect to prtg server.")

        # export csv historic data
        historicCsv = requests.get("http://" + host_ip + "/api/historicdata.csv?id=" + cluster_id + "&avg=0&sdate=" + s_time + "&edate=" + e_time + "&username=" + user + "&password=" + password)

        historicStr = str(historicCsv.content)

        # convert string csv raw data of historic data to matrix
        historic_mat = csv_historic_data_str_to_mat(historicStr)

        # create esxi list
        esxi_dict = create_esxi_list(historic_mat)

        # iterate over the historic data and count alive time and how much above limit
        for rows in range(1, len(historic_mat) - 2):
            for cols in range(3, len(historic_mat[0]) - 2, 2):
                if historic_mat[rows][cols] != "":
                    esxi_dict[historic_mat[0][cols - 1]][0] += 1
                    if float(historic_mat[rows][cols]) >= limit:
                        esxi_dict[historic_mat[0][cols - 1]][1] += 1

        # create channel for esxi
        for esxi in esxi_dict:
            csr.add_channel(name=esxi,
                            value=round((esxi_dict[esxi][1] / esxi_dict[esxi][0]) * 100, 2),
                            unit="%",
                            is_float=True)


        print(csr.json_result)
    except Exception as e:
        csr = CustomSensorResult(text="Python Script execution error")
        csr.error = "Python Script execution error: %s" % str(e)
        print(csr.json_result)
