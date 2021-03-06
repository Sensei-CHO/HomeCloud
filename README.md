# HomeCloud

Here i'm going to present: "How i created my own cloud" at home.

This is not a tutorial but feel free to follow the following steps to create your own one.

:warning: DISCLAIMER :warning:

I'm doing this documention back from 0 so this doc will evoluate.

## Goal

My goal here is to create a "home" cloud to deploy easily everything i want such as

- VMs
- Containers
- Apps
- Etc...

I will need to deploy cloud native apps such as:

- Openstack(microstack in my case)
- LXD
- Kubernetes(microk8s in my case)
- and juju for deployments

And my cloud should look like this:

![Alt text](Diagrams/Images/homecloud.svg?raw=true "Homecloud diagram")

(The diagram will evoluate)

I'm going to deploy this cloud on my `HP Proliant DL360 G6` and use multiple machines in the future.

Actual configuration:

- 32Gb of RAM
- 16Cores
- 500Gb of storage
- 2 Physical NICs (eth0:10.2.0.253/eth1:10.2.0.252)
- Ubuntu 20.04

## Network configuration
This is my network configuration on my `Mikrotik RB2011UiAS-RM`

|          Network         |       IP range      |DHCP |
|--------------------------|---------------------|-----|
| Physical machines        | 10.2.0.1-10.2.0.253 | YES |
| Microstack Instances     | 10.2.1.1-10.2.1.252 | NO  |
| LXD Instances            | 10.2.2.1-10.2.2.252 | NO  |
| Kubernetes Instances     | 10.2.3.1-10.2.3.252 | NO  |

# Installation

Here are the steps to install what i need for my cloud

## Microstack

```bash
sudo snap install microstack --beta --devmode
```

## Microk8s

```bash
sudo snap install microk8s --classic
```

## LXD

```bash
sudo snap install lxd
```

## juju

```bash
 sudo snap install juju --classic
```

# Configuration

Here are the steps to install what i need for my cloud

## Microstack

### Init
This step if for deploying an microstack cloud which will be used as a backing cloud for juju.

```bash
sudo microstack init --control
```

```
Would you like to configure clustering? (yes/no) [default=yes] > yes
2021-12-05 20:40:42,748 - microstack_init - INFO - Configuring clustering ...
Please enter the ip address of the control node [default=10.2.0.253] > 10.2.0.253
...
```

The init process may fail with this error:

```
Traceback (most recent call last):
  File "/snap/microstack/242/bin/microstack", line 11, in <module>
    load_entry_point('microstack==0.0.1', 'console_scripts', 'microstack')()
  File "/snap/microstack/242/lib/python3.8/site-packages/microstack/main.py", line 44, in main
    cmd()
  File "/snap/microstack/242/lib/python3.8/site-packages/init/main.py", line 60, in wrapper
    return func(*args, **kwargs)
  File "/snap/microstack/242/lib/python3.8/site-packages/init/main.py", line 228, in init
    question.ask()
  File "/snap/microstack/242/lib/python3.8/site-packages/init/questions/question.py", line 210, in ask
    self.yes(awr)
  File "/snap/microstack/242/lib/python3.8/site-packages/init/questions/__init__.py", line 887, in yes
    check('openstack', 'network', 'create', 'test')
  File "/snap/microstack/242/lib/python3.8/site-packages/init/shell.py", line 69, in check
    raise subprocess.CalledProcessError(proc.returncode, " ".join(args))
subprocess.CalledProcessError: Command 'openstack network create test' returned non-zero exit status 1.
```

Don't worry just do a retry and it should work

### Aliases

Just to make my life easier

```bash
sudo snap alias microstack.openstack openstack
sudo snap alias microstack.ovs-vsctl ovs-vsctl
```

### Quotas

Default qotas are not enough to deploy what i want.

```bash
openstack quota set --cores 16 --ram 32768 --instances 100 --floating-ips 250 --secgroups 200 --secgroup-rules 1000 --ports 300 admin
```

Let's verify if our modification have been applied:

```
openstack quota show
```

The result should look like this: 

