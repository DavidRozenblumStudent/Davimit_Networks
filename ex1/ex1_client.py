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
        with socket(AF_INET, SOCK_STREAM) as clientSock:
            # connect to server and display first message
            clientSock.connect((self.hostname, self.port))
            input_data = clientSock.recv(1024)
            msg = SCYD.parse_msg(input_data.decode())[1][0]
            print(f"{msg}")

            while True:
                # read line from terminal
                original_line = input()
                line = original_line.split()
                msg = ""

                # if empty line, continue
                if len(line) == 0:
                    continue

                # if quit command, send QUIT message and break
                elif len(line) == 1 and line[0] == "quit":
                    msg = SCYD.build_msg(QUERY_TYPES.QUIT.value, [])
                    clientSock.send(msg)
                
                    # waiting for server acknowledgment
                    clientSock.recv(1024)
                    break
                
                # if login command:
                elif line[0] == "User:":
                    # get username
                    username = original_line[len("User: "):]
                    
                    # read password from stdin
                    original_line = input()
                    line = original_line.split()
                    if line[0] == "Password:":
                        password = original_line[len("Password: "):]
                        
                        # build LOGIN message
                        msg = SCYD.build_msg(QUERY_TYPES.LOGIN.value, [username, password])

                # if parenthases command, build BALANCED_PARENTHESES message
                elif len(line) == 2 and line[0] == "parenthases":
                    msg = SCYD.build_msg(QUERY_TYPES.BALANCED_PARENTHESES.value, [line[1]])
                
                # if lcm command, send LCM message


                # if Cesar command

                # else, invalid command
                else:
                    print("Invalid command.")
                    break

                # send message to server
                clientSock.send(msg)
                        
                # waiting for server response
                input_data = clientSock.recv(1024)
                response = SCYD.parse_msg(input_data.decode())
                
                # check for errors
                if response[0] != ERROR_CODES.NO_ERROR.value:
                    print(f"ERROR - {response[0]}: {response[1][0]}")
                    break # breaking because all errors are fatal

                print(f"{response[1][0]}")



        return None



if __name__ == "__main__":
    # Validate command-line arguments
    if(len(sys.argv) < 1 or len(sys.argv) > 3):
        print("Usage: python ex1_client.py [hostname(optional) [port (only with hostname)]]")
        sys.exit(1)

    # set default hostname and port
    hostname = "127.0.0.1"
    port = 1377
    if len(sys.argv) >= 2:
        hostname = sys.argv[1]
        if len(sys.argv) == 3:
            port = int(sys.argv[2])
    
    print(f"Connecting to server at {hostname} on port {port}")
    
    # create client instance and run
    client_instance = client(hostname, port)
    client_instance.run()