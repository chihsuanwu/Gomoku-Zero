import network as net
import board


class Node(object):
    # UCT Node.
    # NOTE: This class is very size-sensitive.
    def __init__(self, move, row, col, nn_policy, nn_value):
        self._row = row
        self._col = col
        self._nn_value = nn_value
        self._nn_polivy = nn_policy
        self._visit_count = 1
        self._move = move
        self._children = []

    # Create all legal children.
    # Each child could be a real pointer is child exist,
    # or just am array taht includes [row, col, nn_policy].
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

    def select_child(self):
        best = None
        best_value = 0.0
        for child in self._children:
            if type(child) is Node:
                win_rate = child._nn_value
                child_visit = child._visit_count
                child_policy = child._nn_polivy
            else:
                win_rate = 1 - self._nn_value
                child_visit = 0
                child_policy = child[2]

            # Uct value
            value = win_rate + (child_policy / (1 + child_visit))

            if value > best_value:
                best_value = value
                best = child

        return best


class UctTree(object):
    """docstring for UctTree"""
    def __init__(self, net_path='nn/net'):
        self._network = net.Network()
        self._network.set_up()
        self._board = board.Board()
        if net_path is not None:
            self._network.load(net_path)

        self.restart()

    def restart(self):
        self._board.clear()

        data = self._board.get_data_for_nn()
        policy = self._network.output_policy(data)
        value = self._network.output_value(data)

        self._root = Node(0, -1, -1, 0, value)
        self._root.create_children(policy, self._board)
        self._cur_node = self._root

    def mcts_visit(self, visit):
        pass

    def select_until_leaf(self):
        while True:
            pass

    def back_prop(self):
        pass

    def play(self, row, col):
        win = self._board.play(row, col)
        if win:
            return True

        for child in self._cur_node._children:
            if child is Node:
                if child._row == row and child._col == col:
                    self._cur_node = child
                    return False
            else:
                if child[0] == row and child[1] == col:
                    #child = Node(0, -1, -1, 0, value)
                    pass

    def predict_current(self):
        return self._network.output_value(self._board.get_data_for_network())


def main():
    tree = UctTree('net/nn')
    while 1:
        row, col = map(int, input('Row Col: ').split())
        tree.play(int(row), int(col))
        print(tree.predict_current())


if __name__ == '__main__':
    main()
