import socket

UDP_IP = "192.168.56.1"
UDP_PORT = 6753
PORT = 5000
MESSAGE = "prepare/RNID"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

d = sock.recvfrom(1024)
data = d[0]
addr = d[1]
print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
sock.close()
