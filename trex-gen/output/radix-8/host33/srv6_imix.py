from trex_stl_lib.api import *
import random

class STLSRv6IMIX(object):

    def get_streams(self, direction=0, **kwargs):
        # Destination subnet configurations
        dst_subnets = ['fc00:0:f800:0::/64', 'fc00:0:f800:2::/64', 'fc00:0:f800:4::/64', 'fc00:0:f800:6::/64', 'fc00:0:f800:8::/64', 'fc00:0:f800:10::/64', 'fc00:0:f800:12::/64', 'fc00:0:f800:14::/64']
        
        # Source subnet
        src_subnet = 'fc00:0:f800:66::/64'
        
        # SRv6 encapsulation format
        srv6_encap_format = 'fc00:0:{usid1_hex}:{usid2_hex}:{usid3_hex}:{usid4_hex}:{usid5_hex}:{usid6_hex}::'
        
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
            
            # Create SRv6 segment list (simplified for demo)
            # In a real scenario, this would be based on the topology
            usid1_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid2_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid3_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid4_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid5_hex = format(random.randint(1, 255), 'x').zfill(4)
            usid6_hex = format(random.randint(1, 255), 'x').zfill(4)
            
            srv6_sid = srv6_encap_format.format(
                usid1_hex=usid1_hex,
                usid2_hex=usid2_hex,
                usid3_hex=usid3_hex,
                usid4_hex=usid4_hex,
                usid5_hex=usid5_hex,
                usid6_hex=usid6_hex
            )
            
            # Create streams for each packet size in IMIX
            for size_id, (size, weight) in enumerate(zip(imix_sizes, imix_weights)):
                # Calculate packets per second for this stream
                pps = int(pps_base * weight)
                
                # Create IPv6 header with VM
                vm = STLVM()
                
                # Add source IPv6 address variation
                vm.var(name="src", min_value=src_prefix + "::2", 
                       max_value=src_prefix + "::ffff", size=16, op="random")
                vm.write(fv_name="src", pkt_offset="IPv6.src")
                
                # Add destination IPv6 address variation
                vm.var(name="dst", min_value=dst_prefix + "::2", 
                       max_value=dst_prefix + "::ffff", size=16, op="random")
                vm.write(fv_name="dst", pkt_offset="IPv6.dst")
                
                # Create base packet with SRv6 header
                base_pkt = (Ether() / 
                           IPv6(src=src_prefix + "::1", dst=srv6_sid) / 
                           IPv6ExtHdrSegmentRouting(addresses=[srv6_sid, dst_prefix + "::1"]) /
                           IPv6(src=src_prefix + "::1", dst=dst_prefix + "::1") / 
                           UDP())
                
                # Pad to desired size
                pad_size = max(0, size - len(base_pkt))
                if pad_size > 0:
                    base_pkt = base_pkt / ('x' * pad_size)
                
                # Create stream with VM
                vm_stream = STLStream(
                    packet=STLPktBuilder(pkt=base_pkt, vm=vm),
                    mode=STLTXCont(pps=pps),
                    flow_stats=STLFlowStats(pg_id=subnet_id * 10 + size_id)
                )
                
                streams.append(vm_stream)

        return streams

def register():
    return STLSRv6IMIX()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLSRv6IMIX()
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
