import random
import sys
import time
import qrcode
from functools import total_ordering
from rich import print
from rich.console import Console
from pyfiglet import Figlet


@total_ordering
class Card:
    suits = ["♠", "♣", "♥", "♦"]
    ranks = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    card_offset = 6
    max_amount = 36

    def __init__(self, suit: str, rank: str) -> None:
        """Creates a card with a suit and value."""
        self.suit = suit
        self.raw_rank = rank

    def __str__(self) -> str:
        return f"{self.raw_rank}{self.suit}"

    def rank_str(self) -> str:
        """Returns real rank."""
        return f"{self.raw_rank}"

    def color(self) -> str:
        """Returns the color of a card based on its suit."""
        return "red" if self.suit in ["♥", "♦"] else "black"

    @property
    def rank(self) -> int:
        """Returns the rank as a numerical value (for comparison)."""
        return Card.ranks.index(self.raw_rank) + Card.card_offset

    def __eq__(self, other: object) -> bool:
        return self.rank == other.rank if isinstance(other, Card) else NotImplemented

    def __lt__(self, other: object) -> bool:
        return self.rank < other.rank if isinstance(other, Card) else NotImplemented


class Deck:
    def __init__(self) -> None:
        """Creates and shuffles a deck."""
        initial_deck = [Card(suit, rank) for suit in Card.suits for rank in Card.ranks]
        random.shuffle(initial_deck)
        self.cards = initial_deck

    def __str__(self) -> str:
        return " ".join(map(str, self.cards))

    def __len__(self) -> int:
        return len(self.cards)

    def draw(self) -> Card:
        """Take the top card from the deck."""
        return self.cards.pop()

    def put_back(self, card: Card) -> None:
        """Puts a card to the bottom of the deck."""
        self.cards.insert(0, card)


