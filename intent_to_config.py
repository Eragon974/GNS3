import json

def generate_config(as_info):
    configs = []

    for as_name, as_data in as_info.items():
        for router_name, router_data in as_data["routeurs"].items():
            config = "version 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!\n"
            config += f"hostname {router}\n!\n"
            config += "boot-start-marker\nboot-end-marker\n!\n"
            config += "no aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n!\n"
            config += "no ip domain lookup\nipv6 unicast-routing\nipv6 cef\n!\n"
            config +="multilink bundle-name authenticated\n!\n"
            config += "ip tcp synwait-time 5\n!\n"
            
            # Générer les configurations d'interfaces
            for subnetwork_number, interface_name in router_data.items():
                config += f"interface {interface_name}\n"
                config += f" ipv6 address {as_data['IP_range']['physical_interfaces']} link-local\n"
                config += f" ipv6 address {as_data['IP_range']['physical_interfaces']}\n"
                    # Ajouter d'autres configurations d'interface si nécessaire
                    

            # Générer les configurations spécifiques en fonction de l'IGP
            if as_data["IGP"] == "RIP":
                config += "router rip\n"
                config += " version 2\n"
                config += " no auto-summary\n"  # Supprimer la synthèse automatique
                # Ajouter d'autres paramètres RIP si nécessaire

            elif as_data["IGP"] == "OSPF":
                config += "router ospf 1\n"
                config += " router-id 1.1.1.1\n"  # Remplacer par un ID unique par routeur
                # Ajouter d'autres paramètres OSPF si nécessaire

            # Générer la configuration BGP commune pour tous les routeurs
            if "eBGP" in as_info:
                for link in as_info["eBGP"]["links"]:
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

            configs.append(config)

    return configs

def main():
    with open("votre_fichier.json", "r") as file:
        as_info = json.load(file)

    router_configs = generate_config(as_info)

    # Écrire les configurations dans des fichiers séparés
    for i, config in enumerate(router_configs):
        with open(f"config_{as_info['AS1']['routeurs'][i]}.txt", "w") as file:
            file.write(config)

if __name__ == "__main__":
    main()
