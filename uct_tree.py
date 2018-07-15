import network as net
import board as bd
import copy


class Node(object):
    # UCT Node.
    # NOTE: This class is very size-sensitive.
    def __init__(self, move, row, col, nn_policy, nn_value, parent):
        self._row = row
        self._col = col
        self._nn_value = nn_value
        self._nn_polivy = nn_policy
        self._visit_count = 0
        self._mcts_eval = 0.0
        self._move = move
        self._parent = parent
        self._children = []

    # Create all legal children.
    # Each child could be a real pointer is child exist,
    # or just an array which includes [row, col, nn_policy].
    # nn_policy[225] is 'PASS' move.
    def create_children(self, nn_policy, current_board):
        legal_sum = 0.0
        DIMEN = current_board.BOARD_DIMEN
        for row in range(DIMEN):
            for col in range(DIMEN):
                if current_board.is_legal_move(row, col):
                    pos = row * DIMEN + col
                    self._children.append([row, col, nn_policy[pos]])
                    legal_sum += nn_policy[pos]
        self._children.append([-1, -1, nn_policy[225]])
        legal_sum += nn_policy[225]

        if legal_sum > 0.00001:
            # Re-normalize after removing illegal moves.
            for child in self._children:
                child[2] /= legal_sum
        else:
            # This can happen with new randomized nets.
            policy = 1.0 / len(self._children)
            for child in self._children:
                child[2] = policy

    def _get_win_rate(self):
        return ((self._visit_count + self._mcts_eval) /
                (self._visit_count * 2.0))

    def select_child(self):
        best = -1
        best_value = 0.0
        for idx, child in enumerate(self._children):
            if type(child) is Node:
                if child._visit_count > 0:
                    win_rate = child._get_win_rate()
                    child_visit = child._visit_count
                else:
                    win_rate = 1 - self._nn_value
                    child_visit = 0
                child_policy = child._nn_polivy
            else:
                win_rate = 1 - self._nn_value
                child_visit = 0
                child_policy = child[2]

            # Uct value
            value = win_rate + (child_policy / (1 + child_visit))

            if value > best_value:
                best_value = value
                best = idx

        return best

    def update(self, mcts_eval):
        self._visit_count += 1
        self._mcts_eval += mcts_eval


class UctTree(object):
    """docstring for UctTree"""
    def __init__(self, net_path='nn/net'):
        self._network = net.Network()
        self._network.set_up()
        self._board = bd.Board()
        if net_path is not None:
            self._network.load(net_path)

        self.restart()

    def _create_node(self, move, row, col, cur_policy, board, parent):
        data = board.get_data_for_network()
        policy = self._network.output_policy(data)
        value = self._network.output_value(data)

        new_node = Node(move, row, col, cur_policy, value, parent)
        new_node.create_children(policy, board)
        return new_node

    def restart(self):
        self._board.clear()
        self._root = self._create_node(0, -1, -1, 0, self._board, None)
        self._cur_node = self._root

    def mcts_visit(self, visit):
        mcts_board = copy.deepcopy(self._board)
        for _ in range(visit):
            # Select until reach leaf or someone win.
            leaf_node = self._select_until_leaf(mcts_board)
            self._back_prop(leaf_node, mcts_board)

    def _select_until_leaf(self, board):
        cur_node = self._cur_node
        while True:
            next_node_idx = cur_node.select_child()
            next_node = cur_node._children[next_node_idx]
            if type(next_node) is list:
                someone_win = board.play(next_node[0], next_node[1])
                new_node = self._create_node(cur_node._move + 1,
                                             next_node[0], next_node[1],
                                             next_node[2], board, cur_node)
                cur_node._children[next_node_idx] = new_node
                if someone_win == board.WIN:
                    new_node._nn_value = 1.0
                elif someone_win == board.TIE:
                    new_node._nn_value = 0.0
                elif someone_win == board.LOSE:
                    new_node._nn_value = -1.0
                return new_node

            someone_win = board.play(next_node._row, next_node._col)
            # Stop if someone win.
            if someone_win != board.NOTHING:
                return next_node

            cur_node = next_node

    def _back_prop(self, cur_node, board):
        result_value = cur_node._nn_value
        while cur_node is not self._cur_node:
            cur_node.update(result_value)
            result_value = -result_value
            board.undo(cur_node._row, cur_node._col)
            cur_node = cur_node._parent
        cur_node.update(result_value)

    def get_best_move(self):
        best = 0
        row = -1
        col = -1
        for child in self._cur_node._children:
            if type(child) is Node:
                print('row: {}, col: {}, visit: {}, winrate: {}'
                      .format(child._row, child._col,
                              child._visit_count, child._get_win_rate()))
                if child._visit_count > best:
                    best = child._visit_count
                    row = child._row
                    col = child._col
        return row, col

    def print_board(self):
        self._board.print_board()

    # Play at [row, col], if child node not exist then create it
    # and move '_cur_node' to child node.
    # Return game status.
    def play(self, row, col):
        win = self._board.play(row, col)
        if win != bd.Board.NOTHING:
            print('End game')
            return win

        # Find the next move's child.
        for idx, child in enumerate(self._cur_node._children):
            if type(child) is Node:
                if child._row == row and child._col == col:
                    self._cur_node = child
                    return win
            else:
                if child[0] == row and child[1] == col:
                    new_node = self._create_node(self._cur_node._move + 1,
                                                 row, col, child[2],
                                                 self._board, self._cur_node)
                    # Append new child.
                    self._cur_node._children[idx] = new_node
                    self._cur_node = new_node

                    return win

        print('ERROR')

    def predict_current(self):
        return self._network.output_value(self._board.get_data_for_network())
