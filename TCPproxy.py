import argparse
import sys
import socket
import threading

def serverLoop(localHost, localPort, remoteHost, remotePort, receive_first):
    server = socket.socket(AF_INET, SOCK_STREAM)
    
    try:
        server.bind(localHost, localPort)
        server.listen(5)
    except:
        print "Can t listen on %s:%d" %(localHost, localPort)
        sys.exit(0)
    
    print "listening on %s:%d" %(localHost, localPort)

    while True:
        client_socket, addr = server.accept()
        print "==> Received incoming connection from %s:%d" %(addr[0], addr[1])
        proxy_thread = threading.Thread(target = proxy_handler, args=(client_socket, remoteHost, remotePort,receive_first))
        proxy_thread.start()

def proxy_handler(client_socket, remoteHost, remotePort, receive_first):
    remote_socket = socket.socket(AF_INET, SOCK_STREAM)
    remote_socket.connect((remoteHost, remotePort))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print "[<==] Sending %d bytes to localhost." %(remote_buffer)
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print "[==>] Received %d bytes from localhost." %len(local_buffer)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print "sent to remote."
        
        remote_buffer = receive_from(remote_socket)
        
        if len(remote_buffer):
            print "<== Received %d bytes from remote." % len(remote_buffer)
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print "<== Sent to localhost."

        if not len(local_buffer) and not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print "No more data closing the connections."
            break



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("local_host", help = "enter localHost")
    parser.add_argument("local_port", type = int, help = "enter localPort")
    parser.add_argument("remote_host", help = "enter host")
    parser.add_argument("remote_port", type = int, help = "enter remotePort")
    args = parser.parse_args()

    serverLoop(args.local_host, args.local_port, args.remote_host, args.remote_port, receive_first)

