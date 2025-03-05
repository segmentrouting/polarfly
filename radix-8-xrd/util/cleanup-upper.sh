#! /bin/bash

# Cleanup the upper topology

sudo clab tools vxlan delete -p clab
sudo clab destroy -t polarfly-upper.yml -c

docker ps -a | grep Removal | awk '{print $1}' | xargs -n1 docker rm 
docker ps -a | grep Exited | awk '{print $1}' | xargs -n1 docker rm 
