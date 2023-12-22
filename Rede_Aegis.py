import socket
import paramiko
import random

from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher

class Node:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connections = []
        self.proxy_list = []  # Initialize empty proxy list
        self.use_proxy = True  # Enable proxy usage by default

        self.hops = []

    def load_proxy_list(self, filename):
        with open(filename, "r") as f:
            self.proxy_list = f.readlines()
            self.proxy_list = [line.strip() for line in self.proxy_list]

    def send(self, data):
        for conn in self.connections:
            conn.send(data)

    def receive(self, data):
        for conn in self.connections:
            data = conn.receive()
            if data:
                return data
        return None

    def select_random_proxy(self):
        return random.choice(self.proxy_list)

    def connect(self):
        if self.proxy_list:
            proxy = self.select_random_proxy()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((proxy, 80))  # Assuming proxies listen on port 80
            self.socket = paramiko.Transport(sock)
            self.socket.start_tls(rsa.generate_private_key(backend=default_backend()))
        else:
            self.use_proxy = False  # Disable proxy usage if list is empty
            print("Lista de proxies vazia!")  # Print error message

        # Adicione uma lista de hops para o nó
        self.hops = []
        for i in range(1, 10):
            self.hops.append(random.randint(1, 255))

        # Selecione um hop aleatório
        hop = self.select_random_hop()

        # Conecte-se ao hop
        self.connect_to_hop(hop)

    def select_random_hop(self):
        return random.choice(self.hops)

    def connect_to_hop(self, hop):
        print("Conectando-se ao hop " + str(hop))
        self.socket.connect((str(hop), 80))

        # Use um protocolo de criptografia de ponta a ponta
        cipher = Cipher(algorithms.AES(self.socket.get_cipher().get_shared_key()), modes.GCM(self.socket.get_cipher().get_iv()))
        self.socket.cipher = cipher
        self.socket.sendall(cipher.encrypt(b"Hello, world!"))

        # Use um algoritmo de hash seguro
        hash_algorithm = SHA256()

        # Use um esquema de assinatura digital
        key = rsa.generate_private_key(backend=default_backend())
        signature = key.sign(hash_algorithm.digest(b"Hello, world!"))

        # Envie o hash e a assinatura
        self.socket.sendall(hash_algorithm.digest(b"Hello, world!"))
        self.socket.sendall(signature)

        # Receba o hash e a assinatura do hop
        hash_received = self.socket.recv(hash_algorithm.digest_size)
        signature_received = self.socket.recv(key.size_in_bytes())

        # Verifique a assinatura
        if not key.verify(hash_received, signature_received):
            raise Exception("Assinatura inválida")

        # A comunicação é segura
        print("Comunicação segura")
      
