from trex_stl_lib.api import *
import random

class STLIPv6SRv6(object):

    def get_streams(self, direction=0, **kwargs):
        # Source subnet
        src_subnet = 'fc00:0:f800:6::/64'
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
                'subnet': 'fc00:0:f800:16::/64',
                'router': 'node08',
                
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
        
        # IMIX packet sizes (in bytes)
        imix_sizes = 
        # IMIX distribution weights
        imix_weights = 
        
        # Create streams for each destination
        for dst_id, dst_config in enumerate(dst_configs):
            dst_subnet = dst_config['subnet']
            dst_prefix = dst_subnet.split('/')[0]
            
            # Get SRv6 path for this destination
            srv6_path = dst_config['srv6_path']
            
            # If no specific path is provided, use a default pattern based on router IDs
            if not srv6_path:
                # Extract router numbers from source and destination
                src_router = 'node03'
                dst_router = dst_config['router']
                
                # Use a simplified path if no specific path is available
                srv6_path = f"fc00:0:{src_router[1:]}00:{dst_router[1:]}00::"
            
            # Create IMIX streams for this destination
            for size_id, (size, weight) in enumerate(zip(imix_sizes, imix_weights)):
                # Generate random host parts for src and dst
                src_host = random.randint(1, 1000)
                dst_host = random.randint(1, 1000)
                
                # Create full IPv6 addresses
                src_ip = f"{src_prefix}{src_host}"
                dst_ip = f"{dst_prefix}{dst_host}"
                
                # Create SRv6 packet with IPv6 and ICMPv6
                base_pkt = Ether()/\
                          IPv6(src=src_ip, dst=srv6_path)/\
                          IPv6ExtHdrSegmentRouting()/\
                          IPv6(src=src_ip, dst=dst_ip)/\
                          ICMPv6EchoRequest()
                
                # Calculate padding to reach desired size
                pad_size = max(0, size - len(base_pkt))
                
                # Create a stream with the packet
                pkt = STLPktBuilder(pkt=base_pkt/('x' * pad_size))
                
                # Create stream with appropriate weight
                stream = STLStream(
                    packet=pkt,
                    mode=STLTXCont(pps=*weight),
                    isg=10*dst_id,  # Inter-stream gap to avoid bursts
                    flow_stats=STLFlowStats(pg_id=dst_id*10 + size_id)
                )
                
                streams.append(stream)
            
            # For VM streams, create a larger base packet to ensure enough space
            vm_base_pkt = Ether()/\
                         IPv6(src=src_prefix+"1", dst=srv6_path)/\
                         IPv6ExtHdrSegmentRouting()/\
                         IPv6(src=src_prefix+"1", dst=dst_prefix+"1")/\
                         ICMPv6EchoRequest()/\
                         Raw('x' * 64)  # Add padding to ensure packet is large enough
            
            # Add VM (Variable Machine) to randomize source and destination IPs
            vm = STLScVmRaw([
                # Randomize source IP in inner header
                STLVmFlowVar(name="src_addr", min_value=1, max_value=1000, size=4, op="inc"),
                STLVmWrFlowVar(fv_name="src_addr", pkt_offset=54, offset_fixup=12),  # Adjust offset for inner IPv6
                
                # Randomize destination IP in inner header
                STLVmFlowVar(name="dst_addr", min_value=1, max_value=1000, size=4, op="inc"),
                STLVmWrFlowVar(fv_name="dst_addr", pkt_offset=70, offset_fixup=12)  # Adjust offset for inner IPv6
            ])
            
            # Create a stream with VM for IP randomization
            vm_pkt = STLPktBuilder(pkt=vm_base_pkt, vm=vm)
            
            vm_stream = STLStream(
                packet=vm_pkt,
                mode=STLTXCont(pps=300),
                flow_stats=STLFlowStats(pg_id=dst_id*10 + 9)
            )
            
            streams.append(vm_stream)

        return streams

def register():
    return STLIPv6SRv6()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6SRv6()
        streams = profile.get_streams()
        
        # Add all streams to port 0
        client.add_streams(streams, ports=[0])
        print(f"Added {len(streams)} streams to port 0")
        
        # Start traffic on port 0
        client.start(ports=[0])
        
        print("SRv6 IMIX traffic started on port 0")
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