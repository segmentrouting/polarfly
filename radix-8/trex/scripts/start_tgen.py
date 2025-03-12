import sys

# adding trex location to the system path
sys.path.insert(0, '/home/cisco/trex/v3.06/trex_client/interactive/')

from trex_stl_lib.api import *

# host00
a = STLClient(server = "198.18.4.200")
a.connect()
a.reset()
a.start_line (" -f ../host00/imix.py -m 20mbps --port 0")

# host01
a = STLClient(server = "198.18.4.201")
a.connect()
a.reset()
a.start_line (" -f ../host01/imix.py -m 10mbps --port 0")

# host02
a = STLClient(server = "198.18.4.202")
a.connect()
a.reset()
a.start_line (" -f ../host02/imix.py -m 20mbps --port 0")

# host03
a = STLClient(server = "198.18.4.203")
a.connect()
a.reset()
a.start_line (" -f ../host03/imix.py -m 10mbps --port 0")

# host04
a = STLClient(server = "198.18.4.204")
a.connect()
a.reset()
a.start_line (" -f ../host04/imix.py -m 10mbps --port 0")

# host05
a = STLClient(server = "198.18.4.205")
a.connect()
a.reset()
a.start_line (" -f ../host05/imix.py -m 20mbps --port 0")

# host06
a = STLClient(server = "198.18.4.206")
a.connect()
a.reset()
a.start_line (" -f ../host06/imix.py -m 10mbps --port 0")

# host07
a = STLClient(server = "198.18.4.207")
a.connect()
a.reset()
a.start_line (" -f ../host07/imix.py -m 20mbps --port 0")

# host08
a = STLClient(server = "198.18.4.208")
a.connect()
a.reset()
a.start_line (" -f ../host08/imix.py -m 10mbps --port 0")

# host09
a = STLClient(server = "198.18.4.209")
a.connect()
a.reset()
a.start_line (" -f ../host09/imix.py -m 10mbps --port 0")

# host10
a = STLClient(server = "198.18.4.210")
a.connect()
a.reset()
a.start_line (" -f ../host10/imix.py -m 10mbps --port 0")

# host11
a = STLClient(server = "198.18.4.211")
a.connect()
a.reset()
a.start_line (" -f ../host11/imix.py -m 10mbps --port 0")

# host12
a = STLClient(server = "198.18.4.212")
a.connect()
a.reset()
a.start_line (" -f ../host12/imix.py -m 10mbps --port 0")

# host13
a = STLClient(server = "198.18.4.213")
a.connect()
a.reset()
a.start_line (" -f ../host13/imix.py -m 10mbps --port 0")

# host14
a = STLClient(server = "198.18.4.214")
a.connect()
a.reset()
a.start_line (" -f ../host14/imix.py -m 10mbps --port 0")

# host15
a = STLClient(server = "198.18.4.215")
a.connect()
a.reset()
a.start_line (" -f ../host15/imix.py -m 10mbps --port 0")

# host16
a = STLClient(server = "198.18.4.216")
a.connect()
a.reset()
a.start_line (" -f ../host16/imix.py -m 10mbps --port 0")

# host17
a = STLClient(server = "198.18.4.217")
a.connect()
a.reset()
a.start_line (" -f ../host17/imix.py -m 10mbps --port 0")

# host18
a = STLClient(server = "198.18.4.218")
a.connect()
a.reset()
a.start_line (" -f ../host18/imix.py -m 10mbps --port 0")

# host19
a = STLClient(server = "198.18.4.219")
a.connect()
a.reset()
a.start_line (" -f ../host19/imix.py -m 10mbps --port 0")

# host20
a = STLClient(server = "198.18.4.220")
a.connect()
a.reset()
a.start_line (" -f ../host20/imix.py -m 10mbps --port 0")

# host21
a = STLClient(server = "198.18.4.221")
a.connect()
a.reset()
a.start_line (" -f ../host21/imix.py -m 10mbps --port 0")

# host22
a = STLClient(server = "198.18.4.222")
a.connect()
a.reset()
a.start_line (" -f ../host22/imix.py -m 10mbps --port 0")

# host23
a = STLClient(server = "198.18.4.223")
a.connect()
a.reset()
a.start_line (" -f ../host23/imix.py -m 10mbps --port 0")

# host24
a = STLClient(server = "198.18.4.224")
a.connect()
a.reset()
a.start_line (" -f ../host24/imix.py -m 10mbps --port 0")

# host25
a = STLClient(server = "198.18.4.225")
a.connect()
a.reset()
a.start_line (" -f ../host25/imix.py -m 10mbps --port 0")

# host26
a = STLClient(server = "198.18.4.226")
a.connect()
a.reset()
a.start_line (" -f ../host26/imix.py -m 10mbps --port 0")

# host27
a = STLClient(server = "198.18.4.227")
a.connect()
a.reset()
a.start_line (" -f ../host27/imix.py -m 10mbps --port 0")

# host28
a = STLClient(server = "198.18.4.228")
a.connect()
a.reset()
a.start_line (" -f ../host28/imix.py -m 10mbps --port 0")
















