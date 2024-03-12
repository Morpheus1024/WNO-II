import socket
import threading
import time

# Create a threading lock
clients_lock = threading.Lock()

def client(client_socket, client_address, clients):
    login = client_socket.recv(1024).decode()

    print(f"Nowy użytkownik: {login}")

    # Acquire the lock before accessing the shared resource (clients list)
    with clients_lock:
        for other_client, _ in clients:
            if other_client != client_socket:
                exit_message = f"{login} dołączył do rozmowy."
                other_client.send(exit_message.encode())

    while True:
        data = client_socket.recv(9999)

        if not data:
            break

        if data.decode().upper() == "EXIT":
            break

        current_time = time.strftime("%H:%M:%S", time.localtime())
        message = f"({current_time}) {login}: {data.decode()}"
        print(f"Przekazuję wiadomość: {message}")

        with clients_lock:
            for other_client, _ in clients:
                if other_client != client_socket:
                    other_client.send(message.encode())

    print(f"{login}  rozłączył się.")

    with clients_lock:
        for other_client, _ in clients:
            if other_client != client_socket:
                exit_message = f"{login} rozłączył się."
                other_client.send(exit_message.encode())

    with clients_lock:
        clients.remove((client_socket, client_address))

    client_socket.close()

def start_server():
    host = '127.0.0.100'
    port = 12121

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(10)

    print(f"Serwer {host}:{port}")

    clients = []

    while True:
        client_socket, client_address = server.accept()

        client_thread = threading.Thread(target=client, args=(client_socket, client_address, clients))
        client_thread.start()

        # Acquire the lock before modifying the shared resource (clients list)
        with clients_lock:
            clients.append((client_socket, client_address))

if __name__ == "__main__":
    start_server()
