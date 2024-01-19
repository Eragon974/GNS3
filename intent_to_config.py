import json
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
           

if __name__ == "__main__":
    main()
