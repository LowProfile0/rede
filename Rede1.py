import socket
import paramiko
import random

class Node:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connections = []
        self.proxy_list = []  # Initialize empty proxy list
        self.use_proxy = True  # Enable proxy usage by default

    def load_proxy_list(self, filename):
        with open(filename, "r") as f:
            self.proxy_list = f.readlines()
            self.proxy_list = [line.strip() for line in self.proxy_list]

    def send(self, data):
        for conn in self.connections:
            conn.send(data)

    def receive(self):
        for conn in self.connections:
            data = conn.receive()
            if data:
                return data
        return None

    def select_random_proxy(self):
        return random.choice(self.proxy_list)

    def connect(self):
        if self.use_proxy:
            proxy = self.select_random_proxy()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((proxy, 80))  # Assuming proxies listen on port 80
            self.socket = paramiko.Transport(sock)
            self.socket.start_tls(paramiko.RSAKey.from_private_key_file("my-secret-key"))
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))

def main():
    # Cria o servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8080))
    server.listen(0)

    # Lista de nós
    nodes = []

    # Load proxy list from file
    with open("proxy_list.txt", "r") as f:
        proxy_list = f.readlines()
        proxy_list = [line.strip() for line in proxy_list]

    while True:
        # Aceita uma conexão
        conn, addr = server.accept()

        # Cria um novo nó
        node = Node(addr[0], addr[1])
        node.load_proxy_list("proxy_list.txt")  # Load proxies for each node
        nodes.append(node)

        # Adiciona a conexão ao nó
        node.connections.append(conn)

        # Envia um sinal de conexão
        node.send("Conectado!")

        # Distribui um IP aleatório
        node.ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))

        # Criptografa a conexão
        node.connect()  # Call connect to establish connection (with or without proxy)

        # Busca um destino aleatório
        if len(nodes) > 1:
            destination = nodes[random.randint(0, len(nodes) - 1)]
        else:
            destination = nodes[0]

        # Envia uma mensagem de conexão
        node.send("Conectado a " + destination.ip)

        # Recebe a resposta
        data = destination.receive()

        # Imprime a resposta
        print(data)

if __name__ == "__main__":
    main()


