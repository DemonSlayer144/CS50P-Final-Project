import pytest
import re
from unittest.mock import MagicMock
import project
from project import (
    Card,
    Deck,
    Player,
    is_card_valid,
    evaluate_answer,
    is_correct_color,
    is_correct_compare,
    is_correct_range,
    is_correct_suit,
    render_card,
    render_hidden_card,
    combine_cards,
    display_cards,
    ask_question,
    is_valid_input,
    text_to_figlet
)

# ===Tests for Card class===
def test_card_str_repr():
    card = Card("♠", "A")
    assert str(card) == "A♠"

def test_card_rank_str():
    ace = Card("♠", "A")
    assert ace.rank_str() == "A"
    card = Card("♠", "6")
    assert card.rank_str() == "6"

@pytest.mark.parametrize("suit, expected_color", [
    ("♠", "black"),
    ("♣", "black"),
    ("♥", "red"),
    ("♦", "red"),
])
def test_card_color(suit, expected_color):
    card = Card(suit, "K")
    assert card.color() == expected_color

def test_card_rank_numeric_value():
    card = Card("♣", "6")
    assert card.rank == 6
    ace = Card("♣", "A")
    assert ace.rank == 14

def test_card_equality_and_comparison():
    c1 = Card("♣", "A")
    c2 = Card("♥", "A")
    c3 = Card("♦", "K")

    assert c1 == c2
    assert c3 < c1
    assert c1 > c3

def test_card_comparison_with_non_card():
    c1 = Card("♣", "6")
    assert (c1 == "not a card") is False
    with pytest.raises(TypeError):
        _ = c1 < "string"

# ===Tests for Deck class===
def test_deck_init():
    deck = Deck()
    assert len(deck) == Card.max_amount
    assert all(isinstance(card, Card) for card in deck.cards)
    ordered_deck = [Card(suit, rank) for suit in Card.suits for rank in Card.ranks]
    assert deck.cards != ordered_deck

def test_deck_str_repr():
    deck = Deck()
    deck.cards = [Card("♣", "A"), Card("♦", "K")]
    assert str(deck) == "A♣ K♦"

def test_deck_len():
    deck = Deck()
    assert len(deck) == 36
    deck.draw()
    assert len(deck) == 35

def test_deck_draw():
    deck = Deck()
    top_card_before = deck.cards[-1]
    drawn_card = deck.draw()
    assert drawn_card == top_card_before
    assert len(deck) == Card.max_amount - 1

    #assert drawn_card not in deck.cards
    assert all(drawn_card is not card for card in deck.cards)

def test_deck_put_back():
    deck = Deck()
    card = deck.draw()
    bottom_card_before = deck.cards[0]
    deck.put_back(card)
    assert deck.cards[0] == card
    assert bottom_card_before is not card
    assert len(deck) == Card.max_amount

# ===Tests for Player class===
def test_player_initial_bet():
    p = Player()
    p.score = 100
    with pytest.raises(ValueError, match="BET must be an integer"):
        p.initial_bet = "cat"
        p.initial_bet = 1.1
        p.initial_bet = ""
    with pytest.raises(ValueError, match="BET must be positive"):
        p.initial_bet = 0
        p.initial_bet = -1
    with pytest.raises(ValueError, match="BET exceeds your current score"):
        p.initial_bet = 101

    assert p.score == 100

def test_player_get_initial_bet(monkeypatch):
    p = Player()
    p.score = 100

    monkeypatch.setattr("builtins.input", lambda _: "40")

    p.get_initial_bet()

    assert p.initial_bet == 40
    assert p.score == 60

def test_player_call_super_prize(monkeypatch):
    p = Player()
    mock_func = MagicMock(side_effect=SystemExit)
    monkeypatch.setattr(p, "get_super_prize", mock_func)
    p.score = 100

    with pytest.raises(ValueError, match="Not enough points for the SUPER PRIZE"):
        p.initial_bet = "super prize"
        p.initial_bet = "Super Prize"
        p.initial_bet = "super prize".upper()

    p.score = Player.super_prize_price
    with pytest.raises(SystemExit):
        p.initial_bet = "super prize"
    mock_func.assert_called_once()

