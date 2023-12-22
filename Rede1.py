import socket
import paramiko

class Node:
   def __init__(self, ip, port):
       self.ip = ip
       self.port = port
       self.connections = []
       self.proxy_list = ["127.0.0.1:8080", "127.0.0.1:8081", "127.0.0.1:8082"]  # Added proxy list
       self.use_proxy = False  # Added proxy usage flag

   def send(self, data):
       for conn in self.connections:
           conn.send(data)

   def receive(self):  # Added receive method
       for conn in self.connections:
           data = conn.receive()
           if data:
               return data
       return None

   def select_random_proxy(self):  # Added proxy selection method
       return random.choice(self.proxy_list)

   def connect(self):  # Modified connect method to handle proxy usage
       if self.use_proxy:
           proxy = self.select_random_proxy()
           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.connect((proxy, 80))
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

