import uct_tree
import board as bd


def main():
    tree = uct_tree.UctTree('net/nn')
    mc = 1000
    while 1:
        tree.mcts_visit(mc)
        print('Finish mcts')
        row, col = tree.get_best_move()
        if tree.play(row, col) != bd.Board.NOTHING:
            tree.restart()
        tree.print_board()
        print("%c[%d;%df" % (0x1B, 0, 0), end='')


if __name__ == '__main__':
    main()
