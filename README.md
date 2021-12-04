# HomeCloud
<!-- ### Actual cloud diagram
![Alt text](Diagrams/Images/CloudMap-25-11-21.svg?raw=true "Actual cloud diagram") -->
## Requirements
- 32Gb of RAM
- 16Cores
- 500Gb of storage
- 2 Physical NICs
- Ubuntu 20.04

## Network configuration

|          Network         |       IP range      |DHCP |
|--------------------------|---------------------|-----|
| Physical machines        | 10.2.0.1-10.2.0.253 | YES |
| Microstack Instances     | 10.2.1.1-10.2.1.252 | NO  |
| LXD Instances            | 10.2.2.1-10.2.2.252 | NO  |
| Kubernetes Instances     | 10.2.3.1-10.2.3.252 | NO  |

## Installation and configuration of your cloud

### Microstack

#### Installation:

To install microstack just use this command:
`sudo snap install microstack --channel=rocky/edge --classic`
I have encountered difficulties with the latest version of MicroStack so i'm using the version `rocky(195)`.
Microstack `ussuri'(242)` have TLS enabled on the endpoints and juju(that we will use later) have problem with self signed TLS certificates.

#### Configuration

`sudo microstack.init`

Follow this steps:

```
Do you want to setup clustering? (yes/no) [default=no] > yes
What is this machines' role? (control/compute) > control
Please enter the ip address of the control node [default=10.2.0.253] > <IP OF YOUR ETH0>
```

Wait a few minutes and microstack should be marked as initialized!
Now that microstack is ready we have to modify quotas for having juju working properly but let's make our life easier by adding aliases.

```bash
sudo snap alias microstack.openstack openstack
sudo snap alias microstack.ovs-vsctl ovs-vsctl
```

Quotas:

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

It's time to login in the Microstack Dashboard!
Go to `<microstack ip>`(10.2.0.253 in my case) in your browser:

![Alt text](images/OpenStack-Dashboard.png?raw=true "OpenStack Dashboard")

The default credentials are:
```
admin
keystone
```
:warning: WARNING :warning:
If you modify the default credentials you'll need to modify them again in `/var/snap/microstack/common/etc/microstack.rc`.

Now that we are logged in the dashboard, we have to remove the existing router and networks to create new ones.

Go to the `Admin` section and `Routers`

![Alt text](images/remove-router.webp?raw=true "Remove router")

And now to `networks`

![Alt text](images/remove-networks.webp?raw=true "Remove networks")

Let's add a public network to our Microstack!

Network configuration:

![Alt text](images/public-net.png?raw=true "Network configuration")

Subnet configuration:

![Alt text](images/public-subnet.png?raw=true "Subnet configuration")

Subnet details:

![Alt text](images/public-details.png?raw=true "Subnet details")

And now our network should appear in the list:

![Alt text](images/public-shown.png?raw=true "Network shown")

Time to configure it...

```
# ovs-vsctl add-port br-ex enp2s0f1
# ip addr flush dev enp2s0f1
# ip addr add 10.2.1.253/24 dev br-ex
# ip link set br-ex up
```
You'll need to replace `enp2s0f1` with your second NIC.

Now that we have added an IP address to `br-ex`, you'll need to add `microstack-br-workaround`(you can find it in the `microstack` foder) to 
`/usr/local/bin` to your server and do

```bash
chmod +x /usr/local/bin/microstack-br-workaround
```

You'll also need to create a service for this script to run on reboot.

Add `microstack-br-workaround.service` to your server under `/etc/systemd/system` and execute
```
# systemctl daemon-reload
# systemctl enable microstack-br-workaround.service
```

We're almost finished with the microstack configuration, trust me...

Ok so, we now need to create a local network for our machines to communicate together.

Network configuration:

![Alt text](images/juju-net.png?raw=true "Network configuration")

Subnet configuration:

![Alt text](images/juju-subnet.png?raw=true "Subnet configuration")

