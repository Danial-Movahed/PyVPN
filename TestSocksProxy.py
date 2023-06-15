import socks

s = socks.socksocket()

s.set_proxy(socks.SOCKS5, "localhost", 10808)

s.connect(("ipv4.icanhazip.com", 80))
s.sendall(b"""GET / HTTP/1.1
Host: ipv4.icanhazip.com
User-Agent: curl/8.1.2
Accept: */*""")
print(s.recv(4096))