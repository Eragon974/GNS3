import json

def generate_ipv6_address(network_prefix, subnet_index, interface_index):
    
    if subnet_index=="0":
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f"::{interface_index}/64"
    elif subnet_index=="eBGP":
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f"::{interface_index}/64"
    elif interface_index=="0":
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f"::{subnet_index}/64"
    else:
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f":{subnet_index}::{interface_index}/64"

    return ipv6_address


ipv6_address = generate_ipv6_address("2001:100:100::/64", "1", "0")
print(ipv6_address)