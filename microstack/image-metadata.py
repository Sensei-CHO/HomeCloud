# import subprocess
# import json
# from pprint import pprint
# def execute(command, json_outuput=False):
#     sp = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     output = out.decode()
#     if json_outuput:
#         try:
#             output = json.loads(output)
#         except json.decoder.JSONDecodeError:
#             pass
#     return output

# openstack_images = execute(["microstack.openstack", "image", "list", "--format", "json"], json_outuput=True)["output"]
# for x in openstack_images:
#     print(execute(["juju", "metadata", "generate-image", "-d", "~/simplestreams", "-i", x["ID"], "-s", x["Name"], "-r", "microstack", "-u", "http://10.2.1.253:5000/v3"])["output"])

import sys
import os
import subprocess
import json

def runcommand(command, json_output=False):
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    output = result.decode()
    if json_output:
        try:
            output = json.loads(output)
        except json.decoder.JSONDecodeError:
            pass
    return output

# print(runcommand("microstack.openstack image list --format json", json_output=True))