Subnet details:

![Alt text](images/juju-details.png?raw=true "Subnet details")

And now the router !

Router configuration:

![Alt text](images/juju-public-router.png?raw=true "Router configuration")

And now the new router should appear:

![Alt text](images/juju-public-router-shown.png?raw=true "Router shown")

Adding the local network to the router:

![Alt text](images/juju-public-router-add-network.png?raw=true "Add network")

Waiting for our router to be ready:

![Alt text](images/juju-public-router-wait-ready.png?raw=true "Wait ready")

And boom!

![Alt text](images/juju-public-router-ready.png?raw=true "Router ready")

#### Testing

To see if our network configuration is working, we will need to create security groups.

Go to:

![Alt text](images/secgroups-path.png?raw=true "Secgroups path")

Create a new security group:

![Alt text](images/secgroups-add.png?raw=true "Create secgroup")

Add rule for ICMP:

![Alt text](images/secgroups-add-icmp.png?raw=true "Add ICMP rule")

Add rule for SSH:

![Alt text](images/secgroups-add-ssh.png?raw=true "Add SSH rule")

and create a test instance:

Go to:

![Alt text](images/instances-path.png?raw=true "Instances path")

Create a new instance:

![Alt text](images/instances-info.png?raw=true "Instances info")

Select image:

![Alt text](images/instance-select-image.png?raw=true "Instances flavor")

Select flavor:

![Alt text](images/instance-select-flavor.png?raw=true "Instances flavor")

Select network:

![Alt text](images/instance-select-network.png?raw=true "Instances network")

Add floating IP:

![Alt text](images/instance-add-floating-ip.png?raw=true "Instances add IP")

Create floating IP:

![Alt text](images/instance-create-floating-ip.png?raw=true "Instances create IP")

Alocate floating IP:

![Alt text](images/instance-allocate-ip.png?raw=true "Instances allocate IP")

And we're done:

![Alt text](images/instance-ip-added.png?raw=true "Instances IP added")

Now let's try to log in!

```bash
$ ssh cirros@10.2.1.1
```

password:
`gocubsgo`

We are now connected to our test instance!
```bash
$ ip a
```

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast qlen 1000
    link/ether fa:16:3e:b8:23:f8 brd ff:ff:ff:ff:ff:ff
    inet 192.168.222.5/24 brd 192.168.222.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::f816:3eff:feb8:23f8/64 scope link 
       valid_lft forever preferred_lft forever
```

Cool! now our openstack cloud is ready!


### juju

#### Instalation

`sudo snap install juju --classic`

After installing juju, we need to add our microstack to it.

`juju add-cloud --client microstack -f HomeCloud/microstack/microstack.yaml`

And add its credentials.

```
source HomeCloud/microstack/microstack.rc
juju autoload-credentials
```

You should see:

This operation can be applied to both a copy on this client and to the one on a controller.
No current controller was detected and there are no registered controllers on this client: either bootstrap one or register one.

Looking for cloud and credential information on local client...
```
1. LXD credential "localhost" (new)
2. openstack region "<unspecified>" project "admin" user "admin" (new)
3. rackspace credential for user "admin" (new)
Select a credential to save by number, or type Q to quit: 2

Select the cloud it belongs to, or type Q to quit [microstack]: [ENTER]

Saved openstack region "<unspecified>" project "admin" user "admin" to cloud microstack locally

1. LXD credential "localhost" (new)
2. openstack region "<unspecified>" project "admin" user "admin" (existing, will overwrite)
3. rackspace credential for user "admin" (new)
Select a credential to save by number, or type Q to quit: q
```

You'll now need to install ubuntu images for microstack.

Go to:

https://cloud-images.ubuntu.com/

and download:

- Bionic
- Focal
- Xenial

Now we need to add these images to our microstack cloud.

```bash
microstack.openstack image create --file images/bionic-server-cloudimg-amd64.img --public --container-format=bare --disk-format=qcow2 bionic

