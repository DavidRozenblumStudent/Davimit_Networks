# GENERAL USE:
# ./ex1_server.py users_file [port]
# ./ex1_client.py [hostname [port]]

python3 ./ex1_server.py tests/users.txt 12345
python3 ./ex1_client.py 127.0.0.1 12345