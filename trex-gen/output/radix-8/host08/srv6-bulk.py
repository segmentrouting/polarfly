from trex_stl_lib.api import *
import random

class STLIPv6SRv6Bulk(object):

    def get_streams(self, direction=0, **kwargs):
        # Source subnet
        src_subnet = 'fc00:0:f800:16::/64'
        src_prefix = src_subnet.split('/')[0]
        
        # Destination hosts and their SRv6 paths
        dst_configs = [
            
            {
                'subnet': 'fc00:0:f800:0::/64',
                'router': 'node00',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:2::/64',
                'router': 'node01',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:4::/64',
                'router': 'node02',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:6::/64',
                'router': 'node03',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:8::/64',
                'router': 'node04',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:10::/64',
                'router': 'node05',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:12::/64',
                'router': 'node06',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:14::/64',
                'router': 'node07',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:18::/64',
                'router': 'node09',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:20::/64',
                'router': 'node10',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:22::/64',
                'router': 'node11',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:24::/64',
                'router': 'node12',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:26::/64',
                'router': 'node13',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:28::/64',
                'router': 'node14',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:30::/64',
                'router': 'node15',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:32::/64',
                'router': 'node16',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:34::/64',
                'router': 'node17',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:36::/64',
                'router': 'node18',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:38::/64',
                'router': 'node19',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:40::/64',
                'router': 'node20',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:42::/64',
                'router': 'node21',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:44::/64',
                'router': 'node22',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:46::/64',
                'router': 'node23',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:48::/64',
                'router': 'node24',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:50::/64',
                'router': 'node25',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:52::/64',
                'router': 'node26',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:54::/64',
                'router': 'node27',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:56::/64',
                'router': 'node28',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:58::/64',
                'router': 'node29',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:60::/64',
                'router': 'node30',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:62::/64',
                'router': 'node31',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:64::/64',
                'router': 'node32',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:66::/64',
                'router': 'node33',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:68::/64',
                'router': 'node34',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:70::/64',
                'router': 'node35',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:72::/64',
                'router': 'node36',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:74::/64',
                'router': 'node37',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:76::/64',
                'router': 'node38',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:78::/64',
                'router': 'node39',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:80::/64',
                'router': 'node40',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:82::/64',
                'router': 'node41',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:84::/64',
                'router': 'node42',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:86::/64',
                'router': 'node43',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:88::/64',
                'router': 'node44',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:90::/64',
                'router': 'node45',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:92::/64',
                'router': 'node46',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:94::/64',
                'router': 'node47',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:96::/64',
                'router': 'node48',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:98::/64',
                'router': 'node49',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:100::/64',
                'router': 'node50',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:102::/64',
                'router': 'node51',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:104::/64',
                'router': 'node52',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:106::/64',
                'router': 'node53',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:108::/64',
                'router': 'node54',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:110::/64',
                'router': 'node55',
                
                'srv6_path': None
                
            },
            
            {
                'subnet': 'fc00:0:f800:112::/64',
                'router': 'node56',
                
                'srv6_path': None
                
            },
            
        ]
        
        # Create streams list
        streams = []
        
        # Bulk packet size
        packet_size = 1250
        
        # Number of flows per destination
        flows_per_dst = 10
        
        # Create streams for each destination
        for dst_id, dst_config in enumerate(dst_configs):
            dst_subnet = dst_config['subnet']
            dst_prefix = dst_subnet.split('/')[0]
            
            # Get SRv6 path for this destination
            srv6_path = dst_config['srv6_path']
            
            # If no specific path is provided, use a default pattern based on router IDs
            if not srv6_path:
                # Extract router numbers from source and destination
                src_router = 'node08'
                dst_router = dst_config['router']
                
                # Use a simplified path if no specific path is available
                srv6_path = f"fc00:0:{src_router[1:]}00:{dst_router[1:]}00::"
            
            # Create multiple bulk flows for this destination
            for flow_id in range(flows_per_dst):
                # Generate fixed host parts for src and dst to create stable flows
                src_host = 100 + flow_id
                dst_host = 100 + flow_id
                
                # Create full IPv6 addresses
                src_ip = f"{src_prefix}{src_host}"
                dst_ip = f"{dst_prefix}{dst_host}"
                
                # Create SRv6 packet with IPv6 and UDP for bulk transfer
                base_pkt = Ether()/\
                          IPv6(src=src_ip, dst=srv6_path)/\
                          IPv6ExtHdrSegmentRouting()/\
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
                    isg=10*(dst_id*flows_per_dst + flow_id),  # Inter-stream gap to avoid bursts
                    flow_stats=STLFlowStats(pg_id=dst_id*100 + flow_id)
                )
                
                streams.append(stream)

        return streams

def register():
    return STLIPv6SRv6Bulk()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6SRv6Bulk()
        streams = profile.get_streams()
        
        # Add all streams to port 0
        client.add_streams(streams, ports=[0])
        print(f"Added {len(streams)} streams to port 0")
        
        # Start traffic on port 0
        client.start(ports=[0])
        
        print("SRv6 Bulk traffic started on port 0")
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