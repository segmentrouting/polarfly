#! /bin/bash

# Cleanup the lower topology

sudo clab destroy -t polarfly-lower.yml
sudo rm -rf clab-polarfly-radix8
