from trex_stl_lib.api import *
import random

class STLIPv6Bulk(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = [
            
            'fc00:0:f800:0::/64',
            
            'fc00:0:f800:2::/64',
            
            'fc00:0:f800:4::/64',
            
            'fc00:0:f800:6::/64',
            
            'fc00:0:f800:8::/64',
            
            'fc00:0:f800:12::/64',
            
            'fc00:0:f800:14::/64',
            
            'fc00:0:f800:16::/64',
            
            'fc00:0:f800:18::/64',
            
            'fc00:0:f800:20::/64',
            
            'fc00:0:f800:22::/64',
            
            'fc00:0:f800:24::/64',
            
            'fc00:0:f800:26::/64',
            
            'fc00:0:f800:28::/64',
            
            'fc00:0:f800:30::/64',
            
            'fc00:0:f800:32::/64',
            
            'fc00:0:f800:34::/64',
            
            'fc00:0:f800:36::/64',
            
            'fc00:0:f800:38::/64',
            
            'fc00:0:f800:40::/64',
            
            'fc00:0:f800:42::/64',
            
            'fc00:0:f800:44::/64',
            
            'fc00:0:f800:46::/64',
            
            'fc00:0:f800:48::/64',
            
            'fc00:0:f800:50::/64',
            
            'fc00:0:f800:52::/64',
            
            'fc00:0:f800:54::/64',
            
            'fc00:0:f800:56::/64',
            
            'fc00:0:f800:58::/64',
            
            'fc00:0:f800:60::/64',
            
            'fc00:0:f800:62::/64',
            
            'fc00:0:f800:64::/64',
            
            'fc00:0:f800:66::/64',
            
            'fc00:0:f800:68::/64',
            
            'fc00:0:f800:70::/64',
            
            'fc00:0:f800:72::/64',
            
            'fc00:0:f800:74::/64',
            
            'fc00:0:f800:76::/64',
            
            'fc00:0:f800:78::/64',
            
            'fc00:0:f800:80::/64',
            
            'fc00:0:f800:82::/64',
            
            'fc00:0:f800:84::/64',
            
            'fc00:0:f800:86::/64',
            
            'fc00:0:f800:88::/64',
            
            'fc00:0:f800:90::/64',
            
            'fc00:0:f800:92::/64',
            
            'fc00:0:f800:94::/64',
            
            'fc00:0:f800:96::/64',
            
            'fc00:0:f800:98::/64',
            
            'fc00:0:f800:100::/64',
            
            'fc00:0:f800:102::/64',
            
            'fc00:0:f800:104::/64',
            
            'fc00:0:f800:106::/64',
            
            'fc00:0:f800:108::/64',
            
            'fc00:0:f800:110::/64',
            
            'fc00:0:f800:112::/64',
            
        ]
        
        # Source subnet
        src_subnet = 'fc00:0:f800:10::/64'
        
        # Create streams list
        streams = []
        
        # Bulk packet size
        packet_size = 1250
        
        # Number of flows per destination
        flows_per_dst = 10
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create multiple bulk flows for this destination
            for flow_id in range(flows_per_dst):
                # Generate fixed host parts for src and dst to create stable flows
                src_host = 100 + flow_id
                dst_host = 100 + flow_id
                
                # Create full IPv6 addresses
                src_ip = f"{src_prefix}{src_host}"
                dst_ip = f"{dst_prefix}{dst_host}"
                
                # Create packet with IPv6 and UDP for bulk transfer
                base_pkt = Ether()/\
                          IPv6(src=src_ip, dst=dst_ip)/\
                          UDP(sport=1000+flow_id, dport=2000+flow_id)
                
                # Calculate padding to reach desired size
                pad_size = max(0, packet_size - len(base_pkt))
                
                # Create a stream with the packet
                pkt = STLPktBuilder(pkt=base_pkt/('x' * pad_size))
                
                # Create stream with appropriate rate
                # Each flow gets 1/10th of the total rate to achieve ~10Mbps per destination
                stream = STLStream(
                    packet=pkt,
                    mode=STLTXCont(pps=1000/flows_per_dst),
                    isg=10*(subnet_id*flows_per_dst + flow_id),  # Inter-stream gap to avoid bursts
                    flow_stats=STLFlowStats(pg_id=subnet_id*100 + flow_id)
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
        
        print("Bulk traffic started on port 0")
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