from trex_stl_lib.api import *
import random

class STLIPv6Bulk(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = [

        ]
        
        # Source subnet
        src_subnet = ''
        
        # Parse source network prefix
        src_prefix = src_subnet.split('/')[0]
        
        # Create streams list
        streams = []
        
        # Create streams for each destination subnet
        for subnet_id, dst_subnet in enumerate(dst_subnets):
            # Parse destination network prefix
            dst_prefix = dst_subnet.split('/')[0]
            
            # Generate random host parts for src and dst
            src_host = random.randint(1, 1000)
            dst_host = random.randint(1, 1000)
            
            # Create full IPv6 addresses
            src_ip = f"{src_prefix}{src_host}"
            dst_ip = f"{dst_prefix}{dst_host}"
            
            # Create packet with IPv6 and UDP with large payload
            base_pkt = Ether()/\
                      IPv6(src=src_ip, dst=dst_ip)/\
                      UDP(dport=4000+subnet_id, sport=1000+subnet_id)/\
                      ('x' * 1400)  # Large payload for bulk traffic
            
            # Create a stream with the packet
            pkt = STLPktBuilder(pkt=base_pkt)
            
            # Create high-bandwidth stream
            stream = STLStream(
                packet=pkt,
                mode=STLTXCont(percentage=10.0),  # 10% of line rate
                isg=10*subnet_id,  # Inter-stream gap to avoid bursts
                flow_stats=STLFlowStats(pg_id=subnet_id)
            )
            
            streams.append(stream)
            
            # Add VM (Variable Machine) to randomize source and destination IPs for this subnet
            vm_base_pkt = Ether()/\
                         IPv6(src=src_prefix+"1", dst=dst_prefix+"1")/\
                         UDP(dport=4000+subnet_id, sport=1000+subnet_id)/\
                         ('x' * 1400)
            
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
                mode=STLTXCont(pps=1000),
                flow_stats=STLFlowStats(pg_id=100+subnet_id)
            )
            
            streams.append(vm_stream)

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
