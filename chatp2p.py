#!/usr/bin/python
##
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
def send_hello(s, nickname):
	
	msg = str( id_student + code_hello ) + "\001" + "Hello#" + nickname + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )

def send_start(s, nickname):
	
	msg = str( id_student + code_start ) + "\001" + "Start#" + nickname + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )


def send_ips(s, ips_list):

	str_ips = "("
	
	if( len(ips_list) > 1 ):
		for ip in ips_list[:-1]:
			str_ips = str_ips+ip+','
	
		str_ips = str_ips + ips_list[-1]
		
	str_ips = str_ips + ")"
	
	msg = str( id_student + code_ips ) + "\001" + "IPS#"+ str_ips + "\r\n"
	buf = msg.encode('utf-8')
	s.send( buf )	
	
	
	

def lauch_chat(s_ecoute, s_list, nickname):

	ips_list = []
	
	#test
	ips_list.append("10.0.0.0")
	ips_list.append("10.0.0.1")
	
	s_ecoute.listen(5)
	
	chat_lance = True
	sock_connected = []
	
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
				
					#Affichage du message
					print msg[ msg.index('\001')+1:]

					#Recuperation du code du message
					msg_code = msg[:msg.index("\001")]
					print "code = %s" %str(msg_code)
					######Traiter le message en fonction du code ########
				
					if msg_code == str( id_student + code_start ):
						send_hello( sock_client, nickname )
						send_ips( sock_client, ips_list )				
					#####################################################
		
	##############################################
	
	sock_answer.close
	
	
def first_connection(s_ecoute, s_list, ip, nickname):
	
	
	ips_list = []
	#premier socket pour envoi du start
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(("0.0.0.0", port))
	#envoie start.
	s.connect( (ip, port) )
	send_start( s, nickname )
	
	#s_ecoute.listen(5)
	#n_socket, addr = s_ecoute.accept()
	
	recv_hello = False
	recv_ip = False
	
	#tant que la liste d'adresse IP n'est pas donnee
	while not recv_ip:
	
		msg_recv = s.recv(1024).decode('utf-8')
		
		if msg_recv: 
		
			#separation des messages recus si il y en a plusieurs a la fois
			msg_list = msg_recv.split('\n')
			
			for msg in msg_list[:-1]:
				#traitement de hello
				if not recv_hello and msg[:msg.index('\001')] == str( code_hello + id_student ):
					recv_hello = True
					print "HELLO#"+ msg[msg.index("#")+1] 
					nickname_expediteur = msg[msg.index("#")+1 : msg.index('\r')]
					s_list[nickname_expediteur] = s		
	
				#traitement de IPS
				if msg[:msg.index('\001')] == str( code_ips + id_student ):
					recv_ip = True
					#recevoir la liste des ip
					ips_list = msg[msg.index("#")+1: msg.index('\r')]
					print "IPS#%s" %ips_list
	
	



######### Main #############
import socket
import select
s_list = {}

s_ecoute = socket.socket()
s_ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# On cree une socket en ecoute sur le proxy
s_ecoute.bind(('0.0.0.0', port))


# Erreur arg 
if (len(argv) > 2 ):
	print 'Usage : %s or %s IP' %(argv[0])
	exit(1)

nickname = raw_input( "Entrer le nom d'utilisateur : \r\n" )
	
	
#First connection
if (len(argv) == 2):
#Verification IP
	try:
		socket.inet_aton(argv[1])
	except socket.error:
		print("Invalid IP")
		exit(1)
		
	first_connection( s_ecoute, s_list, argv[1], nickname )
	
	
else:
	lauch_chat( s_ecoute, s_list, nickname )


