```
+----------------------+----------------------------------+
| Field                | Value                            |
+----------------------+----------------------------------+
| cores                | 16                               |
| fixed-ips            | -1                               |
| floating-ips         | 250                              |
| health_monitors      | None                             |
| injected-file-size   | 10240                            |
| injected-files       | 5                                |
| injected-path-size   | 255                              |
| instances            | 100                              |
| key-pairs            | 100                              |
| l7_policies          | None                             |
| listeners            | None                             |
| load_balancers       | None                             |
| location             | None                             |
| name                 | None                             |
| networks             | 100                              |
| pools                | None                             |
| ports                | 300                              |
| project              | 29223ea08b5d4ccf999fa697dc802dae |
| project_name         | admin                            |
| properties           | 128                              |
| ram                  | 32768                            |
| rbac_policies        | 10                               |
| routers              | 10                               |
| secgroup-rules       | 1000                             |
| secgroups            | 200                              |
| server-group-members | 10                               |
| server-groups        | 10                               |
| subnet_pools         | -1                               |
| subnets              | 100                              |
+----------------------+----------------------------------+
```

### Network

#### Delete existing router and networks

Delete existing router and networks from the dashboard at `https://<IP>` using password at
```bash
sudo snap get microstack config.credentials.keystone-password
```

to create new ones

##### Public network

This network will be used for allocating IPs from my LAN and access apps and machines easier.

Create a new network from the dashboard in the `Admin` section

```yaml
Name: public-net
Project: admin
Provider Network Type: Flat
Physical Network: physnet1
External: yes
Subnet Name: public-subnet
Network Address: 10.2.1.0/24
IP Version: IPv4
Gateway IP: 10.2.0.254
Enable DHCP: no
Allocation Pools: 10.2.1.1,10.2.1.252
```

Creating a bridge for the net to work on my LAN

In your terminal

```bash
sudo ovs-vsctl add-port br-ex enp2s0f1
sudo ip addr flush dev enp2s0f1
sudo ip addr add 10.2.1.253/24 dev br-ex
sudo ip link set br-ex up
```

Copy `HomeCloud/microstack/microstack-br-workaround` in `/usr/local/bin` and do:

```bash
sudo chmod +x /usr/local/bin/microstack-br-workaround
```

Copy `HomeCloud/microstack/microstack-br-workaround` in `/etc/systemd/system` and do:

```bash
systemctl daemon-reload
systemctl enable microstack-br-workaround.service
```

To reload the configuration on reboot

#### Private network

This network will be used for machines to communicate with each other.

Create a new network from the dashboard in the `Admin` section

```yaml
Name: juju-net
Project: admin
Provider Network Type: Local
Subnet Name: juju-subnet
Network Address: 192.168.222.1/24
IP Version: IPv4
Enable DHCP: yes
```

#### Create a router

This router will link `public-net` and `juju-net` for LAN IPs allocation.

Create a new router from the dashboard in the `Admin` section

```yaml
Router Name: public-router
Project: admin
Enable Admin State: yes
External Network: public
Enable SNAT: yes
```

#### Topology

To link `public-net` and `juju-net` to the router.

In the `Project` -> `Network Topology` section, click on the router and `add interface`, select `juju-net` and wait for the links to be up.

### Testing

This step will help us testing our network configuration.

#### Security Group

Go to `Project` -> `Network` -> `Security Groups`

Create a new group and add 2 rules:

- `All ICMP`
- `SSH`

#### Test Instance

This instance will be used to test the floating IP allocation and accessibility.

```bash
openstack server create \
  --image cirros \
  --flavor m1.tiny \
  --security-group default-public \
  --network juju-net \
  test-instance
```

Now go to the dashboard and allocate a floating ip to the `test-instance`

And try to log in the instance with SSH

```bash
ssh cirros@<floating ip>
```

Default password:

`gocubsgo`

To delete the instance:

```bash
openstack server delete test-instance
```
### Images

Go to https://cloud-images.ubuntu.com and download

- Focal
- Bionic
- Xenial

and add them to microstack

```bash
microstack.openstack image create --file images/bionic-server-cloudimg-amd64.img --public --container-format=bare --disk-format=qcow2 bionic

microstack.openstack image create --file images/focal-server-cloudimg-amd64.img --public --container-format=bare --disk-format=qcow2 focal

microstack.openstack image create --file images/xenial-server-cloudimg-amd64.img --public --container-format=bare --disk-format=qcow2 xenial
```

