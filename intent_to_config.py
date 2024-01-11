import json

def generate_config(as_info):
    configs = []

    for as_name, as_data in as_info.items():
        # Générer la configuration pour chaque routeur dans l'AS
        for router in as_data["routeurs"]:
            config = f"hostname {router}\n"

            # Générer les configurations spécifiques en fonction de l'IGP
            if as_data["IGP"] == "RIP":
                config += "router rip\n"
                config += " version 2\n"
                # Ajouter d'autres paramètres RIP si nécessaire

            elif as_data["IGP"] == "OSPF":
                config += "router ospf 1\n"
                # Ajouter d'autres paramètres OSPF si nécessaire

            # Générer les configurations d'interfaces
            for link in as_data["links"]:
                for interface in link:
                    config += f"interface {interface}\n"
                    config += f" ipv6 address {as_data['IP_range']['physical_interfaces']} link-local\n"
                    # Ajouter d'autres configurations d'interface si nécessaire

            configs.append(config)

    # Générer la configuration eBGP
    ebgp_config = ""
    if "eBGP" in as_info:
        for link in as_info["eBGP"]["links"]:
            ebgp_config += f"router bgp <AS-X>\n"
            ebgp_config += f" neighbor {link[0]} remote-as <AS-Y>\n"
            # Ajouter d'autres configurations eBGP si nécessaire

    return configs, ebgp_config

def main():
    with open("votre_fichier.json", "r") as file:
        as_info = json.load(file)

    router_configs, ebgp_config = generate_config(as_info)

    # Écrire les configurations dans des fichiers séparés
    for i, config in enumerate(router_configs):
        with open(f"config_router{i+1}.txt", "w") as file:
            file.write(config)

    with open("config_ebgp.txt", "w") as file:
        file.write(ebgp_config)

if __name__ == "__main__":
    main()
