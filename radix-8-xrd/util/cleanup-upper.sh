#! /bin/bash

# Cleanup the upper topology

sudo clab destroy -t polarfly-upper.yml
sudo rm -rf clab-polarfly-radix8

docker ps -a | grep Removal | awk '{print $1}' | xargs -n1 docker rm 
docker ps -a | grep Exited | awk '{print $1}' | xargs -n1 docker rm 

sudo clab tools vxlan delete -p clab