import os
import shutil
import json
import glob

def generate_ipv6_address(network_prefix, subnet_index, interface_index):
    
    if subnet_index=="0": #loopback interfaces
        network_prefix_cut = network_prefix[:network_prefix.index('::')] 
        ipv6_address=network_prefix_cut+f"::{interface_index}"
    elif interface_index=="0": #subnet address
        network_prefix_cut = network_prefix[:network_prefix.index('::')]
        ipv6_address=network_prefix_cut+f":{subnet_index}::"
    else: #subnet interfaces
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
            config += f" ipv6 address {ipv6_address}/64\n"
        elif subnetwork_number[:2]=="LB":
            ipv6_address = generate_ipv6_address(as_data['IP_range']['loopback_interfaces'], subnetwork_number[2], subnetwork_number[4])
            config += f" ipv6 address {ipv6_address}/128\n"
        elif subnetwork_number[:4]=="eBGP":
            ipv6_address = as_data['IP_range']['eBGP_interfaces'][subnetwork_number]
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
    config += f" bgp router-id {router_name[1:]}.{router_name[1:]}.{router_name[1:]}.{router_name[1:]}\n"
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
                            if key.startswith(all_subnetwork_number):
                                ipv6_address = all_as_data['IP_range']['eBGP_interfaces'][all_subnetwork_number]
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
                            if key.startswith(all_subnetwork_number):
                                ipv6_address = all_as_data['IP_range']['eBGP_interfaces'][all_subnetwork_number]
                                config += f"  neighbor {ipv6_address} activate\n"
    
    config += " exit address-family\n!\n"
    config += "ip forward-protocol nd\n!\n"
    config += "no ip http server\nno ip http secure-server\n!\n"

    # Générer les configurations spécifiques en fonction de l'IGP
    if as_data["IGP"] == "RIP":
        config += "!\nipv6 router rip ripng\n"
        config += " redistribute connected\n"

    elif as_data["IGP"] == "OSPF":
        config += "!\nipv6 router ospf 1\n"
        config += f" router-id {router_name[1:]}.{router_name[1:]}.{router_name[1:]}.{router_name[1:]}\n"
        config += " passive-interface Loopback0\n"
    
    config += "!\n!\ncontrol-plane\n!\n"
    config += "line con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\n"
    config += "line aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\n"
    config += "line vty 0 4\n login\n!\n!\nend"

    return config


def copy_configs_to_gns3(intent_file):
    for as_name, as_data in intent_file.items():
        for router_name, router_data in as_data["routers"].items():
            router_config = generate_config(intent_file, as_name, as_data, router_name, router_data)

            # Récupérer le nom du routeur sans le préfixe "R"
            router_number = router_name[1:]

            # Utiliser glob pour trouver tous les fichiers de configuration du routeur dans GNS3
            pattern = f"/home/vincent/Documents/INSA TC/Cours/Réseau/Projet GNS3/GNS3_test_intent/project-files/dynamips/**/configs/i{router_number}_startup-config.cfg"
            config_files = glob.glob(pattern, recursive=True)

            # Copier la configuration dans chaque fichier trouvé
            for config_path in config_files:
                with open(config_path, "w") as config_file:
                    config_file.write(router_config)
                    print(f"Le fichier {config_path} a été remplacé.")

def main():
    with open("intent.json", "r") as file:
        intent_file = json.load(file)

    copy_configs_to_gns3(intent_file)

if __name__ == "__main__":
    main()
