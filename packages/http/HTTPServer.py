import socket
from mt import threads
from HTTPHandler import HTTPHandler

class HTTPServer( threads.Thread ):
    def __init__(self, server_socket):
        threads.Thread.__init__(self)
        self.sock = server_socket

    def run ( self ):
        while self.running:
            try:
                client_socket, client_addr = self.sock.accept()
                client_socket.setblocking(1)
                client_thread = HTTPHandler(client_socket, client_addr)
                client_thread.start()
            except socket.timeout:
                pass

        self.sock.shutdown(1)
        self.sock.close()
