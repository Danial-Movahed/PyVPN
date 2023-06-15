import socket
import threading
import os
import time
from cryptography.fernet import Fernet
from encodeN import Encryption
import ssl
from python_socks.sync import Proxy


if os.name == 'posix':
    print('os is linux')
    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))


listen_PORT = 57479

my_socket_timeout = 60


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.encyptionPkg = Encryption()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.proxy = Proxy.from_url('socks5://127.0.0.1:10808')
        self.socksSock = self.proxy.connect(dest_host='check-host.net', dest_port=443)
        self.socksSock = ssl.create_default_context().wrap_socket(
            sock=self.socksSock,
            server_hostname='check-host.net'
        )

    def listen(self):
        self.sock.listen(128)
        while True:
            client_sock, client_addr = self.sock.accept()
            client_sock.settimeout(my_socket_timeout)

            print('someone connected')
            thread_up = threading.Thread(
                target=self.my_upstream, args=(client_sock, self.socksSock))
            thread_up.daemon = True
            thread_up.start()

    def my_upstream(self, client_sock, proxySocks):
        thread_down = threading.Thread(
            target=self.my_downstream, args=(client_sock, proxySocks))
        thread_down.daemon = True
        thread_down.start()
        while True:
            try:
                data = client_sock.recv(65536)
                if data:

                    toSend = self.encyptionPkg.decode(data.decode())
                    print(toSend)

                    proxySocks.sendall(toSend)
                else:
                    raise Exception('cli pipe close')

            except Exception as e:
                # print('upstream : '+ repr(e) )
                time.sleep(2)  # wait two second for another thread to flush
                client_sock.close()
                proxySocks.close()
                return False

    def my_downstream(self, client_sock, proxySocks):
        while True:
            try:
                data = proxySocks.recv(65536)
                if data:

                    received = self.encyptionPkg.encode(data.decode())

                    client_sock.sendall(received)
                else:
                    raise Exception('backend pipe close')

            except Exception as e:
                # print('downstream '+backend_name +' : '+ repr(e))
                time.sleep(2)  # wait two second for another thread to flush
                proxySocks.close()
                client_sock.close()
                return False


print("Now listening at: 127.0.0.1:"+str(listen_PORT))
ThreadedServer('', listen_PORT).listen()
