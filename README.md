### Projet Python - Configuration de routeurs GNS3

**Description :** 
Ce projet Python permet d'automatiser la création de fichiers de configuration de routeurs cisco pour des topologies réseau avec plusieurs systèmes autonomes (AS).
Il est particulièrement utile pour générer automatiquement les configurations d'une simulation GNS3.
La modification du fichier d'intention JSON (intent file) permet de décrire la topologie du réseau à déployer.
Le script intent_to_config.py permet ensuite de générer les configurations des routeurs incluant des paramètres tels que le choix du protocole de routage intra-AS (RIP ou OSPF), les connexions eBGP inter-AS, les local_pref BGP et les communautés BGP.

**Instructions d'utilisation :**
1. Assurez-vous d'avoir Python installé sur votre système. Vous pouvez le télécharger depuis [le site officiel de Python](https://www.python.org/).
2. Clonez ce dépôt Git sur votre machine locale en utilisant la commande `git clone https://github.com/Eragon974/GNS3.git`.
3. Modifiez le fichier d'intention `intent.json` pour qu'il corresponde à votre topologie de réseau
4. Editez le fichier `intent_to_config_with_policies.py` pour modifier le chemin de projet gns3 dans `pattern`
5. Exécutez `intent_to_config_with_policies.py` pour générer les fichiers de configuration (assurez-vous d'avoir démarré votre projet GNS3 au moins une fois).
6. Les fichiers de configuration sont directement copiés dans les répertoires GNS3. Vous n'avez plus qu'à démarrer vos routeurs.

**Contributeurs :**
- Julien GEYER et Vincent FROMONT : Conception et développement du fichier d'intention JSON et du générateur de configurations.

