from trex_stl_lib.api import *

class STLIPv6Imix(object):

    def __init__(self):
        # Source and destination IPv6 addresses
        self.src_addr = 'fc00:0:f800::2'
        self.dst_subnets = [
            'fc00:0:f800:30::',
            'fc00:0:f800:94::'
        ]
        
        # IMIX properties
        self.imix_table = [
            {'size': 128, 'pps': 58, 'isg': 0},
            {'size': 570, 'pps': 33, 'isg': 0.1},
            {'size': 1280, 'pps': 8, 'isg': 0.2}
        ]

    def create_stream(self, dst_addr, size, pps, isg, stream_id):
        # Create base packet with IPv6
        base_pkt = Ether() / IPv6(src=self.src_addr, dst=dst_addr) / UDP(sport=1025, dport=1025)
        
        # Pad to desired size
        pad_size = max(0, size - len(base_pkt))
        if pad_size > 0:
            base_pkt = base_pkt / ('x' * pad_size)
        
        # Create stream
        return STLStream(
            isg=isg,
            packet=STLPktBuilder(pkt=base_pkt),
            mode=STLTXCont(pps=pps),
            flow_stats=STLFlowStats(pg_id=stream_id)
        )

    def get_streams(self, direction=0, **kwargs):
        streams = []
        stream_id = 0
        
        # Create streams for each destination subnet and IMIX size
        for dst_prefix in self.dst_subnets:
            # Create multiple destination addresses for this subnet
            dst_addrs = [f"{dst_prefix}{i}" for i in range(2, 16)]
            
            for dst_addr in dst_addrs:
                for imix in self.imix_table:
                    stream = self.create_stream(
                        dst_addr,
                        imix['size'],
                        imix['pps'],
                        imix['isg'],
                        stream_id
                    )
                    streams.append(stream)
                    stream_id += 1
        
        return streams

def register():
    return STLIPv6Imix()

def main():
    # Create client
    client = STLClient()
    
    try:
        # Connect to server
        client.connect()
        
        # Reset ports
        client.reset()
        
        # Create traffic profile
        profile = STLIPv6Imix()
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