juju will need to create metadatas for these images.

Run `python3 image-metadata.py`

```
Do you want to add bionic to juju? (y/n):y
Do you want to add cirros to juju? (y/n):n
Do you want to add focal to juju? (y/n):y
Do you want to add xenial to juju? (y/n):y
```

This code will add images metadata to juju in the `~/simplestreams`

### juju

Now that the microstack cloud is up, we need to add it to juju

#### Add microstack to juju

For juju to deploy apps on a cloud, we need to add one.

```bash
juju add-cloud microstack
```

```
Cloud Types
  lxd
  maas
  manual
  openstack
  vsphere

Select cloud type: openstack

Enter the API endpoint url for the cloud []: https://10.2.0.253:5000/v3

Enter a path to the CA certificate for your cloud if one is required to access it. (optional) [/var/snap/microstack/common/etc/ssl/certs/cacert.pem]: [PRESS ENTER]

Auth Types
  access-key
  userpass

Select one or more auth types separated by commas: userpass

Enter region name: microstack

Enter the API endpoint url for the region [use cloud api url]: https://10.2.0.253:5000/v3

Enter another region? (y/N): n
```

#### Add credentials for microstack

juju will need to log in microstack to deploy apps

```bash
source /var/snap/microstack/common/etc/microstack.rc
juju autoload-credentials
```

```
1. LXD credential "localhost" (new)
2. openstack region "<unspecified>" project "admin" user "admin" (new)
3. rackspace credential for user "admin" (new)
Select a credential to save by number, or type Q to quit: 2

Select the cloud it belongs to, or type Q to quit [microstack]: microstack

Saved openstack region "<unspecified>" project "admin" user "admin" to cloud microstack locally

1. LXD credential "localhost" (new)
2. openstack region "<unspecified>" project "admin" user "admin" (existing, will overwrite)
3. rackspace credential for user "admin" (new)
Select a credential to save by number, or type Q to quit: q
```

#### Bootstraping a controller

To deploy apps and machines on a cloud, juju need to first deploy a controller.

```bash
juju bootstrap --bootstrap-series=bionic \
  --metadata-source=~/simplestreams \
  --model-default network=juju-net \
  --model-default external-network=public-net \
  --model-default use-floating-ip=true \
  microstack microstack
```

Sometimes the bootstrap procces fails because the controller instance took too long to be up. It often appends because this is the first time using an new microstack image.
juju may also not delete a sec group.

```
WARNING Config attribute "use-floating-ip" is deprecated.
You can instead use the constraint "allocate-public-ip".
Creating Juju controller "microstack" on microstack/microstack
Looking for packaged Juju agent version 2.9.21 for amd64
Located Juju agent version 2.9.21-ubuntu-amd64 at https://streams.canonical.com/juju/tools/agent/2.9.21/juju-2.9.21-ubuntu-amd64.tgz
WARNING Config attribute "use-floating-ip" is deprecated.
You can instead use the constraint "allocate-public-ip".
Launching controller instance(s) on microstack/microstack...
 - instance "1b0c9858-bfe6-44f7-a527-1f026f471b20" has status BUILD,
 - instance "1b0c9858-bfe6-44f7-a527-1f026f471b20" has status BUILD,
 - instance "1b0c9858-bfe6-44f7-a527-1f026f471b20" has status BUILD,
 - instance "1b0c9858-bfe6-44f7-a527-1f026f471b20" has status BUILD,
 - instance "1b0c9858-bfe6-44f7-a527-1f026f471b20" has status BUILD, WARNING Unable to retrieve details for created instance "1b0c9858-bfe6-44f7-a527-1f026f471b20": max duration exceeded: instance "1b0c9858-bfe6-44f7-a527-1f026f471b20" has status BUILD; attempting to terminate it
ERROR failed to bootstrap model: cannot start bootstrap instance: cannot run instance: max duration exceeded: instance "1b0c9858-bfe6-44f7-a527-1f026f471b20" has status BUILD
WARNING cannot delete security group "juju-ce2784a9-1cbd-4f9f-8cf6-e643f7591604-4346b56b-08b1-4057-8811-49d5a516996b-0". Used by another model?
```

Just delete it and retry bootstraping

```bash
openstack security group delete <secgroup>
```

## Microk8s

## LXD
