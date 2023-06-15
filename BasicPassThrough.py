import socket
import threading
import os
import time

if os.name == 'posix':
    print('os is linux')
    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))


listen_PORT = 2500
ServerPort = 4561
BufferSize = 4096
UDSAddress = './uds_socket'

my_socket_timeout = 60


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(128)
        while True:
            client_sock, client_addr = self.sock.accept()
            client_sock.settimeout(my_socket_timeout)

            print('someone connected')
            thread_up = threading.Thread(
                target=self.my_upstream, args=(client_sock,))
            thread_up.daemon = True
            thread_up.start()

    def my_upstream(self, client_sock):
        # backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # backend_sock.settimeout(my_socket_timeout)
        # backend_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # backend_sock.connect((ServerIp, ServerPort))

        backend_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        backend_sock.settimeout(my_socket_timeout)

        # Connect the socket to the port where the server is listening
        server_address = './uds_socket'
        print('connecting to {}'.format(server_address))
        try:
            backend_sock.connect(server_address)
        except socket.error as msg:
            print(msg)

        thread_down = threading.Thread(
            target=self.my_downstream, args=(backend_sock, client_sock))
        thread_down.daemon = True
        thread_down.start()
        while True:
            try:
                data = client_sock.recv(BufferSize)
                if data:
                    print(data)

                    backend_sock.sendall(data)
                else:
                    raise Exception('cli pipe close')

            except Exception as e:
                # print('upstream : '+ repr(e) )
                time.sleep(2)  # wait two second for another thread to flush
                client_sock.close()
                backend_sock.close()
                return False

    def my_downstream(self, backend_sock, client_sock):
        while True:
            try:
                data = backend_sock.recv(BufferSize)
                if data:

                    client_sock.sendall(data)
                else:
                    raise Exception('backend pipe close')

            except Exception as e:
                # print('downstream '+backend_name +' : '+ repr(e))
                time.sleep(2)  # wait two second for another thread to flush
                backend_sock.close()
                client_sock.close()
                return False


print("Now listening at: 127.0.0.1:"+str(listen_PORT))
ThreadedServer('', listen_PORT).listen()
