from trex_stl_lib.api import *

class STLIPv6Bulk(object):

    def __init__(self):
        # Source and destination IPv6 addresses
        self.src_addr = 'fc00:0:f800:0::2'
        self.dst_subnets = [
            'fc00:0:f800:30::',
            'fc00:0:f800:64::',
            'fc00:0:f800:96::',
            'fc00:0:f800:12::'
        ]        
        # Packet size and rate
        self.packet_size = 1250
        self.pps = 1000

    def create_stream(self, dst_addr, stream_id):
        # Create base packet with IPv6
        base_pkt = Ether() / IPv6(src=self.src_addr, dst=dst_addr) / UDP(sport=1025, dport=1025)
        
        # Pad to desired size
        pad_size = max(0, self.packet_size - len(base_pkt))
        if pad_size > 0:
            base_pkt = base_pkt / ('x' * pad_size)
        
        # Create stream
        return STLStream(
            packet=STLPktBuilder(pkt=base_pkt),
            mode=STLTXCont(pps=self.pps),
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
                stream = self.create_stream(
                    dst_addr,
                    stream_id
                )
                streams.append(stream)
                stream_id += 1
        
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
