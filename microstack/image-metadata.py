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
        runcommand(f"juju metadata generate-image -d ~/simplestreams -i {x['ID']} -s {x['Name']} -r microstack -u https://10.2.0.253:5000/v3")
    elif result == "n":
        pass
    else:
        print("Unrecognized argument...")
        exit()
