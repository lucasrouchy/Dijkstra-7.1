import sys
import json
import math  # If you want to use math.inf for infinity
import socket as s
import struct
def ipv4_to_value(ipv4_addr):
    byteIP = s.inet_aton(ipv4_addr)
    return struct.unpack('!L', byteIP)[0]

def get_subnet_mask_value(slash):
    ip, network_bits = slash.split('/')
    network = int(network_bits)
    host = 32 - network
    mask = (2**network) - 1
    return mask << host

def ips_same_subnet(ip1, ip2, slash):
    ip1_val = ipv4_to_value(ip1)
    ip2_val = ipv4_to_value(ip2)
    mask = get_subnet_mask_value(slash)
    net1 = ip1_val & mask
    net2 = ip2_val & mask
    return (net1 == net2)

def find_router_for_ip(routers, ip):
    for ip_value, mask_value in routers.items():
        if ips_same_subnet(ip_value, ip, mask_value['netmask']):
            return ip_value

def distance_to_neighbors(routers, current, neighbor):
    cur = routers[current]
    cur_connections = cur['connections']
    cur_neighbor = cur_connections[neighbor]
    n_dist = cur_neighbor['ad']
    return n_dist

def dijkstras_shortest_path(routers, src_ip, dest_ip):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """
    src_ip = find_router_for_ip(routers, src_ip)
    dest_ip = find_router_for_ip(routers, dest_ip)

    
    unvisited = set()
    dist = {}
    parent = {}  

    for r in routers:
        parent[r] = None
        dist[r] = math.inf  
        unvisited.add(r)
    # start with dist of 0
    dist[src_ip] = 0

    
    while unvisited:
        # current node is the node with the shortest distance that in the unvisited set.
        current = min(unvisited, key=dist.get)
        unvisited.remove(current)
        
        for n in routers[current]["connections"]:
            if n in unvisited:
                # shortest path
                n_dist = distance_to_neighbors(routers, current, n)
                alt_dist = dist[current] + n_dist
                # if the alternative distance is smaller then update new shortest path.
                if alt_dist < dist[n]:
                    dist[n] = alt_dist
                    parent[n] = current
    
    
    path = []
    current = dest_ip
    while current != src_ip:
        path.append(current)
        current = parent[current]
    if path:
        path.append(current)
        path.reverse()
    
    return path

#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
