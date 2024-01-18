import json

def generate_ipv6_address(network_prefix, subnet_index, interface_index):
    
    if subnet_index==0:
        ipv6_address=network_prefix[:10]+f"{interface_index}/64"
    elif subnet_index=="eBGP":
        ipv6_address=network_prefix[:18]+f"{interface_index}/64"
    else:
        ipv6_address=network_prefix[:13]+f"{subnet_index}::{interface_index}/64"

    return ipv6_address


ipv6_address = generate_ipv6_address("2001:100::/64", 0, 1)
print(ipv6_address)