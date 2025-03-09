#!/usr/bin/env python3
from trex_stl_lib.api import *
import argparse

def main():
    parser = argparse.ArgumentParser(description='Enable IPv6 ND on TRex ports')
    parser.add_argument('-s', '--server', type=str, default='localhost',
                        help='TRex server address')
    parser.add_argument('-p', '--ports', type=int, nargs='+', default=[0, 1],
                        help='Ports to enable IPv6 ND on')
    args = parser.parse_args()

    client = STLClient(server=args.server)
    
    try:
        # connect to server
        client.connect()
        
        # Enable service mode on ports
        client.set_service_mode(ports=args.ports, enabled=True)
        print(f"Enabled service mode on ports {args.ports}")
        
        # Configure IPv6 and enable ND on each port
        for port in args.ports:
            if port == 0:
                subnet = 'fc00:0:f801::/64'
                addr = 'fc00:0:f801::2'
            elif port == 1:
                subnet = 'fc00:0:f801:4::/64'
                addr = 'fc00:0:f801:4::2'
            else:
                continue
                
            # Set IPv6 configuration
            client.set_port_attr(port=port, attr_name='ipv6', attr_value=addr)
            client.set_port_attr(port=port, attr_name='ipv6_subnet', attr_value=subnet)
            client.set_port_attr(port=port, attr_name='ipv6_nd_enabled', attr_value=True)
            client.set_port_attr(port=port, attr_name='src_ipv6_enabled', attr_value=True)
            
            print(f"Configured IPv6 {addr} with subnet {subnet} on port {port}")
            print(f"Enabled IPv6 ND on port {port}")
        
        print("\nIPv6 ND is now enabled. Press Ctrl+C to exit...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except STLError as e:
        print(f"Error: {e}")
    finally:
        if client.is_connected():
            # Disable service mode before disconnecting
            client.set_service_mode(ports=args.ports, enabled=False)
            client.disconnect()

if __name__ == "__main__":
    main() 