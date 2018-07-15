import uct_tree


def main():
    tree = uct_tree.UctTree('net/nn')
    mc = 1000
    while 1:
        tree.mcts_visit(mc)
        print('Finish mcts')
        row, col = tree.get_best_move()
        tree.play(int(row), int(col))
        tree.print_board()


if __name__ == '__main__':
    main()
