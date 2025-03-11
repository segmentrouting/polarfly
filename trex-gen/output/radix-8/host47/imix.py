from trex_stl_lib.api import *
import random

class STLIPv6(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = ['fc00:0:f800:0::/64', 'fc00:0:f800:2::/64', 'fc00:0:f800:4::/64', 'fc00:0:f800:6::/64', 'fc00:0:f800:8::/64', 'fc00:0:f800:10::/64', 'fc00:0:f800:12::/64', 'fc00:0:f800:14::/64']
        
        # Source subnet
        src_subnet = 'fc00:0:f800:94::/64'
        
        # IMIX packet sizes and weights
        imix_sizes = [128, 570, 1518]
        imix_weights = [0.5833333333333334, 0.3333333333333333, 0.08333333333333333]
        
        # Base packets per second
        pps_base = 100
        
        # Create streams list
        streams = []
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create streams for each packet size in IMIX
            for size_id, (size, weight) in enumerate(zip(imix_sizes, imix_weights)):
                # Calculate packets per second for this stream
                pps = int(pps_base * weight)
                
                # Create base packet - use fixed addresses instead of VM for IPv6
                base_pkt = Ether() / IPv6(src=src_prefix + "::2", dst=dst_prefix + "::2") / UDP(sport=1025, dport=1025)
                
                # Pad to desired size
                pad_size = max(0, size - len(base_pkt))
                if pad_size > 0:
                    base_pkt = base_pkt / ('x' * pad_size)
                
                # Create stream without VM for IPv6 (TRex limitation)
                stream = STLStream(
                    packet=STLPktBuilder(pkt=base_pkt),
                    mode=STLTXCont(pps=pps),
                    flow_stats=STLFlowStats(pg_id=subnet_id * 10 + size_id)
                )
                
                streams.append(stream)

        return streams

def register():
    return STLIPv6()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6()
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
