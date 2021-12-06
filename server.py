import json
import socket
import threading
import random
from time import sleep, time

IP = "127.0.0.1"
PORT = 10000
SOCKET_TIMEOUT = 6000
COLS = 7
ROWS = 6


def findPlaceToDrop(column, player, matrix):
    """
    Find the place to put the token to
    :param column: the column to drop in
    :param player: 1 or 2 - the player number
    :param matrix: The matrix of the game - values
    :return msg with the place in the board or msg that says the column is full:
    """
    msg = ""
    for i in range(ROWS):
        if matrix[i][column] == 0:
            matrix[i][column] = player
            msg = str(i + 1) + ',' + str(column + 1)
            break  # quit the loop
    if msg == "":
        msg = "Full column"
    return msg


def checkWin(matrix):
    """
    Check if there is a win and if so, who won - check if there are 4 same symbols in row, column or diagonal
    :param matrix: The game board - matrix with values
    :return None:
    """
    # check for win for 4 in row
    for i in range(ROWS):
        curr_player = matrix[i][0]
        count_tokens = 1
        for j in range(1, COLS):
            if curr_player == matrix[i][j] and curr_player != 0:  # found token that creates a row
                count_tokens += 1
                if count_tokens == 4:  # found 4 tokens in a row
                    msg = "Computer won!\n" if curr_player == 1 else "You won!\n"
                    return msg
            else:  # found different token that breaks the row
                count_tokens = 1
                curr_player = matrix[i][j]

    # check for win for 4 in column
    for i in range(COLS):
        curr_player = matrix[0][i]
        count_tokens = 1
        for j in range(1, ROWS):
            if curr_player == matrix[j][i] and curr_player != 0:  # found token that creates a column
                count_tokens += 1
                if count_tokens == 4:  # found 4 tokens in a column
                    msg = "Computer won!\n" if curr_player == 1 else "You won!\n"
                    return msg
            else:  # found different token that breaks the column
                count_tokens = 1
                curr_player = matrix[j][i]

    # check for win for 4 in diagonal
    for i in range(ROWS):
        curr_player = matrix[0][i]
        count_tokens = 1
        for j in range(COLS):
            for k in range(i + 1, i + 5):
                try:
                    if curr_player == matrix[i + k][j + k] and curr_player != 0:  # found token that creates a diagonal
                        count_tokens += 1
                        if count_tokens == 4:  # found 4 tokens in a diagonal
                            msg = "Computer won!\n" if curr_player == 1 else "You won!\n"
                            return msg
                    else:  # found different token that breaks the diagonal
                        count_tokens = 1
                        curr_player = matrix[j][i]
                except IndexError:
                    break

    return "No win"


def play_round_easy(client_socket):
    """
    Controls the game, one round - easy level, chooses column for the server to place its token,
    and place the dice in the column from the client.
    :param client_socket: the client socket
    :return tuple - (True if user won or False otherwise, number of rounds):
    """
    matrix = [[0 * x * y for x in range(COLS)] for y in range(ROWS)]  # game board
    done = False
    turns = 0
    while not done:
        turns += 1
        # server turn
        client_socket.send("Computer's turn".encode())  # send it's the computer turn
        rand = random.randrange(COLS)
        msg = findPlaceToDrop(rand, 1, matrix)
        while "Full" in msg:  # the column is full
            rand = random.randrange(COLS)
            msg = findPlaceToDrop(rand, 1, matrix)
        sleep(0.4)

        client_socket.send(json.dumps(matrix).encode())  # let the client know where the token is
        msg = checkWin(matrix)
        sleep(0.4)
        if "won!" in msg:
            client_socket.send(msg.encode())
            return True if "You" in msg else False, turns
        else:
            client_socket.send("Your turn".encode())

        # client turn
        try:
            wc = client_socket.recv(1024).decode()  # get user's column
        except socket.timeout:
            client_socket.close()
            print("client closed - timeout")
            return
        wc = int(wc) - 1
        msg = findPlaceToDrop(wc, 2, matrix)

        while "Full" in msg:  # the column is full
            client_socket.send("The column is full, choose a new one".encode())
            try:
                wc = client_socket.recv(1024).decode()
            except socket.timeout:
                client_socket.close()
                print("client closed - timeout")
                return
            wc = int(wc) - 1
            msg = findPlaceToDrop(wc, 2, matrix)

        client_socket.send(json.dumps(matrix).encode())  # let the client know where the token is
        msg = checkWin(matrix)
        if "won!" in msg:
            client_socket.send(msg.encode())
            return True if "You" in msg else False, turns


def play_round_hard(client_socket):
    """
    Controls the game, one round - hard level, chooses column for the server to place its token,
    and place the dice in the column from the client.
    :param client_socket: the client socket
    :return tuple (True if user won or False otherwise, number of rounds):
    """
    matrix = [[0 * x * y for x in range(COLS)] for y in range(ROWS)]  # game board
    return True, 1


