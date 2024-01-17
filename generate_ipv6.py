import json

def generate_ipv6_address(base_address, subnet_index, interface_index):
    """
    Génère une adresse IPv6 basée sur une adresse de base, l'index du sous-réseau
    et l'index de l'interface dans le sous-réseau.
    """
    # Séparer les parties de l'adresse de base
    base_address_parts = base_address.split("::")
    print(base_address_parts)

    # Ajouter l'index du sous-réseau à la quatrième partie
    base_address_parts[3] += f"{subnet_index}"

    # Ajouter l'index de l'interface à la sixième partie
    base_address_parts[5] += f"{interface_index}"

    # Formater l'adresse IPv6
    ipv6_address = ":".join(base_address_parts)
    return f"{ipv6_address}/64"


ipv6_address = generate_ipv6_address("2001:100:100::", 1, 1)
print(ipv6_address)