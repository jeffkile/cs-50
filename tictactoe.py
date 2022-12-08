"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_x = 0
    count_o = 0

    for row in board:
        for cell in row:
            if cell == X:
                count_x += 1
            elif cell == O:
                count_o += 1

    if count_x > count_o:
        return O

    # Assumes X always goes first, so if X and O are equal, it's X's turn or if O has more moves, it's X's turn
    return X

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = []

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                actions.append((row, col))

    return actions

def result(b, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board = deepcopy(b)

    board[action[0]][action[1]] = player(board)

    return board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != EMPTY:
            return row[0]
    
    # Check columns
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != EMPTY:
            return board[0][i]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != EMPTY:
        return board[0][2]

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False

    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    result = winner(board)

    if result == X:
        return 1
    elif result == O:
        return -1
    else:
        return 0

def minimax(b):
    """
    Returns the optimal action for the current player on the board.
    """

    board = deepcopy(b)

    # Get the list of possible actions
    action_list = actions(board)

    # X is trying to maximize the score O is trying to minimize the score
    my_player = player(board)

    if my_player == X:
        best_score = float('-inf')
        best_action = None
        for action in action_list:
            new_board = result(board, action)
            new_score = min_value(new_board)

            if new_score > best_score:
                best_score = new_score
                best_action = action
        
        return best_action

    else:
        best_score = float('inf')
        best_action = None
        for action in action_list:
            new_board = result(board, action)
            new_score = max_value(new_board)

            if new_score < best_score:
                best_score = new_score
                best_action = action
        
        return best_action

def min_value(b):
    board = deepcopy(b)

    if terminal(board):
        return utility(board)
    
    # Get the list of possible actions
    action_list = actions(board)

    best_score = float('inf')
    for action in action_list:
        new_board = result(board, action)
        new_score = max_value(new_board)
        best_score = min(new_score, best_score)

    return best_score

def max_value(b):
    board = deepcopy(b)

    if terminal(board):
        return utility(board)
    
    # Get the list of possible actions
    action_list = actions(board)

    best_score = float('-inf')
    for action in action_list:
        new_board = result(board, action)
        new_score = min_value(new_board)
        best_score = max(new_score, best_score)
    
    return best_score