def test_player_get_super_prize(monkeypatch):
    p = Player()
    p.score = Player.super_prize_price

    called = {}

    def fake_exit():
        called["exit"] = True
        raise SystemExit

    monkeypatch.setattr("project.sys.exit", fake_exit)

    with pytest.raises(SystemExit):
        p.initial_bet = "super prize"

    assert called.get("exit", False)

@pytest.mark.parametrize("round_number, expected_prize", [
    (1, 20),
    (2, 30),
    (3, 40),
    (4, 100),
])
def test_player_win(round_number, expected_prize):
    p = Player()
    p.initial_bet = 10
    initial_score = p.score
    p.win(round_number)
    assert p.prize == expected_prize
    assert p.score == initial_score

def test_player_lose():
    p = Player()
    p.initial_bet = 10
    p.win(1)
    p.lose()
    assert p.prize == 0

def test_player_status():
    p = Player()
    plain = re.sub(r"\[/?\w+\]", "", p.status())
    assert f"SCORE: {p.score}" in plain
    assert f"PRIZE: {p.prize}" in plain

def test_player_cash_out():
    p = Player()
    p.initial_bet = 10
    p.win(1)
    p.cash_out()
    assert p.prize == 0
    assert p. score == 120

# ===Tests for 🎮Game Logic functions===
@pytest.mark.parametrize("secret_card, round_number, visible_cards, expected", [
    (Card("♠", "10"), 1, [], True),
    (Card("♠", "10"), 4, [Card("♦", "10"), Card("♦", "J"), Card("♦", "Q")], True),
    (Card("♠", "10"), 2, [Card("♦", "10")], False),
    (Card("♠", "10"), 3, [Card("♦", "6"), Card("♦", "10")], False),
    (Card("♠", "6"), 3, [Card("♦", "6"), Card("♦", "10")], False),
])
def test_is_card_valid(secret_card, round_number, visible_cards, expected):
    assert is_card_valid(secret_card, round_number, visible_cards) == expected

@pytest.mark.parametrize("r_number, sec_card, user, vis_cards, target_func", [
    (1, Card("♦", "6"), "red", [], is_correct_color),
    (2, Card("♦", "6"), "more", [Card("♦", "7")], is_correct_compare),
    (3, Card("♦", "6"), "in", [Card("♦", "8"), Card("♦", "9")], is_correct_range),
    (4, Card("♦", "6"), "1", [Card("♦", "10"), Card("♦", "J"), Card("♦", "Q")], is_correct_suit),
])
def test_evaluate_answer(monkeypatch, r_number, sec_card, user, vis_cards, target_func):
    mock_func = MagicMock(return_value="MOCK")
    monkeypatch.setattr(project, target_func.__name__, mock_func)

    result = evaluate_answer(r_number, sec_card, user, vis_cards)

    assert result == "MOCK"
    mock_func.assert_called_once()
    if r_number in (1, 4):
        mock_func.assert_called_with(sec_card, user)
    else:
        mock_func.assert_called_with(sec_card, user, vis_cards)

@pytest.mark.parametrize("card, user", [
    (Card("♦", "6"), "red"),
    (Card("♥", "6"), "red"),
    (Card("♠", "6"), "black"),
    (Card("♣", "6"), "black"),
])
def test_is_correct_color(card, user):
    assert is_correct_color(card, user)

def test_is_correct_compare():
    vis_cards = [Card("♦", "8")]

    assert is_correct_compare(Card("♦", "9"), "more", vis_cards)
    assert is_correct_compare(Card("♦", "7"), "more", vis_cards) == False

    assert is_correct_compare(Card("♦", "7"), "less", vis_cards)
    assert is_correct_compare(Card("♦", "9"), "less", vis_cards) == False

    assert is_correct_compare(Card("♦", "7"), "Cat", vis_cards) == False

