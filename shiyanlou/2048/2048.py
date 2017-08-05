#-*- coding:utf-8 -*-

from random import randrange, choice
from collections import defaultdict
import curses


letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
# ord() would return unicode code number of character
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actions_dict = dict(zip(letter_codes, actions * 2))


def get_user_action(keyboard):
    char = 'N'
    while char not in actions_dict:
        char = keyboard.getch()
        # getch() do not understand
    return actions_dict[char]


def transpose(field):
    return [list(row) for row in zip(*field)]

def invert(field):
    return [row[::-1] for row in field]


class ChessBoard(object):

    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        self.width = width
        self.win_value = win
        self.score = 0
        self.highscore = 0
        self.reset()

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)]
                      for j in range(self.height)]
        self.spawn()
        self.spawn()

    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        def cast(string):
            screen.addstr(string + '\n')

        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hor_separator, "counter"):
                draw_hor_separator.counter = 0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1

        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else
                         '|      ' for num in row) + '|')
        screen.clear()
        cast('SCORE: ' + str(self.score))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    def spawn(self):
        # create new element
        new_element = 4 if randrange(100) > 89 else 2
        # chose field to be filled
        (i, j) = choice([(i, j) for i in range(self.width)
                         for j in range(self.height)
                         if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def move(self, direction):
        def move_row_left(row):
            def tighten(row):
                new_row = [i for i in row if i != 0]
                # move all non-zero elements to left
                new_row += [0 for i in range(len(row) - len(new_row))]
                # add zero to the end
                return new_row

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        # create new list after merge
                        # 0 is not important at this function
                        # it would be tightened anyway
                        if i + 1 < len(row) and row[i] == row[i+1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
            return tighten(merge(tighten(row)))

        moves = {}
        moves['Left'] = lambda field:\
            [move_row_left(row) for row in field]
        moves['Right'] = lambda field:\
            invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field:\
            transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field:\
            transpose(moves['Right'](transpose(field)))

        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    def is_win(self):
        return any(any(i >= self.win_value for i in row)
                    for row in self.field)
        # Condition for win, any tile is larger than win_value

    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                    # movable
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range (len(row)-1))

        check = {}
        check['Left'] = lambda field:\
            any(row_is_left_movable(row) for row in field)
        check['Right'] = lambda field:\
            check['Left'](invert(field))
        check['Up'] = lambda field: \
            check['Left'](transpose(field))
        check['Down'] = lambda field:\
            check['Right'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False
def main(stdscr):
    def init():
        game_field.reset()
        return 'Game'

    def not_game(state):
        game_field.draw(stdscr)
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        action = get_user_action(stdscr)
        return responses[action]

    def game():
        game_field.draw(stdscr)
        action = get_user_action(stdscr)

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game,
    }

    curses.use_default_colors()
    game_field = ChessBoard(win = 32)

    state = 'Init'

    while state != 'Exit':
        state = state_actions[state]()
        # Understand it as:
        # a = state_actions[state] = lambda: not_game('Win')
        # state = a()


curses.wrapper(main)
