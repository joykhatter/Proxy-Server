from socket import *
import sys
import string

#port = 8888
#max_connections = 1

if len(sys.argv) <= 1:
	print ('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
	sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(("192.168.56.1",8888))
tcpSerSock.listen(10)

while 1:

	# Start receiving data from the client
	print ('Ready to serve...')

	#print (addr)
	tcpCliSock, addr = tcpSerSock.accept()
	print ('Received a connection from:', addr)
	
	message = tcpCliSock.recv(1024)
	print ("Message", message)
	
	# Extract the filename from the given message
	print ("Message 1", message.decode().split()[1])
	filename = message.decode().split()[1].partition("/")[2]
	print ("File Name is" ,filename)
	
	fileExist = "false"
	filetouse = "/" + filename.replace("/","")
	
	print ("File to Use is ", filetouse)
	
	try:
		# Check whether the file exist in the cache
		f = open(filetouse[1:], "r")
		outputdata = f.readlines()
		fileExist = "true"
		
		# ProxyServer finds a cache hit and generates a response message
		resp = ""
		for s in outputdata:
			resp += s
		
		tcpCliSock.send(resp)
		
		print ('Read from cache')
	
	# Error handling for file not found in cache
	except IOError:
		if fileExist == "false":
			# Create a socket on the proxyserver
			print("hi")
			c = socket(AF_INET, SOCK_STREAM)
			hostn = filename.split('/')[0].replace("www.","",1)
			print ("Host n", hostn)
			try:
				# Connect to the socket to port 80
				print("inside try")
				c.connect((hostn, 80))
		
				# Create a temporary file on this socket and ask port 80 for the file requested by the client
				print("connected")
				fileobj = c.makefile('rb', 0)
				#fileobj = io.BytesIO(fileobj)
				#fileobj = open(fileobj,'w')
				fileobj.write("GET"+"http://" + filename + "HTTP/1.0\n\n")
				
				# Show what request was made
				print ("GET "+"http://" + filename + " HTTP/1.0")

				# Read the response into buffer
				resp = c.recv(4096)
				response = ""
				while resp:
					response += resp
					resp = c.recv(4096)
				
				# Create a new file in the cache for the requested file.
				# Also send the response in the buffer to client socket and the corresponding file in the cache
				if(filename[-1:] == '/'):
					filename = filename[:-1]
					
				tmpFile = open("./" + filename.replace("/","") ,"wb")
				tmpFile.write(response)
				tmpFile.close()
				
				tcpCliSock.send(response)
			except Exception as e:
				print (str(e))
				print ("Illegal request")
		else:
			# HTTP response message for file not found
			pass
	
	# Close the client and the server sockets
	tcpCliSock.close()