microstack.openstack image create --file images/focal-server-cloudimg-amd64.img --public --container-format=bare --disk-format=qcow2 focal

microstack.openstack image create --file images/xenial-server-cloudimg-amd64.img --public --container-format=bare --disk-format=qcow2 xenial
```

Ok! now that our images have been added to our microstack, we need to create metadatas for them on juju.

You will need to create a folder named `simplestreams` at your home folder for images metadatas.

`mkdir ~/simplestreams`

and run `python3 HomeCloud/microstack/image-metadata.py`

```
Do you want to add bionic to juju? (y/n):y
Do you want to add cirros to juju? (y/n):n
Do you want to add focal to juju? (y/n):y
Do you want to add xenial to juju? (y/n):y
```

Create a microstack flavor for the controller:

`openstack flavor create juju-controller --ram 2048 --disk 20 --vcpus 1`

And bootstrap a juju controller:

```
juju bootstrap --config network=juju-net \
  --config external-network=public-net \
  --config use-floating-ip=true \
  --bootstrap-series=bionic \
  --bootstrap-constraints instance-type=juju-controller \
  --metadata-source ~/simplestreams \
  microstack microstack
```

The bootstrap may fail because the instance got status `BUILD` for too long.
But dont worry, if the bootstrap failed because of that just retry and it should work!

If the bootstrap fails you'll maybe need to remove a security group by yourself:

```
ERROR failed to bootstrap model: cannot start bootstrap instance: cannot run instance: max duration exceeded: instance "a0902f41-d049-4c11-8d57-b2eda76a3ba1" has status BUILD
WARNING cannot delete security group "juju-ddcd414b-fd72-4d3d-8cd3-1a3ed6e2e96c-14fe29ab-b133-4058-8fb3-e4940fab3c6d-0". Used by another model?
```

`openstack security group list --format yaml`

```yaml
- Description: juju group
  ID: 3587a263-bdf3-44fc-a928-146fc18aa143
  Name: juju-ddcd414b-fd72-4d3d-8cd3-1a3ed6e2e96c-14fe29ab-b133-4058-8fb3-e4940fab3c6d-0
  Project: 29223ea08b5d4ccf999fa697dc802dae
  Tags: []
- Description: Default security group
  ID: 9aab11a2-b25f-41f4-96e3-1c6d80ea23d0
  Name: default
  Project: 29223ea08b5d4ccf999fa697dc802dae
  Tags: []
- Description: Default security group
  ID: b5fe9208-1562-4cfd-bac1-350ac36cbe74
  Name: default
  Project: e044ba87d18f402c9d65890224578632
  Tags: []
- Description: Default security group
  ID: c99394f8-5133-418e-9809-2a014e83fd92
  Name: default
  Project: ''
  Tags: []
- Description: ''
  ID: dc90de11-eb6e-4dfb-be36-ecccf949d1eb
  Name: public-testing
  Project: 29223ea08b5d4ccf999fa697dc802dae
  Tags: []
```

here you can see the security group created by juju

`openstack security group delete 3587a263-bdf3-44fc-a928-146fc18aa143`

`openstack security group list --format yaml`

```yaml
- Description: Default security group
  ID: 9aab11a2-b25f-41f4-96e3-1c6d80ea23d0
  Name: default
  Project: 29223ea08b5d4ccf999fa697dc802dae
  Tags: []
- Description: Default security group
  ID: b5fe9208-1562-4cfd-bac1-350ac36cbe74
  Name: default
  Project: e044ba87d18f402c9d65890224578632
  Tags: []
- Description: Default security group
  ID: c99394f8-5133-418e-9809-2a014e83fd92
  Name: default
  Project: ''
  Tags: []
- Description: ''
  ID: dc90de11-eb6e-4dfb-be36-ecccf949d1eb
  Name: public-testing
  Project: 29223ea08b5d4ccf999fa697dc802dae
  Tags: []
```
And the group has been deleted