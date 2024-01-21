import json

def generate_ipv6_address(network_prefix, subnet_index, interface_index):
    
    if subnet_index=="0":
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f"::{interface_index}"
    elif subnet_index=="eBGP":
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f"::{interface_index}"
    elif interface_index=="0":
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f":{subnet_index}::"
    else:
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f":{subnet_index}::{interface_index}"

    return ipv6_address


def generate_config(intent_file, as_name, as_data, router_name, router_data):
    configs = []

    config = "!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!\n"
    config += f"hostname {router_name}\n!\n"
    config += "boot-start-marker\nboot-end-marker\n!\n"
    config += "no aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n!\n"
    config += "no ip domain lookup\nipv6 unicast-routing\nipv6 cef\n!\n"
    config +="multilink bundle-name authenticated\n!\n"
    config += "ip tcp synwait-time 5\n!\n"
        
    # Générer les configurations d'interfaces
    for subnetwork_number, interface_name in router_data.items():
        config += f"interface {interface_name}\n"
        config += f" no ip address\n"
        if interface_name[:15]=="GigabitEthernet":
            config += " negotiation auto\n"
        elif interface_name[:12]=="FastEthernet":
            config += " duplex full\n"
        if subnetwork_number[:2] == "SN":
            ipv6_address = generate_ipv6_address(as_data['IP_range']['physical_interfaces'], subnetwork_number[2], subnetwork_number[4])
        elif subnetwork_number[:2]=="LB":
            ipv6_address = generate_ipv6_address(as_data['IP_range']['loopback_interfaces'], subnetwork_number[2], subnetwork_number[4])
        elif subnetwork_number[:4]=="eBGP":
            ipv6_address = generate_ipv6_address(as_data['IP_range']['eBGP_interfaces'], subnetwork_number[:4], subnetwork_number[5])
        config += f" ipv6 address {ipv6_address}/64\n"
        config += " ipv6 enable\n"
        if as_data["IGP"] == "RIP":
            if subnetwork_number[:2]=="SN":
                config += " ipv6 rip ripng enable\n"
        elif as_data["IGP"] == "OSPF":
            config += " ipv6 ospf 1 area 0\n"
        config += "!\n"
        
    #Générer la configuration BGP

    config += f"router bgp {as_name[2:]}\n"
    config += f" bgp router-id {router_name[1]}.{router_name[1]}.{router_name[1]}.{router_name[1]}\n"
    config += " bgp log-neighbor-changes\n"
    config += " no bgp default ipv4-unicast\n"
    for all_as_name, all_as_data in intent_file.items():
        for all_router_name, all_router_data in all_as_data["routers"].items():
            for all_subnetwork_number, all_interface_name in all_router_data.items():
                if all_as_name == as_name and all_router_name != router_name:
                    if all_subnetwork_number[:2]=="LB":
                        ipv6_address = generate_ipv6_address(all_as_data['IP_range']['loopback_interfaces'], all_subnetwork_number[2], all_subnetwork_number[4])
                        config += f" neighbor {ipv6_address} remote-as {all_as_name[2:]}\n"
                        config += f" neighbor {ipv6_address} update-source Loopback0\n"
                elif all_as_name != as_name:
                    if all_subnetwork_number[:4]=="eBGP":
                        for key in router_data.keys():
                            if key.startswith("eBGP_"):
                                ipv6_address = generate_ipv6_address(all_as_data['IP_range']['eBGP_interfaces'], all_subnetwork_number[:4], all_subnetwork_number[5])
                                config += f" neighbor {ipv6_address} remote-as {all_as_name[2:]}\n"
    config +=" !\n"
    config += " address-family ipv4\n exit-address-family\n !\n"
    config += " address-family ipv6\n"

    for all_as_name, all_as_data in intent_file.items():
        for all_router_name, all_router_data in all_as_data["routers"].items():
            for all_subnetwork_number, all_interface_name in all_router_data.items():
                if all_as_name == as_name:
                    if all_subnetwork_number[:2] == "SN":
                        ipv6_address = generate_ipv6_address(all_as_data['IP_range']['physical_interfaces'], all_subnetwork_number[2], "0")
                        config += f"  network {ipv6_address}/64\n"
                    if all_router_name != router_name:
                        if all_subnetwork_number[:2]=="LB":
                            ipv6_address = generate_ipv6_address(all_as_data['IP_range']['loopback_interfaces'], all_subnetwork_number[2], all_subnetwork_number[4])
                            config += f"  neighbor {ipv6_address} activate\n"
                elif all_as_name != as_name:
                    if all_subnetwork_number[:4]=="eBGP":
                        for key in router_data.keys():
                            if key.startswith("eBGP_"):
                                ipv6_address = generate_ipv6_address(all_as_data['IP_range']['eBGP_interfaces'], all_subnetwork_number[:4], all_subnetwork_number[5])
                                config += f"  neighbor {ipv6_address} activate\n"
    
    config += " exit address-family\n!\n"
    config += "ip forward-protocol nd\n!\n"
    config += "no ip http server\nno ip http secure-server\n!\n"

    # Générer les configurations spécifiques en fonction de l'IGP
    if as_data["IGP"] == "RIP":
        config += "!\nrouter rip ripng\n"
        config += " redistribute connected\n"

    elif as_data["IGP"] == "OSPF":
        config += "!\nipv6 router ospf 1\n"
        config += f" router-id {router_name[1:]}.{router_name[1:]}.{router_name[1:]}.{router_name[1:]}\n"
        config += " passive-interface Loopback0\n"
    
    config += "!\n!\ncontrol-plane\n!\n"
    config += "line con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\n"
    config += "line aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\n"
    config += "line vty 0 4\n login\n!\n!\nend"

    """
    # Générer la configuration BGP commune pour tous les routeurs
    if "eBGP" in intent_file:
        for link in intent_file["eBGP"]["links"]:
            config += f"router bgp <AS-X>\n"
            config += f" neighbor {link[0]} remote-as <AS-Y>\n"
            config += f" neighbor {link[0]} update-source Loopback0\n"
            # Ajouter d'autres configurations eBGP si nécessaire

        # Générer la configuration spécifique pour le routeur
        config += f"router bgp {as_data['BGP_AS']}\n"
        config += f" bgp router-id 1.1.1.1\n"  # Remplacer par un ID unique par routeur
        config += f" bgp log-neighbor-changes\n"
        config += f" no bgp default ipv4-unicast\n"

        for neighbor in as_data.get("BGP_neighbors", []):
            config += f" neighbor {neighbor} remote-as {as_data['BGP_AS']}\n"
            config += f" neighbor {neighbor} update-source Loopback0\n"
            # Ajouter d'autres configurations BGP si nécessaire

        # Générer les configurations de réseau pour BGP
        config += " address-family ipv4\n"
        config += " exit-address-family\n"
        config += " address-family ipv6\n"
        config += f"  network {as_data['IP_range']['physical_interfaces']}\n"
        config += "  neighbor 2001:100::2 activate\n"
        config += "  neighbor 2001:100::3 activate\n"
        config += "  neighbor 2001:100:100:100::2 activate\n"
        config += " exit-address-family\n"
        config += "!\n"

        """

    return config

def main():
    with open("intent.json", "r") as file:
        intent_file = json.load(file)

    for as_name, as_data in intent_file.items():
        for router_name, router_data in as_data["routers"].items():
            router_config = generate_config(intent_file, as_name, as_data, router_name, router_data)
            with open(f"i{router_name[1]}_startup-config.cfg", "w") as file:
                file.write(router_config)

if __name__ == "__main__":
    main()
