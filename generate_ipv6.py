import json

def generate_ipv6_address(network_prefix, subnet_index, interface_index):
    """
    Génère une adresse IPv6 basée sur une adresse de base, l'index du sous-réseau
    et l'index de l'interface dans le sous-réseau.
    """
    # Adresse de l'interface
    ipv6_address=network_prefix[:13]+f"{subnet_index}::{interface_index}/64"

    return ipv6_address


ipv6_address = generate_ipv6_address("2001:100:100::", 1, 1)
print(ipv6_address)