import sys

# adding trex location to the system path
sys.path.insert(0, '/home/cisco/trex/v3.06/trex_client/interactive/')

from trex_stl_lib.api import *

# host00
a = STLClient(server = "198.18.4.200")
a.connect()
a.reset()
a.stop(ports = [0])

# host01
a = STLClient(server = "198.18.4.201")
a.connect()
a.reset()
a.stop(ports = [0])

# host02
a = STLClient(server = "198.18.4.202")
a.connect()
a.reset()
a.stop(ports = [0])

# host03
a = STLClient(server = "198.18.4.203")
a.connect()
a.reset()
a.stop(ports = [0])

# host04
a = STLClient(server = "198.18.4.204")
a.connect()
a.reset()
a.stop(ports = [0])

# host05
a = STLClient(server = "198.18.4.205")
a.connect()
a.reset()
a.stop(ports = [0])

# host06
a = STLClient(server = "198.18.4.206")
a.connect()
a.reset()
a.stop(ports = [0])

# host07
a = STLClient(server = "198.18.4.207")
a.connect()
a.reset()
a.stop(ports = [0])

# host08
a = STLClient(server = "198.18.4.208")
a.connect()
a.reset()
a.stop(ports = [0])

# host09
a = STLClient(server = "198.18.4.209")
a.connect()
a.reset()
a.stop(ports = [0])

