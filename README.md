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

```bash
sudo microstack init --control
```

```
Would you like to configure clustering? (yes/no) [default=yes] > 
2021-12-05 20:40:42,748 - microstack_init - INFO - Configuring clustering ...
Please enter the ip address of the control node [default=10.2.0.253] > 10.2.0.253
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

```bash
sudo snap alias microstack.openstack openstack
sudo snap alias microstack.ovs-vsctl ovs-vsctl
```

### Quotas

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

### Testing

## Microk8s

## LXD
