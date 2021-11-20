import socket

IP = "127.0.0.1"
PORT = 10000


def playTheGame(c_soc):
    """
    Handles the process of the game, from the client side
    :param c_soc:
    :return:
    """
    return c_soc


def chooseTheGame(c_soc):
    """
    Handles the process of choosing the level of the game, from the client side
    :param c_soc:
    :return:
    """
    try:
        print(c_soc.recv(1024).decode())  # choose to start the game or not
    except():
        c_soc.close()

    option = input()  # get data from user
    c_soc.send(option.encode())  # send to server

    try:
        print(c_soc.recv(1024).decode())  # choose the level
    except():
        c_soc.close()

    option = input()  # get data from user
    c_soc.send(option.encode())  # send to server


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    chooseTheGame(client_socket)


if __name__ == '__main__':
    main()
