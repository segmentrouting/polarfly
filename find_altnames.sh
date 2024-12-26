#!/bin/bash

# Get all network namespaces that start with clab-polarfly
namespaces=$(ip netns list | grep "clab-polarfly" | awk '{print $1}')

# Loop through each namespace
for ns in $namespaces; do
    # Run 'ip a' in the namespace and store the full output
    output=$(ip netns exec $ns ip a)
    
    # Use awk to process the output and find relevant information
    echo "$output" | awk '
        # If line contains interface ID and name
        /^[0-9]+: / {
            # Store the interface info
            interface=$1
            gsub(/:$/, "", interface)  # Remove trailing colon
            current_if=$2
            gsub(/:$/, "", current_if) # Remove trailing colon
        }
        # If line contains altname
        /altname/ {
            # Print namespace, interface ID, interface name, and altname
            printf "=== '"$ns"' ===\n"
            printf "Interface ID: %s\n", interface
            printf "Interface name: %s\n", current_if
            printf "Altname: %s\n\n", $2
        }
    '
done 