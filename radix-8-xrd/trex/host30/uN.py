from trex_stl_lib.api import *

class STLIPv6(object):

    def get_streams(self, direction=0, **kwargs):
        # Source address
        src_addr = 'fc00:0:f800::2'
        
        # Destination configurations with both inner and outer IPv6 addresses
        dst_config = [
            {
                'dst': 'fc00:0:f801::2',
                'srv6_dst': 'fc00:0:1004:1008:1012:1016::'
            },
            {
                'dst': 'fc00:0:f801:4::2',
                'srv6_dst': 'fc00:0:1005:1009:1013:1017::'
            },
            {
                'dst': 'fc00:0:f801:8::2',
                'srv6_dst': 'fc00:0:1006:1010:1014:1018::'
            },
            {
                'dst': 'fc00:0:f801:c::2',
                'srv6_dst': 'fc00:0:1007:1011:1015:1019::'
            }
        ]

        # Create streams list
        streams = []
        
        # Create a stream for each destination
        for stream_id, addresses in enumerate(dst_config):
            # Create packet with outer IPv6 (SRv6) and inner IPv6
            base_pkt = Ether()/\
                      IPv6(src=src_addr, dst=addresses['srv6_dst'])/\
                      IPv6(src=src_addr, dst=addresses['dst'])/\
                      UDP(dport=12345, sport=54321)
            
            # Create a packet size that will result in ~10Mbps at 1000pps
            pad_size = 1250 - len(base_pkt)
            
            # Create a stream with the packet
            pkt = STLPktBuilder(pkt=base_pkt/('x' * pad_size))
            
            # Add stream with a unique ID and small inter-stream gap to avoid bursts
            streams.append(STLStream(
                packet=pkt, 
                mode=STLTXCont(pps=1000),  # 1000 pps for ~10Mbps
                isg=10*stream_id,  # Inter-stream gap
                flow_stats=STLFlowStats(pg_id=stream_id)
            ))

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