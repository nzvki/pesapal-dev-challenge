import socket

class Server:
    def __init__(self, max_clients):
        self.max_clients = max_clients
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 5555))
        self.server_socket.listen(max_clients)
        self.clients = {}  # Keeps track of connected clients
        self.ranks = {}  # Keeps track of clients' ranks

    def start(self):
        print(f'Server started. Waiting for {self.max_clients} clients to connect...')
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f'Client {client_address} connected.')
            rank = self.assign_rank()
            self.clients[rank] = client_socket
            self.ranks[client_socket] = rank
            self.send_to_all_clients(f'Client {client_address} connected with rank {rank}')
            self.handle_client(client_socket, rank)

    def handle_client(self, client_socket, rank):
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if data:
                    self.execute_command(client_socket, rank, data)
            except:
                self.disconnect_client(client_socket)

    def execute_command(self, client_socket, rank, command):
        for r, s in self.clients.items():
            if r < rank:
                s.send(f'Executing command "{command}" from client rank {rank}\n'.encode())

    def disconnect_client(self, client_socket):
        if client_socket in self.ranks:
            rank = self.ranks[client_socket]
            del self.clients[rank]
            del self.ranks[client_socket]
            client_socket.close()
            self.send_to_all_clients(f'Client with rank {rank} disconnected.')
            self.promote_clients(rank)

    def promote_clients(self, disconnected_rank):
        for r in range(disconnected_rank + 1, self.max_clients):
            if r in self.clients:
                client_socket = self.clients[r]
                self.ranks[client_socket] = r - 1
                self.clients[r - 1] = client_socket
                del self.clients[r]
                self.send_to_all_clients(f'Client with rank {r} promoted to rank {r-1}.')

    def send_to_all_clients(self, message):
        for client_socket in self.clients.values():
            client_socket.send(message.encode())

    def assign_rank(self):
        for rank in range(self.max_clients):
            if rank not in self.clients:
                return rank