def playGame(client_socket, rounds, level):
    """
    Play the game according to the level and until got the desired amount of wins,
    and calculate some statistics about the game
    :param client_socket: the client socket
    :param rounds: number of wins to win a whole game
    :param level: the level of the game
    :return None:
    """
    stats = {'wins': 0, 'turns': [], 'time': []}
    curr_round = 0
    while stats['wins'] != rounds:
        start = time()  # start count time of round
        if level == '1':  # easy
            win, turns = play_round_easy(client_socket)  # play one round
        else:  # hard
            win, turns = play_round_hard(client_socket)  # play one round
        finish = time()
        curr_round += 1  # remember rounds played
        sleep(0.5)
        stats['time'].append(finish - start)  # remember time
        stats['turns'].append(turns)  # remember turns
        if win:
            stats['wins'] += 1  # remember wins of user
        avg_wins = stats['wins'] / curr_round  # calc avg wins per round
        avg_turns = sum(stats['turns']) / curr_round  # calc avg turns per round

        # make msg after one round
        msg = "\nRound ended, here are the round statistics:\n"
        msg += "You won: " + str(stats['wins']) + " times\n"
        msg += "The Computer won: " + str(curr_round-stats['wins']) + " times\n"
        msg += "Amount of turns for this round: " + str(turns) + "\n"
        msg += "This round took you " + str(format(stats['time'][curr_round - 1], '.3f')) + " seconds\n"
        msg += "Average amount of turns per round: " + str(avg_turns) + "\n"
        msg += "Average amount of wins per round: " + str(avg_wins) + "\n\n"
        client_socket.send(msg.encode())  # send to client

    # make msg after whole game
    sleep(1)
    avg_wins = stats['wins'] / curr_round  # calc avg wins per round
    avg_turns = sum(stats['turns']) / curr_round  # calc avg turns per round
    avg_time = sum(stats['time']) / curr_round  # calc avg time per round
    msg = "\nGame ended, here are the game statistics:\n"
    msg += "You won: " + str(stats['wins']) + " times\n"
    msg += "The Computer won: " + str(curr_round-stats['wins']) + " times\n"
    msg += "Average amount of time per round: " + str(format(avg_time, '.3f')) + " seconds\n"
    msg += "Average amount of turns per round: " + str(avg_turns) + "\n"
    msg += "Average amount of wins per round: " + str(avg_wins) + "\n\n"
    client_socket.send(msg.encode())  # send to client


def play_with_server(client_socket):
    """
    Control the part when the client chooses what level they want to play.
    :param client_socket: The client socket
    :return None:
    """
    # choose level
    msg = "Choose difficulty level:\n1. Easy\n2. Hard"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv(1024).decode("utf-8")
    except socket.timeout:
        # closing connection if the client didn't respond before timeout happened
        client_socket.close()
        print("client closed - timeout")
        return

    # choose amount of wins
    msg = "Choose amount of wins to declare a win in the game (1 or more):"
    client_socket.send(msg.encode("utf-8"))
    cnt = 0  # count to 5, if it's 5, then add delay of 1 second, if it's 5 again and 2s and so on
    done = False
    amount = ""
    times = 1  # count the times the user was wrong 5 times
    while not done:
        msg = ""  # msg to client
        try:
            amount = client_socket.recv(1024).decode("utf-8")
        except socket.timeout:
            # closing connection if the client didn't respond before timeout happened
            client_socket.close()
            print("client closed - timeout")
            return
        if not amount.isdigit() or int(amount) < 1:
            cnt += 1
            msg += "Not valid, left - " + str(5 * times - cnt) + " tries\n"
            if cnt % 5 == 0:
                msg += "You failed " + str(cnt) + " times, therefore you need to wait " + str(cnt / 5) + " seconds"
                times += 1
        else:
            msg = "valid, " + amount
            client_socket.send(msg.encode())
            break
        client_socket.send(msg.encode())
        if cnt % 5 == 0:
            sleep(cnt / 5)

    sleep(0.3)
    client_socket.send("Good luck :)".encode())
    sleep(1)
    playGame(client_socket, int(amount), option)
    sleep(0.3)
    handle_client(client_socket)  # return to main "screen"


def handle_client(client_socket):
    """
    Controls the start of the game - whether the client wants to play with the server or not
    :param client_socket: The client socket
    :return None:
    """
    # handling clients
    msg = "Welcome to the game!\nChoose option:\n1. Play with server \n2. Quit"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv(1024).decode("utf-8")
    except socket.timeout:
        # closing connection if the client didn't respond before timeout happened
        client_socket.close()
        print("client closed - timeout")
        return

    if option == '1':  # play
        play_with_server(client_socket)
    if option == '2':  # quit
        client_socket.close()
        print("client left")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # start the connection - tcp
    server_socket.bind((IP, PORT))  # connect to ip and port
    server_socket.listen(5)  # set amount of clients that can connect

    while True:
        client_socket, client_address = server_socket.accept()  # accept new client
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)  # set timeout to the client

        thread = threading.Thread(target=handle_client, args=(client_socket,))  # create new thread to the client
        thread.start()


if __name__ == '__main__':
    main()
