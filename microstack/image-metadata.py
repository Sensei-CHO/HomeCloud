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

import subprocess
import json

def runcommand(command, json_output=False):
    try:
        result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    except FileNotFoundError:
        print("It's seems that microstack or juju is not installed. Exiting...")
        exit()
    output = result.decode()
    if json_output:
        try:
            output = json.loads(output)
        except json.decoder.JSONDecodeError:
            pass
    return output

for x in runcommand("microstack.openstack image list --format json", json_output=True):
    result = input(f"Do you want to add {x['Name']} to juju? (y/n):")
    if result == "y":
        runcommand(f"juju metadata generate-image -d ~/simplestreams -i {x['ID']} -s {x['Name']} -r microstack -u http://10.2.1.253:5000/v3")
    elif result == "n":
        pass
    else:
        print("Unrecognized argument...")
        exit()