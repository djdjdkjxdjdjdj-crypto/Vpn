import socket
import select
import sys

def handle_client(client_sock):
    try:
        # Приветствие SOCKS5
        data = client_sock.recv(262)
        if not data or data[0] != 0x05:
            client_sock.close()
            return
        client_sock.send(b'\x05\x00')
        
        # Команда CONNECT
        data = client_sock.recv(262)
        if not data or data[1] != 0x01:
            client_sock.close()
            return
        
        addr_type = data[3]
        if addr_type == 0x01:  # IPv4
            addr = socket.inet_ntoa(data[4:8])
            port = int.from_bytes(data[8:10], 'big')
        elif addr_type == 0x03:  # Домен
            addr_len = data[4]
            addr = data[5:5+addr_len].decode()
            port = int.from_bytes(data[5+addr_len:7+addr_len], 'big')
        else:
            client_sock.close()
            return
        
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.settimeout(10)
        target.connect((addr, port))
        
        client_sock.send(b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + b'\x00\x00')
        
        # Перегон трафика
        sockets = [client_sock, target]
        while True:
            r, _, _ = select.select(sockets, [], [])
            for sock in r:
                data = sock.recv(4096)
                if not data:
                    return
                if sock is client_sock:
                    target.send(data)
                else:
                    client_sock.send(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_sock.close()

def main():
    port = int(8080)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(100)
    print(f"SOCKS5 running on 0.0.0.0:{port}")
    
    while True:
        client, _ = server.accept()
        print("New connection")
        handle_client(client)

if __name__ == '__main__':
    main()
