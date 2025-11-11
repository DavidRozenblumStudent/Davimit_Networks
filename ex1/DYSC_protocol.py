import enum

class QUERY_TYPES(enum.Enum):
    LOGIN = 0
    BALANCED_PARENTHESES = 1
    LCM = 2
    CESAR_CIPHER = 3
    QUIT = 4

class ERROR_CODES(enum.Enum):
    NO_ERROR = 0
    INVALID_MSG_FORMAT = 1
    INVALID_INPUT = 2
    ILLEGAL_QUERY = 3

class DYSC:
    PROTOCOL_VERSION = 1

    @staticmethod
    def build_msg(opcode, payload):
        '''
        Build a byte message from a pyload (list) and query type(int).
        '''
        return tuple([opcode, payload]).__str__().encode()
    
    @staticmethod
    def parse_msg(input_str):
        '''
        Parse the input string from the client into a tuple (int, list).
        Return the tuple if valid, else raise ValueError.
        '''
        try:
            input_tuple = eval(input_str)
            if isinstance(input_tuple, tuple) and len(input_tuple) == 2 and isinstance(input_tuple[0], int) and isinstance(input_tuple[1], list):
                return input_tuple
            else:
                raise ValueError("WRONG FORMAT!")
        except Exception as e:
            raise ValueError(e)
        return None

