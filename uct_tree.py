import network as net
import board


class Node(object):
    """docstring for Node"""
    def __init__(self, move):
        self._win_count = 0
        self._lose_count = 0
        self._visit_count = 1
        self._move = move
        self._children = []


class UctTree(object):
    """docstring for UctTree"""
    def __init__(self, net_path=None):
        self._network = net.Network()
        self._network.set_up()
        self._board = board.Board()
        if net_path is not None:
            self._network.load(net_path)

    def select(self):
        pass

    def back_prop(self):
        pass

    def play(self, row, col):
        self._board.play(row, col)

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
