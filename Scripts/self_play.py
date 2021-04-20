from game import Game, Board
from player import ConsolePlayer


if __name__ == '__main__':
    game = Game(Board(width=10, n_in_row=5))
    PC1, PC2 = ConsolePlayer(random_move=True), ConsolePlayer(random_move=True)
    game.start_play(PC1, PC2, start_player=Game.PREVIOUS, is_shown=True)