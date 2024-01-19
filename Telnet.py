import telnetlib
from telnetlib import Telnet

HOST=["R1","R2","R3","R4","R5","R6"]
IpHost=[""] #adresse ip des routeurs pour communiquer avec eux (https://www.sysnettechsolutions.com/en/configure-telnet-gns3/ partie 8 et 9)
area = 0
for i in range (len(HOST)):
    H=IpHost[i]
    tn=telnetlib.Telnet(H)
    #chercher dans le json la plage et choisir une addresse ip via AddIp.append(Nouvelle addresse ip) et 
    #comparer avec les valeurs dans AddIp pour voir si elle a pas déjà été prise
    tn.write(b"enable\n")
    tn.write(b"conf t\n")
    tn.write(b"ipv6 unicast-routing\n")
    #for allInterface
    tn.write(b"interface"+ +"\n") #Mettre l'interface à paramétrer
    tn.write(b"ipv6 enable\n")
    tn.write(b"ipv6 address"+ +"\n")
    tn.write(b"no shutdown\n")
    tn.write(b"end\n")
    
    
    #if RIP (pas dans le for allInsterface)
    tn.write(b"conf t\n")
    tn.write(b"ipv6 rip connected\n")
    tn.write(b"redistribute connected\n")
    tn.write(b"end\n")
    tn.write(b"conf t\n")
    #for allInterface2 (dans le if)
    tn.write(b"ipv6 rip connected enable\n")
    tn.write(b"end\n")

    #if OSPF
    tn.write(b"conf t\n")
    processid = HOST[i][1:]
    tn.write(b"ipv6 router ospf"+ processid +"\n")
    routerid = processid+"."+processid+"."+processid+"."+processid
    tn.write(b"router-id"+routerid+"\n")
    tn.write(b"end\n")
    tn.write(b"conf t\n")
    #for allInterface3
    tn.write(b"interface"+ +"\n")
    tn.write(b"ipv6 ospf"+processid+"area"+area+"\n")
    
    area +=1 #hors de la bouble for allInterface3
    
