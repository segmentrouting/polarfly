from trex_stl_lib.api import *
import random

class STLIPv6(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = [
            
            'fc00:0:f800:0::/64',
            
            'fc00:0:f800:2::/64',
            
            'fc00:0:f800:4::/64',
            
            'fc00:0:f800:6::/64',
            
            'fc00:0:f800:8::/64',
            
            'fc00:0:f800:10::/64',
            
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
        src_subnet = 'fc00:0:f800:68::/64'
        
        # Create streams list
        streams = []
        
        # IMIX packet sizes (in bytes)
        imix_sizes = 
        # IMIX distribution weights
        imix_weights = 
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Create IMIX streams for this destination
            for size_id, (size, weight) in enumerate(zip(imix_sizes, imix_weights)):
                # Generate random host parts for src and dst
                src_host = random.randint(1, 1000)
                dst_host = random.randint(1, 1000)
                
                # Create full IPv6 addresses
                src_ip = f"{src_prefix}{src_host}"
                dst_ip = f"{dst_prefix}{dst_host}"
                
                # Create packet with IPv6 and ICMPv6
                base_pkt = Ether()/\
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
                    isg=10*subnet_id,  # Inter-stream gap to avoid bursts
                    flow_stats=STLFlowStats(pg_id=subnet_id*10 + size_id)
                )
                
                streams.append(stream)
            
            # For VM streams, create a larger base packet to ensure enough space
            vm_base_pkt = Ether()/\
                         IPv6(src=src_prefix+"1", dst=dst_prefix+"1")/\
                         ICMPv6EchoRequest()/\
                         Raw('x' * 64)  # Add padding to ensure packet is large enough
            
            # Add VM (Variable Machine) to randomize source and destination IPs for this subnet
            vm = STLScVmRaw([
                # Randomize source IP
                STLVmFlowVar(name="src_addr", min_value=1, max_value=1000, size=4, op="inc"),
                STLVmWrFlowVar(fv_name="src_addr", pkt_offset="IPv6.src", offset_fixup=12),
                
                # Randomize destination IP
                STLVmFlowVar(name="dst_addr", min_value=1, max_value=1000, size=4, op="inc"),
                STLVmWrFlowVar(fv_name="dst_addr", pkt_offset="IPv6.dst", offset_fixup=12)
            ])
            
            # Create a stream with VM for IP randomization
            vm_pkt = STLPktBuilder(pkt=vm_base_pkt, vm=vm)
            
            vm_stream = STLStream(
                packet=vm_pkt,
                mode=STLTXCont(pps=300),
                flow_stats=STLFlowStats(pg_id=subnet_id*10 + 9)
            )
            
            streams.append(vm_stream)

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