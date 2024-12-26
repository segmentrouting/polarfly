#!/bin/bash

# Get all network namespaces that start with clab-polarfly
namespaces=$(ip netns list | grep "clab-polarfly" | awk '{print $1}')

# Loop through each namespace
for ns in $namespaces; do
    # Run 'ip a' in the namespace and grep for altname
    result=$(ip netns exec $ns ip a | grep altname)
    
    # If grep found something (exit status 0), print the namespace and result
    if [ $? -eq 0 ]; then
        echo "=== $ns ==="
        echo "$result"
        echo
    fi
done