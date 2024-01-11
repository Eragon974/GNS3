import telnetlib
from telnetlib import Telnet

HOST=["","","","","",""]
AddIp=[]
for i in range (len(HOST)):
    H=HOST[i]
    tn=telnetlib.Telnet(H)
    #chercher dans le json la plage et choisir une addresse ip via AddIp.append(Nouvelle addresse ip) et 
    #comparer avec les valeurs dans AddIp pour voir si elle a pas déjà été prise
    tn.write(b"conf t\n")
    #tn.write
    #if valIGP json == RIP ....