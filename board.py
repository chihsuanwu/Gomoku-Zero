class Board(object):
    # Gomoku board
    BOARD_DIMEN = 15
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    PASS = -1
    DIR_4 = [[0, 1], [1, 0], [1, 1], [1, -1]]

    def __init__(self):
        self.clear()

    def clear(self):
        self._board = [[self.EMPTY]*15 for _ in range(15)]
        self._move = 0

    def who_turn(self):
        return self.BLACK if self._move % 2 == 0 else self.WHITE

    # Return data that going to feed into network.
    # There are 5 feature maps:
    # 1: Black's stone
    # 2: White's stone
    # 3: Empty position
    # 4: 1 if black's turn else 0
    # 4: 1 if white's turn else 0
    def get_data_for_network(self):
        data = []
        for row in range(self.BOARD_DIMEN):
            sub_data = []
            for col in range(self.BOARD_DIMEN):
                point_data = []
                if self._board[row][col] == self.BLACK:
                    point_data += [1, 0, 0]
                elif self._board[row][col] == self.WHITE:
                    point_data += [0, 1, 0]
                else:
                    point_data += [0, 0, 1]

                if self.who_turn() == self.BLACK:
                    point_data += [1, 0]
                else:
                    point_data += [0, 1]

                sub_data.append(point_data)
            data.append(sub_data)
        return data

    def play(self, row, col):
        if (self._board[row][col] != self.EMPTY):
            print('ERROR: play at invalid position.')
            return

        self._board[row][col] = self.who_turn()
        self._move += 1
        return self._check_win(row, col)

    def is_legal_move(self, row, col):
        return self._board[row][col] == self.EMPTY

    # Check the current move five in a row.
    def _check_win(self, row, col):
        def _out_of_bound(row, col):
            return row < 0 or row > 14 or col < 0 or col > 14

        check_color = self._board[row][col]
        for row_dir, col_dir in self.DIR_4:
            count = 0
            for d in range(2):
                for offset in range(1, 5):
                    cur_row = row + (row_dir if d == 0 else -row_dir) * offset
                    cur_col = col + (col_dir if d == 0 else -col_dir) * offset

                    if _out_of_bound(cur_row, cur_col):
                        break

                    if self._board[cur_row][cur_col] != check_color:
                        break

                    count += 1

            if count >= 4:
                return True

        return False

    # Print board, for debug usage.
    def print_board(self):
        def _start_point(row, col):
            return ((row == 8 and col == 8) or
                    (row == 4 and (col == 4 or col == 12)) or
                    (row == 12 and (col == 4 or col == 12)))

        board = ''
        for row in range(self.BOARD_DIMEN + 2):
            for col in range(self.BOARD_DIMEN + 2):
                if row == 0 or row == self.BOARD_DIMEN + 1:
                    # If at the first or the last row,
                    # print the coordinate with letter.
                    if col == 0 or col == self.BOARD_DIMEN + 1:
                        board += '    '
                    else:
                        board += '   ' + chr(64 + col)
                elif col == 0 or col == self.BOARD_DIMEN + 1:
                    # If at the first or the last column,
                    # print the coordinate with number.
                    if col == 0:
                        board += '{:>4}'.format(row)
                    else:
                        board += '    ' + str(row)
                else:
                    if col == 1:
                        board += '   '
                    elif row == 1 or row == self.BOARD_DIMEN:
                        board += '═══'
                    elif _start_point(row, col):
                        board += '──╼'
                    elif _start_point(row, col - 1):
                        board += '╾──'
                    else:
                        board += '───'

                    if (self._board[row - 1][col - 1] == self.EMPTY):
                        if row == 1:
                            if col == 1:
                                board += '╔'
                            elif col == self.BOARD_DIMEN:
                                board += '╗'
                            else:
                                board += '╤'
                        elif row == self.BOARD_DIMEN:
                            if col == 1:
                                board += '╚'
                            elif col == self.BOARD_DIMEN:
                                board += '╝'
                            else:
                                board += '╧'
                        else:
                            if col == 1:
                                board += '╟'
                            elif col == self.BOARD_DIMEN:
                                board += '╢'
                            else:
                                board += '╋' if _start_point(row, col) else '┼'
                    else:
                        board += 'X' if self._board[row - 1][col - 1] == self.BLACK else 'O'

                    # If at the last column, print \n.
                if col == self.BOARD_DIMEN + 1:
                    board += '\n    '

                    # If not at the first or last row, print │ between two row.
                    if 0 < row < self.BOARD_DIMEN:
                        for i in range(15):
                            if i == 0 or i == self.BOARD_DIMEN - 1:
                                board += '   ║'
                            else:
                                board += '   │'
                    board += '\n'

        print(board)


def main():
    board = Board()

    while 1:
        row, col = map(int, input('Row Col: ').split())
        result = board.play(int(row), int(col))
        board.print_board()
        print(result)
        print(board.get_data_for_network())
        if (result):
            print('Win')
            board.clear()


if __name__ == '__main__':
    main()
