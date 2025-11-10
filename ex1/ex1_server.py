import sys
from socket import *
from scyd_protocol import *

QUEUE_SIZE = 5

class server:

    def __init__(self, users_file, server_port=1337):
        '''
        Initialize the server with user dictionary from the given file,
        and set the server port(default 1337).
        '''
        print(f"Starting server with user file: {users_file} on port: {server_port}")
        self.server_port = server_port
        self.users_dict = {}
        
        # open and read users file
        try:
            file = open(users_file, 'r')
            file_text = file.read()
            print(f"Loaded users file: {users_file}")
            file.close() # remember to close file kids ;(
        
        # handle file errors
        except FileNotFoundError:
            print(f"Error: Users file {users_file} not found.")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        
        # parse users file into dictionary
        lines = file_text.splitlines()
        for line in lines:
            user_info = line.split('\t')
            if len(user_info) != 2:
                print(f"Line wrong format - {user_info} - correct format: <username><tab><password>")
                exit(1)
            username, password = user_info
            self.users_dict[username] = password
        
        return None


    
    def run(self):
        # Start server operations here
        listen_socket = socket(AF_INET, SOCK_STREAM)
        listen_socket.bind(('', self.server_port))
        listen_socket.listen(QUEUE_SIZE)
        print(f"Server listening on port {self.server_port}...")

        while True:
            (conn_socket, addr) = listen_socket.accept()
            #print(f"Accepted connection from {addr}")
            #conn_socket.send(b"Hello, Client!")
            
            input_data = conn_socket.recv(1024)
            try:
                input_tuple = SCYD.parse_msg(input_data.decode())
                print(f"Received from client: {input_tuple}")
            except ValueError as ve:
                print(f"Invalid input from client: {ve}")
            
            conn_socket.close()

        return None
    

if __name__ == "__main__":

    # Validate command-line arguments
    if(len(sys.argv) < 2 or len(sys.argv) > 3):
        print("Usage: python ex1_server.py <users_file_path> [server_port(optional)]")
        sys.exit(1)

    # Set default port and parse arguments
    server_port = 1377
    user_file = sys.argv[1]
    if len(sys.argv) == 3:
        server_port = int(sys.argv[2])

    # Create and run server instance
    server_instance = server(user_file, server_port)
    server_instance.run()
