import socket

IP = "127.0.0.1"
PORT = 10000


def playTheGame(c_soc):
    """
    Handles the process of the game, from the client side
    :param c_soc:
    :return:
    """
    finish = False
    while not finish:
        try:
            print(c_soc.recv(1024).decode())
        except socket.timeout:
            print("Timed out")
            c_soc.close()
            return

        column = input("Choose column to drop in (1-7)")
        while not column.isdigit() and (int(column) > 7 or int(column) < 1):
            column = input("Choose column to drop in (1-7)")
        c_soc.send(column.encode())


def chooseTheGame(c_soc):
    """
    Handles the process of choosing the level of the game, from the client side
    :param c_soc:
    :return:
    """
    try:
        print(c_soc.recv(1024).decode())  # choose to start the game or not
    except socket.timeout:
        c_soc.close()
        return

    option = input()  # get data from user
    while not option.isdigit() and (int(option) > 2 or int(option) < 1):
        option = input("Choose number (1 or 2)")
    c_soc.send(option.encode())  # send to server

    try:
        print(c_soc.recv(1024).decode())  # choose the level
    except socket.timeout:
        c_soc.close()
        return

    option = input()  # get data from user
    while not option.isdigit() and (int(option) > 2 or int(option) < 1):
        option = input("Choose number (1 or 2)")
    c_soc.send(option.encode())  # send to server

    playTheGame(c_soc)


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    chooseTheGame(client_socket)


if __name__ == '__main__':
    main()
