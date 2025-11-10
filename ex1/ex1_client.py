import sys
from socket import *
from scyd_protocol import *

class client:
    def __init__(self, hostname, port):
        print(f"Starting client to connect to {hostname} on port {port}")
        self.hostname = hostname
        self.port = port
    
    def run(self):
        # Start client operations here
        print(f"Client initialized with hostname: {self.hostname}, port: {self.port}")
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((self.hostname, self.port))
        print(f"Connected to server at {self.hostname}:{self.port}")

        client_socket.send(SCYD.build_msg(QUERY_TYPES.LOGIN, ['user','pass']))
        client_socket.close()
        return None



if __name__ == "__main__":
    print("This is the ex1_client module.")
    # TODO: Implement client functionality here.
    if(len(sys.argv) < 1 or len(sys.argv) > 3):
        print("Usage: python ex1_client.py [hostname(optional) [port (only with hostname)]]")
        sys.exit(1)
    hostname = "127.0.0.1"
    port = 1377
    if len(sys.argv) >= 2:
        hostname = sys.argv[1]
        if len(sys.argv) == 3:
            port = int(sys.argv[2])
    print(f"Connecting to server at {hostname} on port {port}")

    client_instance = client(hostname, port)
    client_instance.run()