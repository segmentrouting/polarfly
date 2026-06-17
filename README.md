## polarfly

This project is setup to model Polarfly topologies of various size and in some cases has containerlab topology definitions and config files to them. 


### Instructions:

1. Clone this repository

2. Install Containerlab: https://containerlab.dev/install/

3. Acquire a Cisco XRd or other dockerized router image (sonic-vs, etc.)

4. Load docker image
```
docker load -i <image_name>
```

5. Modprobe
```
sudo modprobe br_netfilter
```

6. For anything larger than the q=7 topology append the following to /etc/sysctl.conf
```
fs.inotify.max_user_instances = 131072
fs.inotify.max_user_watches   = 1048576
fs.inotify.max_queued_events  = 65536

net.ipv4.neigh.default.gc_thresh1 = 4096
net.ipv4.neigh.default.gc_thresh2 = 8192
net.ipv4.neigh.default.gc_thresh3 = 16384
net.ipv6.neigh.default.gc_thresh1 = 4096
net.ipv6.neigh.default.gc_thresh2 = 8192
net.ipv6.neigh.default.gc_thresh3 = 16384

net.core.rmem_max          = 16777216
net.core.wmem_max          = 16777216
net.core.netdev_max_backlog = 32768

fs.file-max          = 2097152
kernel.pid_max       = 4194304
kernel.threads-max   = 4194304
vm.max_map_count     = 262144
```

7. Apply sysctl changes
```
sudo sysctl -p
```

8. cd into the topology directory and deploy
```
cd q7
clab deploy -t sonic-polarfly-q7.clab.yaml
```

9. apply sonic configurations
```
./q7-config.sh
```