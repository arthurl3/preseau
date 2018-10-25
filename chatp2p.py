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
	
	msg = str( id_student + code_hello ) + "\001" + "Hello#" + nickname
	buf = msg.encode('utf-8')
	s.send( buf )

def send_start(s, nickname):
	
	msg = str( id_student + code_start ) + "\001" + "Start#" + nickname
	buf = msg.encode('utf-8')
	s.send( buf )
	


def lauch_chat(s, nickname):

	s.listen(5)
	n_socket, addr = s.accept()
	data = n_socket.recv(1024)
	msg = data.decode('utf-8')
	print msg
	
	sock_answer = socket.socket()
	sock_answer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	print "addr = %s" %str(addr)
	sock_answer.connect( addr )
	
	send_hello( sock_answer, nickname )
	
	n_socket.close
	sock_answer.close
	
	
def first_connection(s_ecoute, s_list, ip, nickname):
	
	#premier socket pour envoi du start
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(("0.0.0.0", port))
	#envoie start.
	s.connect( (ip, port) )
	send_start( s, nickname )
	
	#recevoir hello nick
	s_ecoute.listen(1)

	n_socket, addr = s_ecoute.accept()
	data = n_socket.recv(1024)
	msg = data.decode('utf-8')
	print msg
	
	#recuperation du nickname
	nickname_expediteur = msg[(msg.index("#")+1):]
	print "nickname exp = %s" %nickname_expediteur
	
	s_list[nickname_expediteur] = s
	
	s.close()
	






######### Main #############
import socket

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
		print("Valid IP")
	except socket.error:
		print("Invalid IP")
		exit(1)
		
	first_connection( s_ecoute, s_list, argv[1], nickname )
	
	
else:
	lauch_chat( s_ecoute, nickname )


























