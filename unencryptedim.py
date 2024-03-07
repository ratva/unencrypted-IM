import argparse
import select
import socket
import sys

def start_server():
    # Create a socket using IPv4 (AF_INET) and TCP (SOCK_STREAM) for the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set the socket address to be reusable
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to a tuple of hostname and port - localhost (127.0.0.1), port 9999
    server_socket.bind(('localhost', 9999))
    # Set socket to start listening, allowing at most 1 queued connection
    server_socket.listen(1)
    # Comment out print statements for gradescope
    # print('Server started on localhost (127.0.0.1)')
    # print('Waiting for a connection...')

    # Wait for a connection, and return the client socket and address once a connection is made
    client_socket, client_address = server_socket.accept()
    # print(f'Client connected: {client_address}')
    return client_socket

def start_client(hostname):
    # Create an IPv4 TCP socket for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set the socket address to be reusable
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Connect socket to an existing hostname on port 9999, else fail and stop program.
    try:
        client_socket.connect((hostname, 9999))
        # Comment out print statements for gradescope
        # print(f'Connected to server: {hostname}')
    except socket.error as err:
        # Comment out print statements for gradescope
        # print(f"Failed to connect: {err}")
        client_socket.close()
        sys.exit(0)
    return client_socket

def main():
    # Create argument parser to handle command line options
    parser = argparse.ArgumentParser(description='Start server or client for P2P IM.')
    # Set it so that only one of server or client options can be selected
    group = parser.add_mutually_exclusive_group(required=True)
    # If server, set arg.s to True
    group.add_argument('--s', action='store_true', help='Start as server')
    # If client, set arg.c to the provided hostname argument
    group.add_argument('--c', metavar='hostname', type=str, help='Start as client and connect to hostname')
    # Parse inputs from the command line when the script was called
    args = parser.parse_args()

    if args.s:
        # Start the server
        sock = start_server()
    else:
        # Start the client and connect to the hostname provided as an argument
        sock = start_client(args.c)

    try:
        # Loop communication until the connection is closed
        while True:
            # Wait until either the stdin or the socket have a message - both are in the incoming data list and so select waits until either is populated.
            readable, _, _ = select.select([sys.stdin, sock], [], [])
            # Iterate over each readable source to manage if both stdin and the socket have new messages at the same time.
            for source in readable:
                if source == sock:
                    # Read message from socket
                    message = sock.recv(1024)
                    # If message is empty it means the connection is closed, so close socket and exit the console
                    if not message:
                        print('Connection closed')
                        sock.shutdown(socket.SHUT_RDWR)
                        sock.close()
                        sys.exit(0)
                    # Otherwise decode the message from bytes to a string and print to console WITHOUT adding a new line \n character
                    print(message.decode(), end='')
                    # Flush the output to prevent issues with gradescope
                    sys.stdout.flush()
                else:
                    # Read message from stdin
                    message = sys.stdin.readline()
                    # Encode the message to bytes and send it to the socket
                    sock.sendall(message.encode())
    except KeyboardInterrupt:
        # Console will show ^C
        print(' received - closing connection')
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        sys.exit(0)
        
if __name__ == "__main__":
    main()