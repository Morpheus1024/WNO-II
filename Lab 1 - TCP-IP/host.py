import socket
import threading
import sys


mutex = threading.Lock()

def send_message(client_socket, login):
    while True:
        message = input()

        # Acquire the lock before sending a message
        with mutex:
            client_socket.send(message.encode())

        if message.upper() == "EXIT":
            #time.sleep(2.5)
            print("rozłączanie z serwerem")
            
            # Acquire the lock before closing the socket
            with mutex:
                client_socket.close()
            
            sys.exit(0)
            break

def receive_messages(client_socket):
    while True:
        data = client_socket.recv(9999)
        print(data.decode())

        # if data.decode().upper() == "EXIT":
            
        #     client_socket.close()
        #     sys.exit(0)
        #     break

def start_host():
    host = '127.0.0.100'
    port = 12121

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    login = input("Podaj login: ")
    client_socket.send(login.encode())
    print("Witaj na serwerze!")

    receive_messages_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_messages_thread.start()
    send_message_thread = threading.Thread(target=send_message, args=(client_socket, login,))
    send_message_thread.start()

if __name__ == "__main__":
    start_host()
