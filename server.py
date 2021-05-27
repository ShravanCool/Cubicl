import socket
import threading
import pickle

HOST  = '127.0.0.1'
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]}")
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break
    
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}!")

        S = "NICK"
        msg1 = pickle.dumps(S)
        client.send(msg1)
        nickname = pickle.loads(client.recv(1024))

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of client is {nickname}")
        message = f"{nickname} connected to the server!\n"
        msg2 = pickle.dumps(message)
        broadcast(msg2)
        
        # client.send("Connected to the server".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server running...")
receive()
