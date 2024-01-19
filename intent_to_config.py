import json
#<<<<<<< HEAD
area = 0
def generate_config(as_info,R):
    configs = []

    for as_name, as_data in as_info.items():
        for router_name, router_data in as_data["routers"].items():
            if router_name == R:
                config = "version 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!\n"
                config += f"hostname {router_name}\n!\n"
                config += "boot-start-marker\nboot-end-marker\n!\n"
                config += "no aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n!\n"
                config += "no ip domain lookup\nipv6 unicast-routing\nipv6 cef\n!\n"
                config +="multilink bundle-name authenticated\n!\n"
                config += "ip tcp synwait-time 5\n!\n"
            
            # Générer les configurations d'interfaces
                for subnetwork_number, interface_name in router_data.items():
                    config += f"interface {interface_name}\n"
                    config += " no ip address\n"
                    if interface_name == "GigabitEthernet1/0" or "GigabitEthernet2/0" or "GigabitEthernet3/0" or "GigabitEthernet4/0":
                        config += " negociation auto\n"
                    elif interface_name == "FastEthernet0/0":
                        config += " duplex full\n"
                    config += f" ipv6 address {as_data['IP_range']['physical_interfaces']} link-local\n"
                    config += f" ipv6 address {as_data['IP_range']['physical_interfaces']}\n"
                    config += " ipv6 enable\n" 
                        # Ajouter d'autres configurations d'interface si nécessaire
                    if as_data["IGP"] == "RIP":
                        config += " ipv6 rip ripng enable\n!\n"
                        # Ajouter d'autres paramètres RIP si nécessaire
                    elif as_data["IGP"] == "OSPF":
                        config += f" ipv6 ospf 1 area 0\n!\n"
                config += """interface Loopback0
 no ip address
 ipv6 address 2001:100::1/128
 ipv6 enable
!\n"""  
        if R in list(as_data["neighbor"].keys()) :
            config += """interface FastEthernet0/0
 no ip address
 duplex full
 ipv6 address 2001:100:100:100::1/64
 ipv6 enable
!\n"""
            # Générer la configuration BGP commune pour tous les routeurs
        config += f"router bgp {as_name[2:]}\n"
        number = R[1:]
        config += f" bgp router-id {number}.{number}.{number}.{number}\n"
        config += " bgp log-neighbor-changes\n"
        config += " no bgp default ipv4-unicast"
        #for
        #config += f" neighbor {} remote-as <AS-Y>\n"
        #if as_info.get("AS100", {}).get("neighbor", {})==
        #config += f" neighbor {} update-source Loopback0\n"

        # Générer les configurations de réseau pour BGP
        config += " address-family ipv4\n"
        config += " exit-address-family\n!\n"
        config += " address-family ipv6\n"

        config += " exit-address-family\n"
        config += " !\n"
        config += """ ip forward-protocol nd\n!\nno ip http server\nno ip http secure-server\n!
 ipv6 router rip ripng\nredistribute connected\n!\ncontrol-plane\n!\nline con 0
 exec-timeout 0 0\nprivilege level 15\nlogging synchronous\nstopbits 1\nline aux 0\nexec-timeout 0 0
 privilege level 15\nlogging synchronous\nstopbits 1\nline vty 0 4\nlogin\n!\nend\n"""
        configs.append(config)
    return configs

def main():
    with open("intent.json", "r") as file:
        as_info = json.load(file)
    routeur = ["R1","R2","R3","R4","R5","R6"]
    taille = len(routeur)
    for i in range(taille):
        router_configs = generate_config(as_info, routeur[i])

    # Écrire les configurations dans des fichiers séparés
        for config, (as_name, as_data) in zip(router_configs, as_info.items()):
            with open(f'config_{routeur[i]}.txt', "w") as file:
                file.write(config)
           

#======
def generate_ipv6_address(network_prefix, subnet_index, interface_index):
    
    if subnet_index=="0":
        ipv6_address=network_prefix[:10]+f"{interface_index}/64"
    elif subnet_index=="eBGP":
        ipv6_address=network_prefix[:18]+f"{interface_index}/64"
    else:
        ipv6_address=network_prefix[:13]+f"{subnet_index}::{interface_index}/64"

    return ipv6_address

def generate_config(intent_file, as_name, as_data, router_name, router_data):
    configs = []

    config = "version 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!\n"
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
        if subnetwork_number[:2] == "SB":
            ipv6_address = generate_ipv6_address(as_data['IP_range']['physical_interfaces'], subnetwork_number[2], subnetwork_number[4])
        elif subnetwork_number[:2]=="LB":
            ipv6_address = generate_ipv6_address(as_data['IP_range']['loopback_interfaces'], subnetwork_number[2], subnetwork_number[4])
        elif subnetwork_number[:4]=="eBGP":
            ipv6_address = generate_ipv6_address(as_data['IP_range']['eBGP_interfaces'], subnetwork_number[:4], subnetwork_number[5])
        config += f" ipv6 address {ipv6_address}\n"
        config += " ipv6 enable\n"
        if as_data["IGP"] == "RIP":
            if subnetwork_number[:2]=="SB":
                config += " ipv6 rip ripng enable\n"
        elif as_data["IGP"] == "OSPF":
            config += " ipv6 ospf 1 area 0\n"
        config += "!\n"
            

    # Générer les configurations spécifiques en fonction de l'IGP
    if as_data["IGP"] == "RIP":
        config += "!\nrouter rip ripng\n"
        config += " redistribute connected\n"

    elif as_data["IGP"] == "OSPF":
        config += "!\nipv6 router ospf 1\n"
        config += " router-id 1.1.1.1\n"
        config += " passive-interface Loopback0\n"

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

    return config

def main():
    with open("intent.json", "r") as file:
        intent_file = json.load(file)

    for as_name, as_data in intent_file.items():
        for router_name, router_data in as_data["routers"].items():
            router_config = generate_config(intent_file, as_name, as_data, router_name, router_data)
            with open(f"config_{router_name}.txt", "w") as file:
                file.write(router_config)
#>>>>>>> e7a278155a55681e5d52932aa53597dd58e82f7a

if __name__ == "__main__":
    main()
