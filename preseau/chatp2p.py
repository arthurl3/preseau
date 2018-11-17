#!/usr/bin/python
# -*- encoding: utf-8 -*-
# TCP chat server
# port 1664
##

from sys import *
from socket import *
from select import *

## Globales
port       = 1664
id_student = 201

code_start = 1000
code_hello = 2000
code_ips   = 3000
code_pm    = 4000
code_bm    = 5000

##
def get_ips_list( sock_list ):
	
	ips_list = []
	for user_name, sock_user in sock_list.items():
		ip_sock, port_sock = sock_user.getpeername()
		ips_list.append(ip_sock)
		print "ip_sock : %s" %ip_sock
	return ips_list

def send_hello(s, nickname):
	
	msg = str( id_student + code_hello ) + "\001" + "HELLO" + '\043' + nickname + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )

def send_start(s, nickname):
	
	msg = str( id_student + code_start ) + "\001" + "START" + '\043' + nickname + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )


def send_ips(s, ips_list):
	
	str_ips = "("
	
	if( len(ips_list) >= 1 ):
		for ip in ips_list[:-1]:
			str_ips = str_ips+ip+','
		str_ips = str_ips + ips_list[-1]
		
	str_ips = str_ips + ")"
	print "ips = %s" %str_ips
	msg = str( id_student + code_ips ) + "\001" + "IPS" + '\043' + str_ips + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )	
	
def send_pm( data, s_list, nickname ):

	#recuperation du nickname 
	data_split = data.split(" ")
	dest_nickname = data_split[1]
	del data_split[0]
	del data_split[0]
	#Reconstruction du message sans le nickname et le pm
	new_data = " ".join(data_split)
	msg = str( id_student + code_pm ) + "\001" + "PM" + '\043' + new_data + "\r\n"
	s_list[dest_nickname].send( msg )
	

#Envoi a tout le monde
def send_bm( data, s_list , nickname, ban_list):
	new_data = data[data.index(" ")+1:]
	msg = str( id_student + code_bm ) + "\001" + "BM" + '\043' + new_data + "\r\n"
	for user_name, sock_client in s_list.items():
		if not user_name in ban_list:
			sock_client.send( msg )

def ban( ban_list, nickname ):

	if not is_in_ban_list( nickname, ban_list ): #S'il n'est pas déja dans la list
		print u"%s a été banni" %nickname
		ban_list.append(nickname)
	else:
		print u"L'utilisateur %s est déjà banni" %nickname	
	
	
def unban( ban_list, nickname ):

	if is_in_ban_list( nickname, ban_list ): #S'il n'est pas déja dans la list
		print u"%s a été débanni" %nickname
		ban_list.remove(nickname)
	else:
		print u"L'utilisateur %s n'est pas banni" %nickname

#Renvoie vrai si c'est un nickname valide et qui n'est pas banni, faux sinon 
def is_valid_nickname( nickname, s_list ):
	
	if nickname not in s_list:
		print u"Le nom d'utilisateur %s n'existe pas" %nickname
		return False
	else:	
		return True
    

def is_in_ban_list( nickname, ban_list ):

	if nickname in ban_list:
		return True
    
	return False

def verif_IP( ip ):

	occurence_point = ip.count(".")
	if occurence_point == 3: 
		ip_split = ip.split('.')
		print str(len(ip_split) )
		if len(ip_split) == 4:
			for number in ip_split:
				if number == '' or int(number) > 256 :
					return False
		else :
			return False
	else:
		return False
	return True

#def display_message(msg):

	



