import sys
from socket import *
from DYSC_protocol import *
import errno
from select import select
import math

# CONSTS
QUEUE_SIZE = 5
SERVER_PORT = 1377
WELCOME_MSG = "Welcome! Please log in."
FAIL_TO_LOGIN_MSG = "Failed to login."

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
        welcome_msg =  DYSC.build_msg(ERROR_CODES.NO_ERROR.value, [WELCOME_MSG])

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
            return (-1, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, [FAIL_TO_LOGIN_MSG]))
        return (ERROR_CODES.NO_ERROR.value, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, [f"Hi {username}, good to see you"]))

    def service_balanced_parentheses(self, input_data):
        '''Handle BALANCED_PARENTHESES service.'''
        if len(input_data) != 1:
            return (ERROR_CODES.INVALID_INPUT.value,
                    DYSC.build_msg(ERROR_CODES.INVALID_INPUT.value, ["Balanced parentheses requires 1 string"]))
        s = str(input_data[0])
        stack = []
        for ch in s:
            if ch == '(':
                stack.append(ch)
            elif ch == ')':
                if not stack:
                    result = "NO"
                    break
                stack.pop()
        else:
            result = "YES" if not stack else "NO"
        return (ERROR_CODES.NO_ERROR.value, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, [result]))

    def service_lcm(self, input_data):
        '''Handle LCM service.'''
        try:
            assert(len(input_data) == 2)
            a = int(input_data[0])
            b = int(input_data[1])
        except Exception:
            return (ERROR_CODES.INVALID_INPUT.value,
                    DYSC.build_msg(ERROR_CODES.INVALID_INPUT.value, ["LCM arguments must be 2 integers"]))

        if a == 0 and b == 0:
            return (ERROR_CODES.INVALID_INPUT.value,
                    DYSC.build_msg(ERROR_CODES.INVALID_INPUT.value, ["LCM undefined for both operands zero"]))
        g = math.gcd(a, b)
        lcm = 0 if g == 0 else abs(a * b) // g
        return (ERROR_CODES.NO_ERROR.value, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, [str(lcm)]))

    def service_cesar_cipher(self, input_data):
        '''Handle CESAR_CIPHER service.'''
        if len(input_data) != 2:
            return (ERROR_CODES.INVALID_INPUT.value,
                    DYSC.build_msg(ERROR_CODES.INVALID_INPUT.value, ["Cesar cipher requires shift and text"]))
        
        try:
            shift = int(input_data[0])
        except Exception:
            return (ERROR_CODES.INVALID_INPUT.value,
                    DYSC.build_msg(ERROR_CODES.INVALID_INPUT.value, ["Shift must be an int"]))
        
        text = str(input_data[1])
        sshift = shift % 26
        out_chars = []
        for ch in text:
            if 'a' <= ch <= 'z':
                out_chars.append(chr((ord(ch) - ord('a') + sshift) % 26 + ord('a')))
            elif 'A' <= ch <= 'Z':
                out_chars.append(chr((ord(ch) - ord('A') + sshift) % 26 + ord('A')))
            else:
                out_chars.append(ch)
        ciphered = ''.join(out_chars)
        return (ERROR_CODES.NO_ERROR.value, DYSC.build_msg(ERROR_CODES.NO_ERROR.value, [ciphered]))

    def services(self, code, input_data):
        '''
        Handle different services based on the code argument.
        Returns (error_code_int, msg_bytes).
        '''
        if code == QUERY_TYPES.BALANCED_PARENTHESES.value:
            return self.service_balanced_parentheses(input_data)
        elif code == QUERY_TYPES.LCM.value:
            return self.service_lcm(input_data)
        elif code == QUERY_TYPES.CESAR_CIPHER.value:
            return self.service_cesar_cipher(input_data)
        else:
            return (ERROR_CODES.ILLEGAL_QUERY.value,
                    DYSC.build_msg(ERROR_CODES.ILLEGAL_QUERY.value, ["Illegal query or unsupported operation"]))


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
