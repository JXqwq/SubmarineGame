import socket
from random import choices
import threading
import sys
import json

# Server side

class server:
    def __init__(self, port):
        self.port = port
        self.clients = []
        self.prev_status = None
        self.current_turn = 1
        self.lock = threading.Lock()
        self.start = []
    
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", self.port))
        server.listen()
        print("Waiting for connections...")

        while len(self.clients) <= 2:
            # Accept a new client
            clientsocket, addr = server.accept()
            print(f"Accepted connection from {addr}")

            # Add client to the list
            self.clients.append(addr)

            # Create a new thread for the client
            client_thread = threading.Thread(target=self._on_new_client, args=(clientsocket, addr))
            client_thread.start()
    
    def _on_new_client(self,clientsocket,addr):
        while len(self.clients) < 2:
            continue

        if addr == self.clients[1]:
            clientsocket.sendall("FIRST".encode())
        else:
            clientsocket.sendall("SECOND".encode())
        
        # Witing for ready
        ready = clientsocket.recv(1024).decode()
        print(f"Received from player ({addr}): {ready}")
        with self.lock:
            self.start.append(ready)

        while len(self.start) < 2:
            continue
            
        clientsocket.sendall("START".encode())

        while True:
            # Waiting for another player 
            while addr != self.clients[self.current_turn % 2]:
                continue
            if self.prev_status != None:
                clientsocket.sendall(json.dumps(self.prev_status).encode('utf-8'))
                if self.prev_status['dead'] == True:
                    print(f"Player {addr} win!")
                    break
            
            status_msg_bytes = clientsocket.recv(1024)
            print(f"Turn {self.current_turn}: Player {addr}")
            status_msg = json.loads(status_msg_bytes.decode())

            if status_msg['dead'] == True:
                with self.lock:
                    self.current_turn += 1
                    self.prev_status = status_msg
                print(f"Player {addr} died!")
                break

            print(f"Received from player {self.current_turn % 2} ({addr}): {status_msg}")
            
            # Write to the shared variables
            with self.lock:
                self.current_turn += 1
                self.prev_status = status_msg

        clientsocket.close()
        with self.lock:
            self.start.pop()
            if len(self.start) == 0:
                self.current_turn = 1
                self.clients = []
                self.prev_status = None
                print("All players have exited...Waiting for a new game.")
            


    #def _initialize_map(self):
        # Add random obstacles to 5*5 map
        # Rule1: Each tile has 0.2 possibility becoming an obstacle
        # Rule2: Each row has most 2 obstacles to avoid bug
    #    values = ["Ground", None]
    #    weights = [8, 2]
    #    for i in range(5):
    #        row = []
    #        obstacles = 0
    #        for j in range(5):
    #            result = choices(values, weights=weights, k=1) if obstacles < 2 else ["Ground"]
    #            if result == [None]:
    #                obstacles += 1
    #            row += result
    #        self.map.append(row)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        my_server = server(sys.argv[1])
    else:
        my_server = server(2000)
    my_server.start_server()






        