##### ChatP2P ########
def lauch_chat(s_ecoute, s_list, list_ip_username, nickname):
	
	#Liste des bannis, vide pour l'instant
	ban_list = []

	# On cree une socket en ecoute sur le proxy
	s_ecoute.bind(('0.0.0.0', port))
	s_ecoute.listen(5)
	
	chat_lance = True
	sock_connected = []
	
	#On remplit le sock_connected avec les sockets deja connecte
	for user_name, sock_user in s_list.items():
		sock_connected.append(sock_user)
	
	#### Tant que l'utilisateur ne quitte pas ####
	while chat_lance:
		
		###### Ajout de nouveaux clients #####
		sock_demandes, wlist, xlist = select.select([s_ecoute], [], [], 0.05)
		for sock_en_attente in sock_demandes:
			new_sock_client, addr = sock_en_attente.accept()
			# On ajoute le socket connecte a la liste des clients
			sock_connected.append(new_sock_client)
		
		######################################
	    
	    
		##### Ecoute sur les clients #########
		sock_to_read = []
		
		try:
			sock_to_read, wlist, xlist = select.select(sock_connected, [], [], 0.05)
		except select.error:
			pass
		else:
			
			# On parcourt la liste des clients a lire
			for sock_client in sock_to_read:
				
				msg = sock_client.recv(1024).decode('utf-8')	
				
				#Si il y a un nouveau message
				if( msg ):
				
					#Recuperation du code du message
					msg_code = msg[:msg.index("\001")]
					
					######Traiter le message en fonction du code ########
					
					##### Code BM ######
					if msg_code == str(id_student + code_bm) :
						ip_user, port_user = sock_client.getpeername()
						nickname_expediteur = list_ip_username[ip_user]
						
						if not is_in_ban_list( nickname_expediteur, ban_list ):
							print (u"%s (broadcast) de %s : %s" %( msg_code, nickname_expediteur, msg[ msg.index('\043')+1:] ) )
					####################
					
					##### Code PM ######
					elif msg_code == str(id_student + code_pm) :
						ip_user, port_user = sock_client.getpeername()
						nickname_expediteur = list_ip_username[ip_user]
						if not is_in_ban_list( nickname_expediteur, ban_list ):
							print (u"%s (privé) de %s : %s" %( msg_code, nickname_expediteur, msg[ msg.index('\043')+1:] ) )
					####################	
										
					#### Code Start ####
					elif msg_code == str( id_student + code_start ):
					
						send_hello( sock_client, nickname ) #dire bonjour
						
						ips_list = get_ips_list( s_list ) #recuperer la liste d'ip
						send_ips( sock_client, ips_list ) #la donner a la personne qui vient de se connecter
						
						# Ajout du socket dans la s_list avec son nickname comme indice et dans list_ip_username le username avec comme cle l'ip
						nickname_expediteur = msg[msg.index("\043")+1 : msg.index('\r')] 
						s_list[nickname_expediteur] = sock_client
						ip_user, port_user = sock_client.getpeername()
						list_ip_username[ip_user] = nickname_expediteur
					####################	
					
					#### Code Hello ####
					elif msg_code == str( id_student + code_hello ):
						send_hello( sock_client, nickname )
						
						# Ajout du socket dans la s_list avec son nickname comme indice et dans list_ip_username le username avec comme cle l'ip
						nickname_expediteur = msg[msg.index("\043")+1 : msg.index('\r')] 
						s_list[nickname_expediteur] = sock_client
						ip_user, port_user = sock_client.getpeername()
						list_ip_username[ip_user] = nickname_expediteur
					####################
					
		#####################################################
					
		################ Entrees claviers ###################		
		lin, lout, lex = select.select([stdin],[],[], 0.05)
		for text in lin:
			if text==stdin :
				data = stdin.readline().strip("\n")
				cmd = data[:data.index(" ")]
				
				#Quitter
				if cmd == "quit":
					chat_lance = False
				
				#Bannir
				elif cmd == "ban":
				
					data_split = data.split(' ')
					user_nick = data_split[1]
					if is_valid_nickname( user_nick, s_list):
						ban( ban_list, user_nick )
				
				#Débannir
				elif cmd == "unban":
				
					data_split = data.split(' ')
					user_nick = data_split[1]
					if is_valid_nickname( user_nick, s_list):
						unban( ban_list, user_nick )
					
				#PM
				elif cmd == "pm":
				
					data_split = data.split(' ')
					user_nick = data_split[1]
					if is_valid_nickname( user_nick, s_list):
						if not is_in_ban_list(user_nick, ban_list):
							send_pm( data, s_list, nickname )
						else: 
							print u"impossible d'envoyer des messages à %s car il est banni" %nickname
						
				#BM
				elif cmd == "bm":
					send_bm( data, s_list, nickname, ban_list )
				else:
					print "Erreur commande"
		#################################################
	
	for sock in sock_connected:
		sock.close()
	print "Fin du Chat"
	
	
