#! /bin/bash

# Cleanup the lower topology

sudo clab destroy -t polarfly-lower.yml
sudo rm -rf clab-polarfly-radix8

docker ps -a | grep Removal | awk '{print $1}' | xargs -n1 docker rm 
docker ps -a | grep Exited | awk '{print $1}' | xargs -n1 docker rm 

sudo clab tools vxlan delete -p clab