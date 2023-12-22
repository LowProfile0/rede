import socket
import paramiko
import cryptography

class Node:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connections = []

    def send(self, data):
        for connection in self.connections:
            connection.sendall(data)

    def receive(self):
        data = b""
        while True:
            chunk = self.socket.recv(1024)
            if chunk == b"":
                break
            data += chunk
        return data.decode()

def main():
    # Cria o servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8080))
    server.listen(0)

    # Lista de nós
    nodes = []

    while True:
        # Aceita uma conexão
        conn, addr = server.accept()

        # Cria um novo nó
        node = Node(addr[0], addr[1])
        nodes.append(node)

        # Adiciona a conexão ao nó
        node.connections.append(conn)

        # Envia um sinal de conexão
        node.send("Conectado!")

        # Distribui um IP aleatório
        node.ip = str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255)) + "." + str(random.randint(1, 255))

        # Criptografa a conexão
        node.socket = paramiko.Transport(node.socket)
        node.socket.start_tls(paramiko.RSAKey.from_private_key_file("my-secret-key"))

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
