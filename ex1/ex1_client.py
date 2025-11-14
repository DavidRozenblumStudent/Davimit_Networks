import sys
from socket import *
from DYSC_protocol import *

# CONSTS
HOSTNAME = "127.0.0.1"
DEF_PORT = 1377
RECV_BUFFER_SIZE = 1024
INVALID_CMD_MSG = "Invalid command."

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
            input_data = clientSock.recv(RECV_BUFFER_SIZE)
            msg = DYSC.parse_msg(input_data.decode())[1][0]
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
                    msg = DYSC.build_msg(QUERY_TYPES.QUIT.value, [])
                    clientSock.send(msg)
                
                    # waiting for server acknowledgment
                    clientSock.recv(RECV_BUFFER_SIZE)
                    break
                
                # if login command:
                elif line[0] == "User:":
                    # get username
                    username = original_line[len("User: "):]
                    
                    # read password from stdin
                    original_line = input()
                    line = original_line.split()
                    if len(line) > 0 and line[0] == "Password:":
                        password = original_line[len("Password: "):]
                        
                        # build LOGIN message
                        msg = DYSC.build_msg(QUERY_TYPES.LOGIN.value, [username, password])
                    else:
                        print(INVALID_CMD_MSG)
                        break

                # if parentheses command, build BALANCED_PARENTHESES message
                elif len(line) == 2 and line[0] == "parenthesis:":
                    msg = DYSC.build_msg(QUERY_TYPES.BALANCED_PARENTHESES.value, [line[1]])
                
                # if lcm command, send LCM message
                elif len(line) == 3 and line[0] == "lcm:":
                    msg = DYSC.build_msg(QUERY_TYPES.LCM.value, [line[1], line[2]])
                
                # if Cesar command
                elif len(line) == 3 and line[0] == "cesar:":
                    msg = DYSC.build_msg(QUERY_TYPES.CESAR_CIPHER.value, [line[1], line[2]])

                # else, invalid command
                else:
                    print(INVALID_CMD_MSG + "2")
                    break

                # send message to server
                clientSock.send(msg)
                        
                # waiting for server response
                input_data = clientSock.recv(RECV_BUFFER_SIZE)
                response = DYSC.parse_msg(input_data.decode())
                
                # check for errors
                if response[0] != ERROR_CODES.NO_ERROR.value:
                    print(f"ERROR - {response[0]}: {response[1][0]}")
                    break # breaking because all errors are fatal

                print(f"{response[1][0]}")
                
        return None


if __name__ == "__main__":
    # Validate command-line arguments
    if(len(sys.argv) < 1 or len(sys.argv) > 3):
        print("Usage: python ex1_client.py [hostname [port]]") # Hostname is allowed without port, but not vice verca 
        sys.exit(1)

    port = DEF_PORT
    
    if len(sys.argv) >= 2:
        HOSTNAME = sys.argv[1]
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number. Try again.")
            sys.exit(1)
    
    print(f"Connecting to server at {HOSTNAME} on port {port}")
    
    # create client instance and run
    client_instance = client(HOSTNAME, port)
    client_instance.run()