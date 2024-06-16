import socket

host = 'red-cpb3sa7sc6pc73a1uij0'
port = 6379

try:
    ip = socket.gethostbyname(host)
    print(f"Resolved {host} to IP address: {ip}")
except socket.gaierror as e:
    print(f"Failed to resolve {host}: {e}")
