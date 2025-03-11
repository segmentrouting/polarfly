from trex_stl_lib.api import *
import random

class STLIPv6Bulk(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = ['fc00:0:f800:0::/64', 'fc00:0:f800:2::/64', 'fc00:0:f800:4::/64', 'fc00:0:f800:6::/64', 'fc00:0:f800:8::/64', 'fc00:0:f800:10::/64', 'fc00:0:f800:12::/64', 'fc00:0:f800:14::/64']
        
        # Source subnet
        src_subnet = 'fc00:0:f800:40::/64'
        
        # Packet size (in bytes)
        packet_size = 1250
        
        # Packets per second
        pps = 1000
        
        # Create streams list
        streams = []
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create base packet - use fixed addresses instead of VM for IPv6
            base_pkt = Ether() / IPv6(src=src_prefix + "::2", dst=dst_prefix + "::2") / UDP(sport=1025, dport=1025)
            
            # Pad to desired size
            pad_size = max(0, packet_size - len(base_pkt))
            if pad_size > 0:
                base_pkt = base_pkt / ('x' * pad_size)
            
            # Create stream without VM for IPv6 (TRex limitation)
            stream = STLStream(
                packet=STLPktBuilder(pkt=base_pkt),
                mode=STLTXCont(pps=pps),
                flow_stats=STLFlowStats(pg_id=subnet_id)
            )
            
            streams.append(stream)

        return streams

def register():
    return STLIPv6Bulk()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6Bulk()
        streams = profile.get_streams()
        
        # Add all streams to port 0
        client.add_streams(streams, ports=[0])
        print(f"Added {len(streams)} streams to port 0")
        
        # Start traffic on port 0
        client.start(ports=[0])
        
        print("Traffic started on port 0")
        print("Press Enter to stop...")
        input()
        
        # Stop traffic
        client.stop()
        
    except STLError as e:
        print(e)
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 
