# FORTUNE FLIP
#### Video Demo:  <[URL HERE](https://www.youtube.com/watch?v=X9xDdAjixaA)>
---
Fortune Flip is a terminal-based ASCII card game inspired by the classic Ride the Bus. Unlike the original drinking game, this version is all about betting, strategy, and luck.
Each session consists of four rounds, where every choice puts your intuition and fortune to the test.
The main goal is to earn points through betting and strategic decisions, eventually saving enough to unlock the **super prize**.

There is no final “winning state”: the game can be played endlessly, allowing you to keep growing your score and challenging yourself. This makes Fortune Flip both an engaging challenge and a perfect way to pass the time.

*The game was created as a final project for the CS50P course.*
## 🎮Game rules
In general, the game is quite simple, you should play it several times and the basic rules and mechanics become clear. The basic rules for reading are presented below.

At the start of the game, the player receives <ins>*100*</ins> points, which can be used for betting. Each game session begins with an initial bet and goes through four consecutive rounds:

1️⃣**RED OR BLACK** — guess the color of the hidden card (red or black);

2️⃣**MORE OR LESS** — guess whether the hidden card is higher or lower in rank than the card from the first round;

3️⃣**IN OR OUT** — guess whether the hidden card’s rank falls inside or outside the range defined by the first two cards;

4️⃣**SUIT** — guess the suit of the hidden card.

### ✨Features of the rules

🟣If the player makes a wrong guess in any round, the session is considered lost: the bet is forfeited. The player can start a new session with a new bet or exit the game.

🟣If the guess is correct, the round is considered won. The winnings are calculated as the initial bet multiplied by the round’s coefficient:

- **Round 1 → x2**

- **Round 2 → x3**

- **Round 3 → x4**

- **Round 4 → x10**

🟣After winning a round, the player can either cash out immediately or risk continuing to the next round.

🟣A fresh deck is generated at the start of every session.

🟣The deck contains 36 cards (from six to ace, a “Russian”/“Spanish” style deck).

🟣In the second and third rounds, strict inequality is applied: the hidden card cannot have the same rank as previously revealed cards.
## 🛠️Usage
The game runs entirely in the terminal.

To launch it locally:

1️⃣ Make sure **Python 3.11+** is installed;

2️⃣ Download the project files:

- project.py
- requirements.txt

3️⃣ Open a terminal and navigate to the project folder;

4️⃣ Install dependencies:
```bash
pip install -r requirements.txt
```
5️⃣Run the game:
```bash
python project.py
```
*After launching, the game interacts with the player through a text-based terminal interface.*

## ⚙️Technical features
The project consists of four files:

🟣**project.py**

Contains the entire main project code, which is structurally divided by comments into various blocks containing various functions. Each block is responsible for its own portion of the game logic:

- 🎮**GAME LOGIC** - functions responsible for implementing the game rules;

- 🖼️**UI** - includes functions responsible for drawing ASCII objects to create the user interface;

- 🛠️**UTILITY** - auxiliary functions, such as validating player input;

- 🧠**GAME CONTROL** - impure functions responsible for gameplay;

- 🚀**Game Entry Point** - main, responsible for managing game loops.

Also, project.py contains 3 classes that describe the main elements of the game - **CARD**, **DECK** and **PLAYER**.

🟣**test_project.py**

Contains all test functions run via **pytest**. This file is also divided into blocks corresponding to those in project.py.
While writing the tests, I was actively studying testing, so the tests I wrote are slightly beyond the knowledge gained in CS50P.

```bash
pytest test_project.py
```

🟣**requirements.txt**

Contains a list of packages used in the project:

- **pyfiglet** - for creating ASCII objects;

- **qrcode** - for creating a QR code as an ASCII object;

- **rich** - for terminal formatting.

🟣**README.md**

You are here!😜
```
 🌸/)_/)
 ( ̳• · ̳•)
 />🎁<\
 ```
