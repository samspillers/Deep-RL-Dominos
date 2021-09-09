import enum
import random
from abc import ABC, abstractmethod

random = random.Random()
START_HAND_SIZE = 7


class Direction(enum.Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class Domino:
    def __init__(self, num_a: int, num_b: int, num_max: int):
        self.num_a, self.num_b, self.num_max = num_a, num_b, num_max

    def get_id(self) -> int:
        i = 0
        __dom_id = 0
        while i < self.num_a:
            __dom_id += self.num_max - i + 1
            i += 1
        return __dom_id + self.num_max - self.num_b

    @staticmethod
    def id_to_nums(domino_id: int, num_max) -> (int, int):
        assert 0 <= domino_id < ((num_max + 1) * (num_max + 2) / 2) and num_max >= 0
        id_max = int((num_max + 1) * (num_max + 2) / 2) - 1
        i = 0
        while domino_id < id_max - i:
            id_max -= i + 1
            i += 1
        return num_max - i, domino_id - id_max + num_max

    def check_match(self, other: "Domino") -> (int,
                                               int):  # Note: Since there is only one copy of every number pair domino, if a_1 matches b_1, it is impossible for a_2 to match b_2 also. Thus only one return will ever be possible.
        if other is None or not issubclass(type(other), Domino):
            return None

        if self.is_double():
            if self.num_a is other.num_a:
                return 0, 1
            if self.num_a is other.num_b:
                return 0, -1
        if other.is_double():
            if self.num_a is other.num_a:
                return -1, 0
            if self.num_b is other.num_a:
                return 1, 0
        if self.num_b is other.num_a:
            return 1, 1
        elif self.num_b is other.num_b:
            return 1, -1
        elif self.num_a is other.num_a:
            return -1, 1
        elif self.num_a is other.num_b:
            return -1, -1
        else:
            return None  # Should not reach here

    def is_double(self) -> bool:
        return self.num_a is self.num_b


class Board:
    # num_b is outfacing number, a is inner. UNLESS reversed
    class ReversibleDomino(Domino):
        def __init__(self, domino: Domino, reverse: bool):
            super().__init__(domino.num_a, domino.num_b, domino.num_max)
            self.reverse = reverse

        def get_out_facing_number(self):
            return self.num_a if self.reverse else self.num_b

        def get_in_facing_number(self):
            return self.num_b if self.reverse else self.num_a

        def get_out_facing_sum(self):
            if self.is_double():
                return self.num_a * 2
            else:
                return self.get_out_facing_number()

        def get_in_facing_sum(self):
            if self.is_double():
                return self.num_a * 2
            else:
                return self.get_in_facing_number()

    def __init__(self):
        self.spinner = None
        self.north = []
        self.south = []
        self.east = []
        self.west = []

    def play_domino(self, dom: Domino, direction: Direction):
        assert (self.spinner is not None and (direction is Direction.NORTH or direction is Direction.SOUTH) or (
                    (direction is Direction.WEST or direction is Direction.EAST) and (
                        len(self.north) is not 0 and len(self.south) is not 0))) \
               or (self.spinner is None and (direction is Direction.NORTH or direction is Direction.SOUTH))
        if self.spinner is None:  # No spinner case
            if len(self.north) is 0:  # If first piece
                new_dom = self.ReversibleDomino(dom, False)
                if dom.is_double():  # Insert spinner if appropriate
                    self.spinner = new_dom
                else:
                    self.north.append(new_dom)
            else:
                if direction is Direction.NORTH:
                    last_dom = self.north[-1]
                    matches = last_dom.check_match(dom)
                    assert matches is not None and matches[0] * (-1 if last_dom.reverse else 1) is not -1
                    new_dom = self.ReversibleDomino(dom, matches[1] is -1)
                    if dom.is_double():  # Insert spinner if appropriate
                        for i in range(len(self.north)):
                            temp_dom = self.north.pop()
                            temp_dom.reverse = not temp_dom.reverse
                            self.south.append(temp_dom)
                        self.spinner = new_dom
                    else:
                        self.north.append(new_dom)
                else:  # Should only be Direction.SOUTH at this point due to the assertion above
                    assert direction is Direction.SOUTH
                    last_dom = self.north[0]
                    matches = dom.check_match(last_dom)
                    assert matches is not None and matches[1] * (-1 if last_dom.reverse else 1) is not -1
                    new_dom = self.ReversibleDomino(dom, matches[0] is -1)
                    if dom.is_double():  # Insert spinner if appropriate
                        self.spinner = new_dom
                    else:
                        self.north.insert(0, new_dom)
        else:  # Spinner case
            if direction is Direction.NORTH:
                self.__add_dom_to_stack(self.north, dom)
            elif direction is Direction.EAST:
                self.__add_dom_to_stack(self.east, dom)
            elif direction is Direction.SOUTH:
                self.__add_dom_to_stack(self.south, dom)
            elif direction is Direction.WEST:
                self.__add_dom_to_stack(self.west, dom)

    def __add_dom_to_stack(self, stack: list,
                           dom: Domino):  # Should not be called if no spinner and stack length is more than 0
        if len(stack) is 0:
            matches = self.spinner.check_match(dom)
            assert matches is not None and matches[0] * (
                -1 if self.spinner.reverse else 1) is not -1  # Shouldn't ever trigger, but here just in case
            new_dom = self.ReversibleDomino(dom, matches[1] is -1)
            stack.append(new_dom)
        else:
            last_dom = stack[-1]
            matches = last_dom.check_match(dom)
            assert matches is not None and matches[0] * (-1 if last_dom.reverse else 1) is not -1
            new_dom = self.ReversibleDomino(dom, matches[1] is -1)
            stack.append(new_dom)

    def __str__(self) -> str:
        output = "["
        if self.spinner is None:
            output += "Spinner: None, "
        else:
            output += f"Spinner: ({self.spinner.get_in_facing_number()}, {self.spinner.get_out_facing_number()}), "
        output += f"North: [{self.__output_stack(self.north)}], East: [{self.__output_stack(self.east)}], South: [{self.__output_stack(self.south)}], West: [{self.__output_stack(self.west)}]]"
        return output

    def __output_stack(self, stack: list) -> str:
        output = ""
        for i in range(len(stack)):
            x = stack[i]
            output += f"({x.get_in_facing_number()}, {x.get_out_facing_number()})"
            if i < len(stack) - 1:
                output += " - "
        return output

    def get_board_sum(self) -> int:
        # if self.spinner is None:
        #     return 0
        sum = 0
        sum += self.north[-1].get_out_facing_sum() if len(self.north) is not 0 else 0
        sum += self.east[-1].get_out_facing_sum() if len(self.east) is not 0 else 0
        sum += self.south[-1].get_out_facing_sum() if len(self.south) is not 0 else 0
        sum += self.west[-1].get_out_facing_sum() if len(self.west) is not 0 else 0
        if self.spinner is None:
            sum += self.north[0].get_in_facing_sum() if len(self.north) is not 0 else 0
        elif len(self.north) is 0 or len(self.south) is 0:
            sum += self.spinner.get_out_facing_sum()
        return sum

    def get_board_state(self) -> (int, int, int, int, int):
        spinner = self.spinner.get_id() if self.spinner is not None else None
        north = self.north[-1].get_id() if len(self.north) is not 0 else None
        east = self.east[-1].get_id() if len(self.east) is not 0 else None
        south = self.south[-1].get_id() if len(self.south) is not 0 else self.north[0].get_id() if len(
            self.north) is not 0 else None
        west = self.west[-1].get_id() if len(self.west) is not 0 else None
        return spinner, north, east, south, west

    def get_out_facing_numbers(self):
        output = []
        if len(self.north) is not 0:
            output.append(self.north[-1].get_out_facing_number())
        if len(self.east) is not 0:
            output.append(self.east[-1].get_out_facing_number())
        if len(self.south) is not 0:
            output.append(self.south[-1].get_out_facing_number())
        elif len(self.north) is not 0 and self.spinner is None:
            output.append(self.north[0].get_in_facing_number())
        if len(self.west) is not 0:
            output.append(self.west[-1].get_out_facing_number())
        if self.spinner is not None and (len(self.west) is 0 or len(self.east) is 0 or len(self.north) is 0 or len(self.south) is 0):
            output.append(self.spinner.get_out_facing_number())
        return output

    def is_empty(self):
        return self.spinner is None and len(self.north) is 0 and len(self.south) is 0 and len(self.east) is 0 and len(self.west) is 0


class Game:
    class Player(ABC):
        @abstractmethod
        def take_turn(self, current_board: Board, current_hand: list, curr_player_num: int, players: list, scores: dict, pile_size: int):
            pass

    def __init__(self, max_num: int, score_to_win: int, players: list):  # players list must contain objects with a take_turn(current_board, current_hand) method
        self.score_to_win = score_to_win
        self.max_num = max_num
        self.players = players
        self.scores = self.__init_scores()
        self.__shuffle_current_turn()
        self.last_played = None

    def __shuffle_current_turn(self):
        self.current_turn = random.randint(0, len(self.players) - 1)

    def __find_max_double_player(self):
        pass  # TODO: This

    def __init_round(self, shuffle_current_player: bool = False):
        self.board = Board()
        self.pile = self.__init_pile(self.max_num)
        self.hands = self.__init_hands()
        if shuffle_current_player:
            self.__shuffle_current_turn()
        for hand in self.hands.values():
            for _ in range(START_HAND_SIZE):
                hand.append(self.__draw_random_dom_from_pile())

    def __init_pile(self, max_num: int):
        pile = []
        max_dom = Domino(max_num, max_num, max_num)  # Create largest possible domino double, get its id to find max id
        max_id = max_dom.get_id()
        for id in range(max_id):
            pile.append(Domino(*Domino.id_to_nums(id, max_num), max_num))
        pile.append(max_dom)
        return pile

    def __init_hands(self):
        hands = {}
        for player in self.players:
            hands[player] = []
        return hands

    def __draw_random_dom_from_pile(self):
        assert len(self.pile) > 0
        return self.pile.pop(random.randint(0, len(self.pile) - 1))

    def __check_for_winner(self):
        for player in self.players:
            if self.scores[player] >= self.score_to_win:
                return player
        return None

    def play_match(self):
        print("Starting new match")
        while self.__check_for_winner() is None:
            self.play_game()
        scores_string = ""
        for player in self.players:
            scores_string += f"{self.scores[player]} "
        print(f"Scores: {scores_string}")
        print("Finished match")

    def play_game(self):
        print("Starting new game")
        self.__init_round(False)
        game_over = False
        while not game_over:
            game_over = self.take_turn()
        print("Finished game")

    def __check_if_can_play(self, player: Player):
        board_numbers = set(self.board.get_out_facing_numbers())
        hand = self.hands[player]
        hand_numbers = set()
        for x in hand:
            hand_numbers.add(x.num_a)
            hand_numbers.add(x.num_b)
        return len(board_numbers.intersection(hand_numbers)) is not 0 or self.board.is_empty()

    def take_turn(self) -> bool:
        current_player = self.players[self.current_turn]
        current_hand = self.hands[current_player]
        current_board = self.board
        if not self.__check_if_can_play(current_player) and len(self.pile) == 0:
            # print(f"Can't play. Full cycle?: {self.last_played == self.current_turn}, ({self.last_played}, {self.current_turn})")
            actual_current_turn = self.current_turn
            self.current_turn = (self.current_turn + 1) % len(self.players)
            return self.last_played == actual_current_turn  # Check if full cycle of lock
        successful = False
        while not successful:
            (dom_index, direction) = current_player.take_turn(current_board, current_hand, self.current_turn, self.players, self.scores, len(self.pile))  # Note: Giving the player the board allows them to cheat. For security, change to a copy of the board in the future
            if dom_index != -1:
                dom_to_play = current_hand[dom_index]
                try:  # TODO: This method sucks
                    self.board.play_domino(dom_to_play, direction)
                    successful = True
                    current_hand.pop(dom_index)
                    self.last_played = self.current_turn
                except:
                    pass
            else:
                if len(self.pile) > 0:
                    current_hand.append(self.__draw_random_dom_from_pile())
                    return False
        board_sum = self.board.get_board_sum()
        if board_sum % 5 == 0:
            self.scores[current_player] += board_sum
        if len(current_hand) == 0:
            sum = 0
            for hand in self.hands.values():
                current_sum = 0
                for dom in hand:
                    current_sum += dom.num_a + dom.num_b
                sum += int(5 * round(float(current_sum) / 5))  # Rounds each hand to the nearest 5
            self.scores[current_player] += sum
            return True
        self.current_turn = (self.current_turn + 1) % len(self.players)
        return self.__check_for_winner()

    def __init_scores(self):
        scores = {}
        for player in self.players:
            scores[player] = 0
        return scores


class RandomPlayer(Game.Player):
    def take_turn(self, current_board: Board, current_hand: list, curr_player_num: int, players: list, scores: dict, pile_size: int):
        options = []
        if pile_size > 0:
            options.append((-1, None))
        if current_board.is_empty():
            for i in range(len(current_hand)):
                options.append((i, Direction.NORTH))
        else:
            out_facing_numbers = []
            if len(current_board.north) != 0:
                out_facing_numbers.append((current_board.north[-1].get_out_facing_number(), Direction.NORTH))
            elif current_board.spinner is not None:
                out_facing_numbers.append((current_board.spinner.get_out_facing_number(), Direction.NORTH))
            if len(current_board.south) != 0:
                out_facing_numbers.append((current_board.south[-1].get_out_facing_number(), Direction.SOUTH))
            else:
                if len(current_board.north) != 0 and current_board.spinner is None:
                    out_facing_numbers.append((current_board.north[0].get_in_facing_number(), Direction.SOUTH))
                if current_board.spinner is not None:
                    out_facing_numbers.append((current_board.spinner.get_out_facing_number(), Direction.SOUTH))
            if len(current_board.east) != 0:
                out_facing_numbers.append((current_board.east[-1].get_out_facing_number(), Direction.EAST))
            elif current_board.spinner is not None:
                out_facing_numbers.append((current_board.spinner.get_out_facing_number(), Direction.EAST))
            if len(current_board.west) != 0:
                out_facing_numbers.append((current_board.west[-1].get_out_facing_number(), Direction.WEST))
            elif current_board.spinner is not None:
                out_facing_numbers.append((current_board.spinner.get_out_facing_number(), Direction.WEST))

            for num, direction in out_facing_numbers:
                for i in range(len(current_hand)):
                    curr_dom = current_hand[i]
                    if curr_dom.num_a == num or curr_dom.num_b == num:
                        options.append((i, direction))



        print("Rando's hand:")
        to_print_1 = "    "
        to_print_2 = "    "
        to_print_3 = "    "
        to_print_4 = "    "
        for i in range(len(current_hand)):
            to_print_1 += "-----    "
            to_print_2 += f"|{current_hand[i].num_a}|{current_hand[i].num_b}|    "
            to_print_3 += "-----    "
            to_print_4 += f"  {i + 1}"
            for _ in range(7 - len(str(i + 1))):
                to_print_4 += " "
        print(to_print_1 + "\n" + to_print_2 + "\n" + to_print_3 + "\n" + to_print_4)
        return options[random.randint(0, len(options) - 1)]


class ConsolePlayer(Game.Player):
    def take_turn(self, current_board: Board, current_hand: list, curr_player_num: int, players: list, scores: dict, pile_size: int):
        print(f"Player {curr_player_num + 1}")
        scores_string = ""
        for player in players:
            scores_string += f"{scores[player]} "
        print(f"Scores: {scores_string}")
        print("The board:")
        print(str(current_board))
        print(f"Pile size: {pile_size}")
        print("Your hand:")
        to_print_1 = "    "
        to_print_2 = "    "
        to_print_3 = "    "
        to_print_4 = "    "
        for i in range(len(current_hand)):
            to_print_1 += "-----    "
            to_print_2 += f"|{current_hand[i].num_a}|{current_hand[i].num_b}|    "
            to_print_3 += "-----    "
            to_print_4 += f"  {i + 1}"
            for _ in range(7 - len(str(i + 1))):
                to_print_4 += " "
        print(to_print_1 + "\n" + to_print_2 + "\n" + to_print_3 + "\n" + to_print_4)
        while True:
            try:
                action = int(input("Choose domino number, or 0 to draw another: "))
                if 0 <= action <= len(current_hand):
                    break
            except:
                pass
            print("Bad input")

        if action is 0:
            return -1, None
        else:
            while True:
                try:
                    direction = int(input("Choose a direction (N/E/S/W = 1/2/3/4): "))
                    if 1 <= direction <= len(Direction):
                        break
                except:
                    pass
                print("Bad input")
            return action - 1, Direction(direction - 1)


if __name__ == '__main__':
    # player_1 = ConsolePlayer()
    # player_2 = ConsolePlayer()
    game = Game(max_num=6, score_to_win=200, players=[RandomPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()])
    game.play_match()
