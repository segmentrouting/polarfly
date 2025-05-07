### quick install

1. Install docker
2. Install containerlab
```
bash -c "$(curl -sL https://get.containerlab.dev)"
```

3. Install Ansible

4. Get sonic-vpp image tarball from GDrive:
```
https://drive.google.com/file/d/1lgLaQ0nrEN5DKgHEcmyPZR9uhKMQQdXg/view?usp=drive_link
```

5. docker load image
```
docker load -i vrnetlab/sonic_sonic-vs:vpp20250422
```

6. Get ubuntu-trex container image from dockerhub:
```
docker pull iejalapeno/ubuntu-trex:1.4
```

7. Deploy containerlab topology
```
sudo clab deploy -t topology.yml
```

It takes a couple min for the sonic nodes and their docker containers to come up

8. Verify sonic container status, example:
```
docker ps
docker logs clab-polarfly-node00
```

If the log ends with something like "Startup complete in: 0:03:07.192163" you should be good

9. Test ssh access
```
ssh admin@clab-polarfly-node00

password = admin
```

10. Upon ssh access check sonic docker containers
```
docker ps
```

Example output:
```
admin@clab-topo-host1-node00's password: 
Linux sonic 6.1.0-22-2-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.94-1 (2024-06-21) x86_64
You are on
  ____   ___  _   _ _  ____
 / ___| / _ \| \ | (_)/ ___|
 \___ \| | | |  \| | | |
  ___) | |_| | |\  | | |___
 |____/ \___/|_| \_|_|\____|

-- Software for Open Networking in the Cloud --

Unauthorized access and/or use are prohibited.
All access and/or use are subject to monitoring.

Help:    https://sonic-net.github.io/SONiC/

Last login: Tue May  6 06:43:22 2025 from 198.18.4.1
admin@sonic:~$ docker ps
CONTAINER ID   IMAGE                                COMMAND                  CREATED        STATUS          PORTS     NAMES
326aa3389d0a   docker-snmp:latest                   "/usr/bin/docker-snm…"   24 hours ago   Up 28 minutes             snmp
3e708456692c   docker-platform-monitor:latest       "/usr/bin/docker_ini…"   24 hours ago   Up 24 hours               pmon
b1ba522ac7d8   docker-sonic-mgmt-framework:latest   "/usr/local/bin/supe…"   24 hours ago   Up 24 hours               mgmt-framework
2e85f8b5a577   docker-lldp:latest                   "/usr/bin/docker-lld…"   24 hours ago   Up 24 hours               lldp
7eed762b3fb5   docker-sonic-gnmi:latest             "/usr/local/bin/supe…"   24 hours ago   Up 24 hours               gnmi
baa1286ed33e   docker-router-advertiser:latest      "/usr/bin/docker-ini…"   24 hours ago   Up 29 minutes             radv
c145f8b11090   docker-fpm-frr:latest                "/usr/bin/docker_ini…"   24 hours ago   Up 28 minutes             bgp
c81451d22282   docker-syncd-vpp:latest              "/usr/local/bin/supe…"   24 hours ago   Up 29 minutes             syncd
9dad25ba76d0   docker-teamd:latest                  "/usr/local/bin/supe…"   24 hours ago   Up 28 minutes             teamd
d140ce342eaa   docker-orchagent:latest              "/usr/bin/docker-ini…"   24 hours ago   Up 29 minutes             swss
efa4a95da813   docker-eventd:latest                 "/usr/local/bin/supe…"   24 hours ago   Up 24 hours               eventd
ff747056ba89   docker-database:latest               "/usr/local/bin/dock…"   24 hours ago   Up 24 hours               database
admin@sonic:~$ 
```

11. From sonic bash test BGP/FRR container access 
```
vtysh
```

Example:
````
admin@sonic:~$ vtysh

Hello, this is FRRouting (version 10.0.1).
Copyright 1996-2005 Kunihiro Ishiguro, et al.

2025/05/07 06:25:04 [YDG3W-JND95] FD Limit set: 1048576 is stupidly large.  Is this what you intended?  Consider using --limit-fds also limiting size to 100000
sonic# 
```

From there everything works like classic IOS

12. Exit sonic, cd into the ansible directory and run the 'sonic' playbook:
```
cd ~/polarfly/sonic-radix8/ansible

ansible-playbook -i hosts sonic-playbook.yaml -e "ansible_user=admin ansible_ssh_pass=admin ansible_sudo_pass=admin" -vv
```

sonic-playbook.yaml will apply global/interface configs, run a hostname and loopback shell script, add an 'sr0' loopback interface for SRv6 purposes, then apply the FRR config

Note, I haven't tested it on the polarfly topology yet as I still need to finish breaking it up across my 4 puny VMs. But, the 'hosts' file is updated such that everything else should work (fingers crossed!)

13. ssh into routers and see if BGP is working
```
ssh admin@clab-polarfly-node00

vtysh

show bgp summary
```