@pytest.mark.parametrize("vis_cards", [
    ([Card("♦", "10"), Card("♦", "Q")]),
    ([Card("♦", "Q"), Card("♦", "10")])
])
def test_is_correct_range(vis_cards):
    assert is_correct_range(Card("♦", "J"), "in", vis_cards)
    assert is_correct_range(Card("♦", "9"), "in", vis_cards) == False
    assert is_correct_range(Card("♦", "K"), "in", vis_cards) == False

    assert is_correct_range(Card("♦", "9"), "out", vis_cards)
    assert is_correct_range(Card("♦", "K"), "out", vis_cards)
    assert is_correct_range(Card("♦", "J"), "out", vis_cards) == False

    assert is_correct_range(Card("♦", "J"), "Cat", vis_cards) == False

def test_is_correct_suit():
    assert is_correct_suit(Card("♠", "6"), "1")
    assert is_correct_suit(Card("♠", "6"), "spades")

    assert is_correct_suit(Card("♣", "6"), "2")
    assert is_correct_suit(Card("♣", "6"), "clubs")

    assert is_correct_suit(Card("♥", "6"), "3")
    assert is_correct_suit(Card("♥", "6"), "hearts")

    assert is_correct_suit(Card("♦", "6"), "4")
    assert is_correct_suit(Card("♦", "6"), "diamonds")

    assert is_correct_suit(Card("♦", "6"), "1") == False
    assert is_correct_suit(Card("♥", "6"), "2") == False
    assert is_correct_suit(Card("♣", "6"), "3") == False
    assert is_correct_suit(Card("♠", "6"), "4") == False

    assert is_correct_suit(Card("♦", "6"), "diamonds")

    with pytest.raises(KeyError):
        assert is_correct_suit(Card("♦", "6"), "Cat")

# ===Tests for 🖼️UI functions===
def test_render_card():
    card = Card("♦", "6")
    lines = render_card(card)

    assert isinstance(lines, list)

    assert len(lines) == 9

    assert any("♦" in line for line in lines)
    assert any("6" in line for line in lines)

def test_render_hidden_card():
    lines = render_hidden_card()

    assert isinstance(lines, list)

    assert len(lines) == 9

    assert any("?" in line for line in lines)

def test_combine_cards():
    card1 = render_card(Card("♦", "6"))
    card2 = render_card(Card("♦", "7"))

    combined = combine_cards([card1, card2])

    assert len(combined) == len(card1)

    assert len(combined[0]) > len(card1[0])

def test_display_cards():
    # with hidden card
    card1 = Card("♦", "6")
    card2 = Card("♦", "7")
    result = display_cards([card1, card2], False)

    assert isinstance(result, list)
    assert len(result) == 9
    assert any("?" in line for line in result)

    card1 = render_card(card1)
    card2 = render_card(card2)

    assert len(result[0]) > len(combine_cards([card1, card2])[0])

    # without hidden card
    card1 = Card("♦", "6")
    card2 = Card("♦", "7")
    result = display_cards([card1, card2], True)

    assert isinstance(result, list)
    assert len(result) == 9
    assert any("?" not in line for line in result)

    card1 = render_card(card1)
    card2 = render_card(card2)

    assert len(result[0]) == len(combine_cards([card1, card2])[0])

def test_ask_question(monkeypatch):
    monkeypatch.setattr("project.text_to_figlet", MagicMock(return_value="MOCK"))

    result = ask_question(1)

    assert result == "MOCK"

    project.text_to_figlet.assert_called_with("RED OR BLACK ? ")

# ===Tests for 🛠️UTILITY functions===
def test_is_valid_input():
    assert is_valid_input("yes", 1, "again")
    assert is_valid_input("no", 1, "again")
    assert is_valid_input("Cat", 1, "again") == False

    assert is_valid_input("away", 1, "away/continue")
    assert is_valid_input("continue", 1, "away/continue")
    assert is_valid_input("1", 1, "away/continue")
    assert is_valid_input("2", 1, "away/continue")
    assert is_valid_input("Cat", 1, "away/continue") == False

    assert is_valid_input("red", 1, "")
    assert is_valid_input("black", 1, "")
    assert is_valid_input("Cat", 1, "") == False
    assert is_valid_input("red", 5, "") == False

def test_text_to_figlet():
    result = text_to_figlet("A")

    assert isinstance(result, str)
    assert any(ch in result for ch in "_|/\\")
    assert "\n" in result
    assert "A" not in result



