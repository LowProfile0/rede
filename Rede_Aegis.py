import socket
import paramiko
import random
import struct
import logging
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from aegis.core import Node, Message

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class Node(Node):

    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.logger = logger
        self.cipher = Cipher(algorithms.AES(self.get_shared_key()), modes.GCM(self.get_iv()))

    def disconnect(self):
        if hasattr(self, 'socket') and self.socket:
            self.socket.close()
            self.logger.info("Desconectado com sucesso")

    def connect(self):
        if self.proxy_list:
            proxy = self.select_random_proxy()
            self.logger.info("Conectando-se ao proxy: %s", proxy)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((proxy, 80))
            except socket.error as e:
                self.logger.error("Erro ao conectar ao proxy: %s", e)
                return

            self.socket.start_tls(rsa.generate_private_key(backend=default_backend()))
        else:
            self.logger.warning("Lista de proxies vazia!")
            self.use_proxy = False

        # Conecta-se aos hops restantes
        if self.hops:
            for hop in self.hops:
                self.logger.info("Conectando-se ao hop: %s", hop)
                try:
                    self.socket.connect((str(hop), 80))
                except socket.error as e:
                    self.logger.error("Erro ao conectar ao hop: %s", e)
                    return
        else:
            self.logger.warning("Nenhum hop disponível!")

    def handle_handshake_message(self, message):
        self.send(message.create_handshake())

    def handle_data_message(self, message):
        self.logger.info("Mensagem recebida do hop anterior: %s", message.data)


class Message(Message):

    TYPE_HANDSHAKE = 1
    TYPE_DATA = 2

    logger = logging.getLogger(__name__)

    def __init__(self, type=None, sender_id=None, data=None):
        super().__init__(type, sender_id, data)

        if type not in (self.TYPE_HANDSHAKE, self.TYPE_DATA):
            self.logger.error("Tipo de mensagem inválido")

    def to_bytes(self):
        data = struct.pack("!I", self.type)
        data += struct.pack("!I", self.sender_id)
        if self.data:
            data += self.data.encode()
        return data

    @classmethod
    def from_bytes(cls, data):
        message = cls()
        message.type = struct.unpack("!I", data[:4])[0]
        message.sender_id = struct.unpack("!I", data[4:8])[0]
        if len(data) > 8:
            message.data = data[8:].decode()
        return message


def main():
    node = Node("127.0.0.1", 80)
    node.connect()

    message = Message(type=Message.TYPE_HANDSHAKE, sender_id=1)
    node.send(message)

    message = node.receive()

    print(message.data)

    node.disconnect()


if __name__ == "__main__":
    main()