############# Si le programme est lance avec un argument, first_connection est d'abord appele pour relier la machine au chat###
def first_connection(s, s_list,list_ip_username, ip, nickname):
	
	
	ips_list = []
	#premier socket pour envoi du start
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#envoie start
	s.connect( (ip, port) )
	send_start( s, nickname )
	
	recv_hello = False
	recv_ip = False
	
	str_ips_list = ""
	#tant que la liste d'adresse IP n'est pas donnee
	while not recv_ip:
	
		msg_recv = s.recv(1024).decode('utf-8')
		
		if msg_recv: 
		
			#separation des messages recus si il y en a plusieurs a la fois
			msg_list = msg_recv.split('\n')
			
			for msg in msg_list[:-1]:
				
				#Recuperation du code du message
				msg_code = msg[:msg.index("\001")]
				
				#traitement de hello
				if not recv_hello and msg_code == str( code_hello + id_student ):
					recv_hello = True
					nickname_expediteur = msg[msg.index("\043")+1 : msg.index('\r')]					
					print "%s Hello de %s" %(msg_code, nickname_expediteur)
					s_list[nickname_expediteur] = s
					
					# Ajout correspondance ip => username
					ip_user, port_user = s.getpeername()
					list_ip_username[ip_user] = nickname_expediteur
					
								
				#traitement de IPS
				if msg_code == str( code_ips + id_student ):
					recv_ip = True
					#recevoir la liste des ip
					str_ips_list = msg[msg.index("\043")+1: msg.index('\r')]
					print "%s Ips : %s" %(msg_code, str_ips_list)
					str_ips_list = str_ips_list[1:-1]
					
		
		ips_list = str_ips_list.split(',')
		
		if ips_list[0] <> "":	
			#Hello a toutes les ips et attendre hello en retour
			for ip_user in ips_list: 
				
				sock_user = socket.socket()
				sock_user.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				sock_user.bind(("0.0.0.0", port))
				#envoie hello
				sock_user.connect( (ip_user, port) )
				send_hello( sock_user, nickname )
		
				recv_hello = False
	
			#tant que le hello n'est recu
				while not recv_hello:
	
					msg_recv = sock_user.recv(1024).decode('utf-8')
		
					if msg_recv: 
		
						#separation des messages recus si il y en a plusieurs a la fois
						msg_list = msg_recv.split('\n')
			
						for msg in msg_list:
							#traitement de hello
							if not recv_hello and msg[:msg.index('\001')] == str( code_hello + id_student ):
								recv_hello = True
								print "HELLO#"+ msg[msg.index("#")+1:] 
								nickname_expediteur = msg[msg.index("#")+1 : msg.index('\r')]
								s_list[nickname_expediteur] = sock_user
		
			
		



######### Main #############
import socket
import select
s_list = {} #dictionnaire ; clé : le nickname, contenu : le socket correspondant
list_ip_username = {} #dictionnaire ; clé : l'ip, contenu : le nickname correspondant
s_ecoute = socket.socket()
s_ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Erreur argument 
if (len(argv) > 2 ):
	print 'Usage : %s or %s IP' %(argv[0])
	exit(1)

nickname = raw_input( "Entrer le nom d'utilisateur : \r\n" )
	
#Premiere connexion
if (len(argv) == 2):
#Verification IP
	if( not verif_IP( argv[1]) ):
		print "Invalid IP"
		exit(1)
		
	first_connection( s_ecoute, s_list, list_ip_username, argv[1], nickname )
	
lauch_chat( s_ecoute, s_list, list_ip_username, nickname )


























