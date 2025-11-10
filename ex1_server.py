import sys
from socket import *
from dysc_protocol import *
import errno
from select import select

# CONSTS
QUEUE_SIZE = 5
SERVER_PORT = 1377

class server:

    def __init__(self, users_file, server_port=SERVER_PORT):
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
        try:
            listen_socket = socket(AF_INET, SOCK_STREAM)
            listen_socket.bind(('', self.server_port))
            listen_socket.listen(QUEUE_SIZE)
            print(f"Server listening on port {self.server_port}...")
        except OSError as e:
            print(f"Error starting server: {e}")
            sys.exit(1)

        # prepare for select loop
        rlist = [listen_socket]
        wlist = []
        xlist = []

        # socket msg dictionary
        socket_msg_dict = {}
        welcome_msg =  DYSC.build_msg(ERROR_CODES.NO_ERROR.value, ["Welcome! Please log in"])

        while True:
            # select readable, writable sockets
            readable, writable, _ = select(rlist, wlist, xlist)

            # first handle incoming messages
            for sock in readable:
                # if new connection
                if sock is listen_socket:
                    try:
                        client_socket, _ = listen_socket.accept()
                        rlist.append(client_socket)
                        wlist.append(client_socket)
                        # set welcome message
                        socket_msg_dict[client_socket] = (ERROR_CODES.NO_ERROR.value, welcome_msg)
            
                    except OSError as e:
                        print(f"Error accepting new connection: {e}")
                    
                else:
                    # existing connection, receive data
                    try:
                        input_data = sock.recv(1024)
                        code, payload = DYSC.parse_msg(input_data.decode())

                        #if yet to login
                        if socket_msg_dict[sock] != None and socket_msg_dict[sock][0] < 0:
                            # if not login query, illegal access
                            if code != QUERY_TYPES.LOGIN.value:
                                error_msg = DYSC.build_msg(ERROR_CODES.ILLEGAL_QUERY.value, ["Illegal Access, yet to login"])
                                socket_msg_dict[sock] = (ERROR_CODES.ILLEGAL_QUERY.value, error_msg)
                                continue # to next readable socket
                            
                            # attempt login
                            socket_msg_dict[sock] = self.attempt_login(payload)
                        
                        else:
                            # if logged in already but sent login query again, illegal query
                            if code == QUERY_TYPES.LOGIN.value:
                                error_msg = DYSC.build_msg(ERROR_CODES.ILLEGAL_QUERY.value, ["Already logged in"])
                                socket_msg_dict[sock] = (ERROR_CODES.ILLEGAL_QUERY.value, error_msg)
                           
                            else: # handle services
                                socket_msg_dict[sock] = self.services(code, payload)

                    # if throwm error during parsing, send invalid format error (later close socket)
                    except ValueError:
                        error_msg = DYSC.build_msg(ERROR_CODES.INVALID_MSG_FORMAT.value, ["Invalid Message Format"])
                        socket_msg_dict[sock] = (ERROR_CODES.INVALID_MSG_FORMAT.value, error_msg)

            # now handle outgoing messages
            for sock in writable:
                # check if there's a message to send
                if socket_msg_dict[sock] != None:
                    code, msg = socket_msg_dict[sock]
                    try:
                        # if we want to ignore this msg - sentinal for not logged in
                        if code < -1:
                            continue # already sended failed login message

                        # send message
                        sock.send(msg)


                        # if failed\yet to log in, update so would only send once
                        if code == -1 or socket_msg_dict[sock][1] == welcome_msg:
                            socket_msg_dict[sock] = (-2, b"")
                       
                        # if message was error, close socket
                        elif code != ERROR_CODES.NO_ERROR.value:
                            rlist.remove(sock)
                            wlist.remove(sock)
                            del socket_msg_dict[sock]
                            sock.close()
                       
                        else:
                            # clear message after sending
                            socket_msg_dict[sock] = None

                    except OSError as e:
                        print(f"Error occured while sending message to client: {e}")
                    
        return None

    def attempt_login(self, payload):
        '''
        Attempt to login with the given payload [username, password].
        checks if the username and password match.
        returns 0 on success, -1 on failure.
        '''
        if len(payload) != 2:
            return (ERROR_CODES.INVALID_INPUT.value, DYSC.build_msg(ERROR_CODES.INVALID_INPUT.value, ["Login requires username and password"]))
        
        username, password = payload
        if self.users_dict.get(username) != password:
            return (-1, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, ["Failed to login."]))
        return (ERROR_CODES.NO_ERROR.value, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, [f"Hi {username}, good to see you"]))

    def services(self, code, input_data):
        '''
        Handle different services based on the func argument.
        '''
        return (ERROR_CODES.NO_ERROR.value, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, ["Not implemented"]))  # TODO


if __name__ == "__main__":

    # Validate command-line arguments
    if(len(sys.argv) < 2 or len(sys.argv) > 3):
        print("Usage: python ex1_server.py users_file_path [server_port]")
        sys.exit(1)

    server_port = SERVER_PORT

    user_file = sys.argv[1]
    if len(sys.argv) == 3:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number. Try again.")
            sys.exit(1)

    # Create and run server instance
    server_instance = server(user_file, server_port)
    server_instance.run()