class Player:
    super_prize_price = 10000

    def __init__(self) -> None:
        """Initializes the player's numeric values."""
        self.score = 100
        self._initial_bet = 0
        self.prize = 0

    @property
    def initial_bet(self) -> int:
        return self._initial_bet

    @initial_bet.setter
    def initial_bet(self, value: int | str) -> None:
        if value == "super prize" and self.score >= Player.super_prize_price:
            self.get_super_prize()
        elif value == "super prize" and self.score < Player.super_prize_price:
            raise ValueError("Not enough points for the SUPER PRIZE")

        try:
            value = int(value)
        except ValueError:
            raise ValueError("BET must be an integer")
        if value <= 0:
            raise ValueError("BET must be positive")
        if value > self.score:
            raise ValueError("BET exceeds your current score")

        self._initial_bet = value

    def get_initial_bet(self) -> None:
        """Requests an initial bet from the player with the option to choose a super prize."""
        ad_super_prize = [
            "       ♠️ ────────────────────────♥️",
            "🌸/)_/) │[bold]If you want this[/bold]         │",
            (
                "( ̳• · ̳•)│[bold cyan]SPECIAL[/bold cyan] [bold blue]SUPER[/bold blue] "
                "[bold violet]SECRET[/bold violet] [bold red]GIFT[/bold red]│"
            ),
            " />🎁<\\ │[bold]for [underline]10.000[/underline] points[/bold]        │",
            "        │[bold]just text [underline]'SUPER PRIZE'[/underline][/bold]  │",
            "       ♦️ ────────────────────────♣️",
            "",
            "",
        ]

        while True:
            animate(ad_super_prize, delay=0, own_style=True)
            print(f"[bold]SCORE: {self.score}, BET:[/bold] ", end="")
            try:
                self.initial_bet = get_user_input("")
                self.score -= self.initial_bet
                break
            except ValueError as e:
                Console().clear()
                print(f"[red]{e}[/red]")

    def win(self, round_number: int) -> None:
        """Sets the win depending on the round."""
        jackpot = 10
        if round_number == 4:
            self.prize = self.initial_bet * jackpot
        else:
            self.prize = self.initial_bet * (int(round_number) + 1)

    def lose(self) -> None:
        """Resets current winnings."""
        self.prize = 0

    def status(self) -> str:
        """Returns a string with the player's numeric values."""
        return f"[[underline]SCORE: {self.score}, PRIZE: {self.prize}[/underline]]"

    def cash_out(self) -> None:
        """Changes the player's numerical values when cashing out."""
        self.score += self.prize
        self.prize = 0

    def get_super_prize(self) -> None:
        """Displays the super prize and terminates the program."""
        Console().clear()
        qr = qrcode.QRCode(border=1)
        qr.add_data("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        qr.make(fit=True)
        qr.print_ascii(invert=True)

        time.sleep(0.5)
        animate(text_to_figlet("TY  FOR  PLAYING").splitlines(), color="red", delay=0.2)
        sys.exit()


# ===🎮GAME LOGIC===
def is_card_valid(
    secret_card: Card, round_number: int, visible_cards: list[Card]
) -> bool:
    """Rejects cards equal in rank to the previous ones (only on the 2nd and 3rd rounds)."""
    if round_number == 2 and secret_card.rank == visible_cards[0].rank:
        return False
    if round_number == 3 and secret_card.rank in [
        visible_cards[0].rank,
        visible_cards[1].rank,
    ]:
        return False
    return True


def evaluate_answer(
    round_number: int, secret_card: Card, user: str, visible_cards: list[Card]
) -> bool:
    """Checks if the player gave the correct answer based on the round."""
    match round_number:
        case 1:
            return is_correct_color(secret_card, user)
        case 2:
            return is_correct_compare(secret_card, user, visible_cards)
        case 3:
            return is_correct_range(secret_card, user, visible_cards)
        case 4:
            return is_correct_suit(secret_card, user)


def is_correct_color(secret_card: Card, user: str) -> bool:
    """Returns the result of guessing the color of the card."""
    return secret_card.color() == user


def is_correct_compare(secret_card: Card, user: str, visible_cards: list[Card]) -> bool:
    """Returns the result of guessing 'more/less'."""
    if user == "more":
        return secret_card > visible_cards[0]
    if user == "less":
        return secret_card < visible_cards[0]
    return False


def is_correct_range(secret_card: Card, user: str, visible_cards: list[Card]) -> bool:
    """Returns the result of guessing 'in/out'."""
    low, high = sorted([visible_cards[0], visible_cards[1]])
    if user == "in":
        return low < secret_card < high
    if user == "out":
        return secret_card < low or secret_card > high
    return False


def is_correct_suit(secret_card: Card, user: str) -> bool:
    """Returns the result of guessing the suit of the card."""
    suit_aliases = {
        "1": "♠",
        "spades": "♠",
        "2": "♣",
        "clubs": "♣",
        "3": "♥",
        "hearts": "♥",
        "4": "♦",
        "diamonds": "♦",
    }
    user_suit = suit_aliases[user]
    return secret_card.suit == user_suit


# ===🖼️UI===
def render_card(card: Card) -> list[str]:
    """Returns ASKII art of one card."""
    suit_painted = f"[{card.color()}]{card.suit}[/{card.color()}]"
    return [
        "┌─────────┐",
        f"│[bold black]{card.rank_str():<2}[/bold black]       │",
        f"│{suit_painted}        │",
        "│         │",
        f"│    [bold]{suit_painted}[/bold]    │",
        "│         │",
        f"│        {suit_painted}│",
        f"│       [bold black]{card.rank_str():>2}[/bold black]│",
        "└─────────┘",
    ]


def render_hidden_card() -> list[str]:
    """Returns ASKII art of the hidden card."""
    return [
        "┌─────────┐",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "│░░░░[bold]?[/bold]░░░░│",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "└─────────┘",
    ]


def combine_cards(card_lines: list[list[str]]) -> list[str]:
    """Returns a combination of ASKII art of various cards."""
    card_height = 9
    card_distance_between = 3
    combined = ["" for _ in range(card_height)]
    for i in range(card_height):
        for card in card_lines:
            combined[i] += card[i] + " " * card_distance_between
    return combined


def display_cards(cards: list[Card], round_end: bool = False) -> list[str]:
    """Returns a combination of ASKII arts of various cards, ready for output to the terminal."""
    card_lines = [render_card(card) for card in cards]

    if not round_end:
        card_lines.append(render_hidden_card())

    return combine_cards(card_lines)


def ask_question(round_number: int) -> str:
    """Returns ASKII art question depending on the round."""
    questions = ["RED OR BLACK ? ", "MORE OR LESS ? ", "IN OR OUT ? ", "SUIT ? "]
    return text_to_figlet(questions[round_number - 1])


# ===🛠️UTILITY===
def is_valid_input(user: str, round_number: int = 0, action: str = "") -> bool:
    """Performs validation of user input in various situations."""
    if action == "again":
        return user in ["yes", "no"]
    elif action == "away/continue":
        return user in ["away", "continue", "1", "2"]

    valid_inputs = {
        1: ["red", "black"],
        2: ["more", "less"],
        3: ["in", "out"],
        4: ["1", "2", "3", "4", "spades", "clubs", "hearts", "diamonds"],
    }
    return user in valid_inputs.get(round_number, [])


def text_to_figlet(text: str) -> str:
    """Returns ASKII art text as a multi-line string."""
    fig = Figlet(font="small")
    return fig.renderText(text)


# ===🧠GAME CONTROL (impure functions)===
def show_intro() -> None:
    """Outputs the game intro to the terminal."""
    start_colors = ["red", "green", "blue"]
    start_times = len(start_colors)
    line_time = 0.4
    pause_time = 0.5
    welcome_time = 1

    start_ascii = text_to_figlet("GAME  IS  STARTING")
    welcome_ascii = text_to_figlet("WELCOME!")

    for k in range(start_times):
        clr = start_colors[k]

        animate(start_ascii.splitlines(), color=clr, delay=line_time)
        Console().clear()

        if k != start_times - 1:
            time.sleep(pause_time)

    animate(welcome_ascii.splitlines(), delay=0)
    time.sleep(welcome_time)
    Console().clear()


def play_game_session(deck: Deck, player: Player, debug: bool = False) -> bool:
    """Plays one session of the game. Returns True on win, False on loss."""
    # table initialization
    visible_cards = []

    # launching the game cycle
    while len(visible_cards) < 4:
        # guessing the card
        secret_card = deck.draw()
        # determining the round number
        round_number = Card.max_amount - len(deck)

        # checking a map for 'border repeat'
        if is_card_valid(secret_card, round_number, visible_cards):
            # drawing a card
            Console().clear()
            animate(display_cards(visible_cards, round_end=False), own_style=True)

            # SHOWING HIDDEN MAP
            if debug:
                print(f"[DEBUG MODE]SECRET CARD: {secret_card}")

            # round question output
            animate(ask_question(round_number).splitlines(), color="green")
            # extra line for round 4
            if round_number == 4:
                print("[♠️  -1, ♣️  -2, ♥️  -3, ♦️  -4]")

            # checking the answer to the question
            while True:
                user = get_user_input()
                if is_valid_input(user, round_number):
                    break

            # win or lose processing
            if evaluate_answer(round_number, secret_card, user, visible_cards):
                # result - WIN
                # adding a card to the table
                visible_cards.append(secret_card)

                # drawing a card
                Console().clear()
                animate(display_cards(visible_cards, round_end=True), own_style=True)
                # output of the inscription WIN
                display_round_result("WIN")

                # calculation of winnings and display of information about points
                player.win(round_number)
                print(player.status())

                # interruption of the game cycle in case of victory in the 4th round
                if len(visible_cards) == 4:
                    player.cash_out()
                    return True

                # 'away or continue' processing
                print("AWAY[1] OR CONTINUE[2]?")
                while True:
                    user = get_user_input()
                    if is_valid_input(user, action="away/continue"):
                        break
                # processing 'away'
                if user == "away" or user == "1":
                    player.cash_out()
                    return True

            else:
                # result - LOSE
                visible_cards.append(secret_card)
                Console().clear()
                animate(display_cards(visible_cards, round_end=True), own_style=True)
                display_round_result("LOST")
                player.lose()
                print(player.status())

                # processing a player's total loss
                if player.score == 0:
                    animate(text_to_figlet("GL NEXT TIME").splitlines(), color="blue")
                    sys.exit()
                return False

        else:
            # return the incorrect card to the bottom of the deck
            deck.put_back(secret_card)


def animate(
    lines: list[str],
    color: str = "black",
    style: str = "bold",
    delay: float = 0.1,
    own_style: bool = False,
) -> None:
    """Displays ASKII art line by line depending on the specified parameters."""
    for line in lines:
        if own_style:
            print(line)
        else:
            print(f"[{style} {color}]{line}[/{style} {color}]")
        time.sleep(delay)


def display_round_result(result: str) -> None:
    """Displays ASKII art of the round result"""
    result_ascii = text_to_figlet(f"YOU {result}")
    animate(result_ascii.splitlines(), color="red")


def ask_to_continue(result: bool) -> bool:
    """Displays the ASKII art of the question 'away/continue'
    and returns the result of the user's answer."""
    if result:
        question = "CONTINUE ? "
    else:
        question = "TRY AGAIN ? "

    again_ascii = text_to_figlet(question)
    animate(again_ascii.splitlines(), color="blue")

    while True:
        user = get_user_input()
        if is_valid_input(user, action="again"):
            break

    if user == "yes":
        return True
    else:
        return False


def get_user_input(prompt: str = "> ") -> str:
    """Receives and normalizes user input."""
    try:
        return input(prompt).lower().strip()
    except KeyboardInterrupt:
        print("\n[red]Game interrupted.[/red]")
        sys.exit()


# ===🚀Game Entry Point===
def main() -> None:
    """The entry point to the game. Manages game loops"""
    show_intro()
    player = Player()

    while True:
        Console().clear()
        player.get_initial_bet()

        deck = Deck()
        round_result = play_game_session(deck, player, debug=False)

        if not ask_to_continue(round_result):
            break


if __name__ == "__main__":
    main()
