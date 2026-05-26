# -*- coding: utf-8 -*-
"""
Tic-Tac-Toe  —  Python / Tkinter
==================================
A complete, two-mode Tic-Tac-Toe game with a dark-themed graphical window.
No extra packages needed — just run:

    python tic_tac_toe.py

────────────────────────────────────────────────────────────────
WHY TKINTER?
────────────────────────────────────────────────────────────────
Python comes with a built-in GUI (Graphical User Interface) library called
Tkinter.  Think of Tkinter as a toolbox that lets you create real windows,
buttons, text boxes, and drawing canvases — things you can see and click on,
not just text in a terminal.

Because it's built into Python, you don't need to install anything extra.
It works on Windows, Mac, and Linux.

────────────────────────────────────────────────────────────────
CONCEPTS YOU WILL LEARN IN THIS FILE
────────────────────────────────────────────────────────────────
  • Constants          — values that are set once and never change
  • Lists              — ordered collections, e.g. the 9-square board
  • Dictionaries       — named collections, e.g. the game state
  • Functions (def)    — reusable blocks of code with inputs and outputs
  • Classes            — blueprints that bundle data and behaviour together
  • Methods (self)     — functions that belong to a class
  • Loops & conditions — for / if / elif / else
  • Events             — code that runs when the user clicks or moves the mouse
  • AI logic           — simple rules that let the computer make smart moves
  • Closures           — functions defined inside other functions
"""

# ──────────────────────────────────────────────────────────────
# IMPORTS  —  bringing in tools we didn't write ourselves
# ──────────────────────────────────────────────────────────────
#
# "import" means: go find this library and make it available here.
# We give libraries a short nickname with "as" to save typing later.
#
import tkinter as tk          # the main GUI toolkit  (tk.Frame, tk.Button, …)
from tkinter import font as tkfont  # the font sub-module for custom text sizes
import random                 # lets us pick random items from a list (for AI corners)


# ══════════════════════════════════════════════════════════════
#  SECTION 1 — CONSTANTS
#
#  A constant is a variable whose value we agree never to change
#  after we set it the first time.  Python has no enforced
#  constant keyword, but writing names IN_ALL_CAPS is the
#  universal convention that tells other programmers "don't
#  touch this".
# ══════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────
# The 8 ways to win Tic-Tac-Toe
# ──────────────────────────────────────────────────────────────
#
# We number the 9 squares like this (a flat list, not a grid):
#
#   0 | 1 | 2
#   ---------
#   3 | 4 | 5
#   ---------
#   6 | 7 | 8
#
# There are exactly 8 winning lines:
#   3 rows  →  [0,1,2]  [3,4,5]  [6,7,8]
#   3 cols  →  [0,3,6]  [1,4,7]  [2,5,8]
#   2 diags →  [0,4,8]  [2,4,6]
#
# Storing them here as a list of lists means we can loop over
# all 8 at once instead of writing 8 separate if-statements.
#
WIN_COMBOS = [
    [0, 1, 2],   # top row
    [3, 4, 5],   # middle row
    [6, 7, 8],   # bottom row
    [0, 3, 6],   # left column
    [1, 4, 7],   # middle column
    [2, 5, 8],   # right column
    [0, 4, 8],   # diagonal: top-left → bottom-right
    [2, 4, 6],   # diagonal: top-right → bottom-left
]

# ──────────────────────────────────────────────────────────────
# Colour palette  (hex colour codes, like in web / CSS)
# ──────────────────────────────────────────────────────────────
#
# WHY A DICTIONARY?
#   We could write the hex code "#f43f5e" everywhere we need red,
#   but if we later want to change the red shade we'd have to find
#   and update every single place.  Storing colours in one dict
#   means we change it in ONE place and the whole program updates.
#
# WHAT IS A HEX CODE?
#   "#RRGGBB" — two hex digits each for Red, Green, Blue.
#   #000000 = black  |  #ffffff = white  |  #f43f5e = rose-red
#
C = {
    "bg":      "#07071a",   # very dark navy — main window background
    "surface": "#11112b",   # slightly lighter navy — card backgrounds
    "surf2":   "#1a1a3a",   # even lighter — input boxes and cell backgrounds
    "surf3":   "#242450",   # hover state for cells and buttons
    "accent":  "#7c3aed",   # vivid purple — active highlights and borders
    "x":       "#f43f5e",   # rose-red — colour of the X symbol
    "o":       "#22d3ee",   # cyan — colour of the O symbol
    "win":     "#f59e0b",   # amber/gold — colour of winning cells
    "text":    "#f1f5f9",   # near-white — primary readable text
    "muted":   "#94a3b8",   # grey-blue — secondary / placeholder text
    "border":  "#2d2d5a",   # subtle border between cards
}

# ──────────────────────────────────────────────────────────────
# Board pixel measurements
# ──────────────────────────────────────────────────────────────
#
# The board is drawn on a Tkinter Canvas — a blank rectangle we
# can paint shapes on.  All positions are in pixels.
#
# Total canvas size  =  3 cells  +  2 gaps  +  2 edge insets
#                    =  3×108   +  2×8     +  2×14
#                    =  324     +  16      +  28
#                    =  368 pixels wide and tall
#
CELL_PX  = 108   # each cell is a 108×108 pixel square
GAP_PX   = 8     # 8-pixel gap between adjacent cells (the "grid lines")
INSET_PX = 14    # blank space between the canvas edge and the first cell
SYM_PAD  = 20    # how many pixels to shrink inward when drawing X or O


# ══════════════════════════════════════════════════════════════
#  SECTION 2 — GAME STATE
#
#  The "state" is a single dictionary that stores everything
#  the game needs to remember: who's playing, what's on the
#  board, whose turn it is, and so on.
#
#  WHY A FUNCTION INSTEAD OF A PLAIN VARIABLE?
#    If we stored the state in a global variable and then wrote
#    state = {} to reset it, Python would just rebind the name —
#    any old references would still point to the original dict.
#    Calling new_state() always creates a brand-new dictionary,
#    so "reset" is always clean and predictable.
# ══════════════════════════════════════════════════════════════

def new_state():
    """
    Return a fresh dictionary representing a brand-new game.
    Call this at startup, and again whenever the player clicks
    'New Game Setup' to return to the beginning.
    """
    return {
        # "single" = player vs computer  |  "two" = two human players
        "mode": None,

        # A list with two player dictionaries — index 0 is Player 1,
        # index 1 is Player 2 (or Computer in single-player mode).
        "players": [
            {"name": "Player #1", "symbol": "X"},
            {"name": "Player #2", "symbol": "O"},
        ],

        # The 9 squares of the board.
        #   None  →  the square is empty
        #   "X"   →  X has been placed there
        #   "O"   →  O has been placed there
        #
        # [None] * 9 is a shortcut for writing [None, None, None, …] nine times.
        "board": [None] * 9,

        # Index (0 or 1) of the player whose turn it currently is.
        "current": 0,

        # How many times each player has won.  wins[0] = Player 1's count.
        "wins": [0, 0],

        # Total number of completed games (wins + draws combined).
        "games": 0,

        # Becomes True the moment the game ends (win or draw).
        # We use this to stop further clicks on the board.
        "over": False,

        # Which player index (0 or 1) goes first in this round.
        # This alternates each time "Play Again" is pressed, so
        # it's fair: if you went second last game, you go first next.
        "starter": 0,

        # When someone wins, we store the 3 winning square indices here
        # so we can highlight them in gold on the board.
        "win_cells": [],

        # True while the computer is "thinking" (during its 650ms delay).
        # We block human clicks during this time so moves don't overlap.
        "thinking": False,
    }


# ══════════════════════════════════════════════════════════════
#  SECTION 3 — WIN AND DRAW DETECTION
#
#  These are "pure functions" — they take inputs and return a
#  result WITHOUT changing anything else in the program.
#  Pure functions are easy to test: give them the same input
#  and they always give the same output.
# ══════════════════════════════════════════════════════════════

def find_winner(board):
    """
    Scan all 8 possible winning lines.  If any line has the same
    non-empty symbol in all three squares, return those 3 indices
    so we can highlight them.  If nobody has won yet, return None.

    HOW IT WORKS:
      The "for a, b, c in WIN_COMBOS" loop unpacks each inner list
      automatically.  For [0, 1, 2] the variables become a=0, b=1, c=2.

      board[a] and board[a] == board[b] == board[c]
        • "board[a]" alone is True when the square is "X" or "O",
          and False when it's None (empty).  We need this first check
          so we don't accidentally say three empty squares are a match.
        • "board[a] == board[b] == board[c]" checks that all three
          squares have the same symbol.  Python lets you chain
          comparisons like this — it's a neat shortcut.

    WHY RETURN EARLY?
      As soon as we find a winner we return immediately.  There's no
      point checking the other 7 lines once we already have the answer.
    """
    for a, b, c in WIN_COMBOS:
        if board[a] and board[a] == board[b] == board[c]:
            return [a, b, c]   # ← found a winner; stop and return

    return None   # ← checked all 8 lines, no winner yet


def is_draw(board):
    """
    Return True when every square is filled (and find_winner already
    returned None, meaning nobody won).

    HOW IT WORKS:
      Python's built-in all() function returns True only if every
      item in the list is "truthy" (not None, not 0, not "").
      Since empty squares are None and played squares are "X" or "O",
      all(board) is True exactly when there are no empty squares left.
    """
    return all(board)


# ══════════════════════════════════════════════════════════════
#  SECTION 4 — COMPUTER AI
#
#  This is the "brain" of the single-player mode.  Two questions:
#
#  Q: Is this a standard approach?
#  A: YES.  This style of AI is called a "rule-based" or "heuristic"
#     approach.  A heuristic is a practical rule of thumb that works
#     well in most situations, even if it's not guaranteed to be
#     mathematically perfect in every case.
#
#     The mathematically PERFECT strategy for Tic-Tac-Toe is called
#     "Minimax" — an algorithm that looks ahead at every possible
#     future move and picks the one that's best regardless of what
#     the opponent does.  A perfect Minimax player NEVER loses.
#
#     Our 5-rule heuristic is much simpler to read and understand,
#     and it still plays very strong Tic-Tac-Toe.  It will never miss
#     a winning move or forget to block an obvious threat.
# ══════════════════════════════════════════════════════════════

def find_winning_square(board, symbol):
    """
    Look for a square that, if filled with `symbol`, would complete
    a line of three.  This is used for two purposes:
      • Called with the computer's symbol → finds a move to WIN.
      • Called with the human's symbol    → finds a move to BLOCK.

    HOW IT WORKS:
      For each of the 8 winning lines we build a small list called
      `row` with the current contents of those 3 squares.

      row.count(symbol) == 2  →  two of the three squares already
                                  have our symbol
      row.count(None)   == 1  →  exactly one square is still empty

      When both conditions are true, filling that empty square
      completes the line.

      row.index(None) gives us the position of the empty slot inside
      `row` (0, 1, or 2).  We use that to look up the real board
      index: [a, b, c][row.index(None)].

    Returns -1 if no such square exists (the sentinel value meaning
    "nothing found").
    """
    for a, b, c in WIN_COMBOS:
        row = [board[a], board[b], board[c]]
        if row.count(symbol) == 2 and row.count(None) == 1:
            return [a, b, c][row.index(None)]
    return -1   # no winning/blocking square found


def best_move(board, computer_sym, human_sym):
    """
    Choose the best available square for the computer using five
    priority rules, applied in order.  The FIRST rule that finds
    a valid move wins — lower-priority rules are never reached.

    ─────────────────────────────────────────────────────────
    WHY THESE 5 RULES, IN THIS ORDER?
    ─────────────────────────────────────────────────────────

    RULE 1 — Win immediately
      If the computer can place its symbol and win right now,
      it must do so.  There is never a reason to delay a win.
      This is checked FIRST because winning trumps everything else.

    RULE 2 — Block the opponent's win
      If the human has two symbols in a line with one empty square,
      they will win on their NEXT turn.  The computer MUST block
      that square or it will lose.  This comes second because
      blocking is only relevant when we can't win ourselves.

    RULE 3 — Take the center (square 4)
      The center square belongs to 4 winning lines:
        • the middle row
        • the middle column
        • both diagonals
      No other square belongs to that many lines, so the center
      gives the most future options.  Statistical analysis of
      Tic-Tac-Toe shows that taking the center early is the
      strongest opening after checking for immediate wins/blocks.

    RULE 4 — Take a corner (squares 0, 2, 6, 8)
      Each corner belongs to 3 winning lines (a row, a column,
      and one diagonal).  Corners are the next-best squares after
      the center.  We pick a random corner so the computer doesn't
      always play the same game — this makes it feel less robotic.

    RULE 5 — Take any remaining free square
      If the center and all corners are taken, only edge squares
      remain (1, 3, 5, 7).  We pick one at random.

    ─────────────────────────────────────────────────────────
    COULD WE MAKE IT SMARTER?
    ─────────────────────────────────────────────────────────
    Yes!  The "Minimax" algorithm considers all possible future
    game trees and picks the provably optimal move every time.
    With Minimax the computer can NEVER be beaten — the worst
    result against a perfect opponent would be a draw.

    Our 5-rule version is simpler to read and almost as good.
    It won't miss a win or a block, which are the moves that
    matter most in real games.
    """

    # ── Rule 1: Win if we can ──────────────────────────────
    move = find_winning_square(board, computer_sym)
    if move != -1:
        return move   # found a winning square — take it immediately

    # ── Rule 2: Block the human's winning move ─────────────
    # We reuse find_winning_square but pass the HUMAN's symbol.
    # If the human is one move away from winning, that square
    # is exactly where the computer must play.
    move = find_winning_square(board, human_sym)
    if move != -1:
        return move   # block the threat

    # ── Rule 3: Take the center ────────────────────────────
    # Square index 4 is the center of the 3×3 grid.
    # "is None" checks that it hasn't been played yet.
    if board[4] is None:
        return 4

    # ── Rule 4: Take a random free corner ──────────────────
    # List comprehension: build a list of corner indices that
    # are still empty.  [i for i in (...) if board[i] is None]
    # reads as "give me i, for each i in (0,2,6,8), but only
    # if that square is currently empty".
    free_corners = [i for i in (0, 2, 6, 8) if board[i] is None]
    if free_corners:
        return random.choice(free_corners)   # random so it varies each game

    # ── Rule 5: Any remaining free square ──────────────────
    # enumerate(board) gives pairs of (index, value) for each square.
    # We keep only indices where the value is still None.
    free_squares = [i for i, val in enumerate(board) if val is None]
    return random.choice(free_squares)


# ══════════════════════════════════════════════════════════════
#  SECTION 5 — THE APPLICATION CLASS
#
#  WHAT IS A CLASS?
#    A class is a blueprint.  It bundles together:
#      • Data    (variables that belong to the object)
#      • Behaviour (functions — called "methods" — that work on that data)
#
#    For example, a Car class might have data like colour and speed,
#    and methods like accelerate() and brake().
#
#  WHY USE A CLASS HERE?
#    Our game has many pieces of data (the canvas, all the labels,
#    the state dict, the current hover cell…) and many related
#    functions that read or change that data.  Without a class we'd
#    need to pass those values between every function as arguments.
#    A class keeps everything together under "self", which you can
#    think of as "the current instance of this game".
#
#  WHAT IS "self"?
#    Every method of a class gets "self" as its first argument
#    automatically.  It refers to the specific object you created.
#    self.canvas is "this game's canvas widget".
#    self.state  is "this game's state dictionary".
# ══════════════════════════════════════════════════════════════

class TicTacToe:
    """
    The main application object.  One instance of this class = one
    running game window.

    Screens managed by this class:
      1. Setup screen  — mode selection, player names, symbol choice
      2. Game screen   — the 3×3 board (left) + scoreboard (right)
      3. Result popup  — win or draw announcement with play-again button
    """

    # ──────────────────────────────────────────────────────
    # __init__  —  the CONSTRUCTOR
    # ──────────────────────────────────────────────────────
    #
    # Python calls __init__ automatically the moment you write:
    #   app = TicTacToe(root)
    #
    # Think of it as the "setup" step that runs once at the start.
    # Everything that should exist for the lifetime of the game
    # gets created here.
    #
    # The parameter "root: tk.Tk" is a type hint — it tells readers
    # that `root` should be a Tk window object.  Python doesn't
    # enforce this, but it's good documentation.
    #
    def __init__(self, root: tk.Tk):
        self.root  = root          # the main window; every widget lives inside it
        self.state = new_state()   # start with a clean game state

        # Track which cell the mouse is currently hovering over.
        # -1 means "not hovering over any cell right now".
        self._hovered_cell = -1

        # Configure the main window
        self.root.title("Tic-Tac-Toe")    # text in the window title bar
        self.root.configure(bg=C["bg"])    # set the window background colour
        self.root.resizable(False, False)  # lock the size (no drag-to-resize)

        # Build everything in order:
        self._build_fonts()          # create font objects we'll use everywhere
        self._build_setup_screen()   # create the setup widgets (hidden for now)
        self._build_game_screen()    # create the game widgets (hidden for now)
        self._show_setup_screen()    # show ONLY the setup screen to start

    # ──────────────────────────────────────────────────────
    # FONTS
    # ──────────────────────────────────────────────────────

    def _build_fonts(self):
        """
        Pre-create all font objects in one place and store them in a
        dictionary self.F.

        WHY PRE-CREATE FONTS?
          Creating a font object is slightly expensive.  If we wrote
          tkfont.Font(...) every time we created a label, we'd be
          creating hundreds of font objects.  Creating them once and
          reusing them is both faster and keeps all size decisions in
          one easy-to-find location.

        CLOSURES — a function inside a function:
          The inner function `f(size, weight)` is a shortcut so we
          don't have to type tkfont.Font(family="Segoe UI", …) eight
          times.  `f` "closes over" (remembers) the family name from
          the outer function even after the outer function has returned.
          This is called a closure.
        """
        # A small helper function — only visible inside _build_fonts.
        def f(size, weight="normal"):
            return tkfont.Font(family="Segoe UI", size=size, weight=weight)

        # Build the font dictionary.  Keys are descriptive names.
        self.F = {
            "title":   f(20, "bold"),   # screen headings ("Tic-Tac-Toe")
            "heading": f(12, "bold"),   # section headings
            "body":    f(10),           # normal body text
            "label":   f(8,  "bold"),   # small uppercase field labels
            "symbol":  f(32, "bold"),   # the ✕ and ○ in the score tiles
            "score":   f(26, "bold"),   # the large win-count number
            "button":  f(10, "bold"),   # button text
            "status":  f(11, "bold"),   # "Sid's Turn" status label
            "emoji":   f(34),           # 🏆 and 🤝 in the result popup
        }

    # ──────────────────────────────────────────────────────
    # SETUP SCREEN BUILDER
    # ──────────────────────────────────────────────────────

    def _build_setup_screen(self):
        """
        Create ALL setup widgets once and attach them to self.frm_setup.
        They are invisible until _show_setup_screen() is called.

        WHY BUILD ONCE AND HIDE/SHOW?
          We could destroy and recreate widgets every time the user
          navigates.  But creating widgets is slow and we'd have to
          re-bind all the events.  Instead we build everything once at
          startup and simply show or hide frames as needed.  Tkinter's
          pack_forget() removes a widget from view WITHOUT destroying it,
          and pack() makes it visible again.

        THE THREE STEPS:
          Step 1  frm_mode  — choose Single Player or Two Players
          Step 2  frm_p1    — enter Player 1's name and symbol
          Step 3  frm_p2    — enter Player 2's name (two-player only)

        Only one step is visible at a time.
        """
        # The outer frame fills the whole window during setup.
        self.frm_setup = tk.Frame(self.root, bg=C["bg"])

        # The "modal card" — a bordered box in the centre of the window.
        # highlightbackground + highlightthickness add a coloured border.
        card = tk.Frame(
            self.frm_setup,
            bg=C["surface"],
            highlightbackground=C["accent"],
            highlightthickness=1,
        )
        # ipadx / ipady add internal padding (inside the border).
        # padx / pady add external padding (outside the border).
        card.pack(padx=60, pady=50, ipadx=32, ipady=28)

        # Build each step inside the same card frame.
        self._build_mode_step(card)
        self._build_player1_step(card)
        self._build_player2_step(card)

    # ── Step 1: mode selection ────────────────────────────

    def _build_mode_step(self, parent):
        """
        Create the 'choose a mode' screen with two large clickable cards.
        Stored as self.frm_mode.
        """
        self.frm_mode = tk.Frame(parent, bg=C["surface"])

        # Title label — purely decorative text at the top.
        tk.Label(
            self.frm_mode,
            text="Tic-Tac-Toe",
            font=self.F["title"],
            fg=C["accent"],
            bg=C["surface"],
        ).pack(pady=(0, 4))

        # Subtitle / instruction text.
        tk.Label(
            self.frm_mode,
            text="Choose a game mode to get started",
            font=self.F["body"],
            fg=C["muted"],
            bg=C["surface"],
        ).pack(pady=(0, 20))

        # A horizontal row to hold the two mode cards side by side.
        btn_row = tk.Frame(self.frm_mode, bg=C["surface"])
        btn_row.pack()

        # LAMBDA FUNCTIONS:
        #   lambda: self._on_mode_chosen("single")
        #   creates a tiny anonymous function with no arguments that, when
        #   called, runs self._on_mode_chosen("single").  We need lambdas
        #   here because tk.Button's command= expects a function OBJECT
        #   (something to call later), not the result of calling one now.
        #   Writing command=self._on_mode_chosen("single") would call the
        #   function immediately during setup — not what we want.
        self._mode_card(
            btn_row, "🤖", "Single Player", "vs Computer",
            lambda: self._on_mode_chosen("single"),
        ).pack(side="left", padx=6)

        self._mode_card(
            btn_row, "👥", "Two Players", "vs a Friend",
            lambda: self._on_mode_chosen("two"),
        ).pack(side="left", padx=6)

    # ── Step 2: player 1 config ───────────────────────────

    def _build_player1_step(self, parent):
        """
        Create the name-entry and symbol-selection form for Player 1.
        Stored as self.frm_p1.

        The title text changes depending on the selected mode:
          Single player  → "Your Setup"
          Two players    → "Player 1 Setup"
        So we keep references to the labels (self.lbl_p1_title, etc.)
        so we can call .config(text=…) later to update them.
        """
        self.frm_p1 = tk.Frame(parent, bg=C["surface"])

        # We store the label references so we can update their text later.
        self.lbl_p1_title = tk.Label(
            self.frm_p1, text="Your Setup",
            font=self.F["title"], fg=C["accent"], bg=C["surface"],
        )
        self.lbl_p1_title.pack(pady=(0, 4))

        self.lbl_p1_sub = tk.Label(
            self.frm_p1, text="Set up your profile",
            font=self.F["body"], fg=C["muted"], bg=C["surface"],
        )
        self.lbl_p1_sub.pack(pady=(0, 16))

        # "YOUR NAME" field label (the small uppercase text above the box).
        tk.Label(
            self.frm_p1, text="YOUR NAME",
            font=self.F["label"], fg=C["muted"], bg=C["surface"],
        ).pack(anchor="w")   # anchor="w" aligns it to the left (West)

        # The text-entry widget.  _make_entry adds placeholder behaviour.
        self.entry_p1 = self._make_entry(self.frm_p1, placeholder="Player #1")
        self.entry_p1.pack(fill="x", pady=(4, 14))  # fill="x" stretches it horizontally

        # Symbol selection label.
        tk.Label(
            self.frm_p1, text="CHOOSE YOUR SYMBOL",
            font=self.F["label"], fg=C["muted"], bg=C["surface"],
        ).pack(anchor="w")

        # A row to hold the X card and O card side by side.
        sym_row = tk.Frame(self.frm_p1, bg=C["surface"])
        sym_row.pack(fill="x", pady=(4, 18))

        # tk.StringVar is a special Tkinter object that holds a string
        # and can notify widgets automatically when its value changes.
        # We use it to track whether the player chose "X" or "O".
        # Default is "X" (pre-selected when the form opens).
        self.p1_symbol_var = tk.StringVar(value="X")

        # Create both symbol cards and store references so they can
        # update each other's highlight when one is selected.
        self.sym_card_x = self._symbol_card(
            sym_row, "X", "Play as X", C["x"], self.p1_symbol_var,
        )
        self.sym_card_o = self._symbol_card(
            sym_row, "O", "Play as O", C["o"], self.p1_symbol_var,
        )
        self.sym_card_x.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.sym_card_o.pack(side="left", expand=True, fill="x", padx=(6, 0))

        # The "Continue" button calls _on_p1_continue when clicked.
        self._primary_button(
            self.frm_p1, "Continue →", self._on_p1_continue,
        ).pack(fill="x")

    # ── Step 3: player 2 config (two-player only) ─────────

    def _build_player2_step(self, parent):
        """
        Create the name-entry form for Player 2.
        Player 2's symbol is auto-assigned (the opposite of Player 1's),
        so there's no symbol picker here — just a display box showing
        what they'll get.
        """
        self.frm_p2 = tk.Frame(parent, bg=C["surface"])

        tk.Label(
            self.frm_p2, text="Player 2 Setup",
            font=self.F["title"], fg=C["accent"], bg=C["surface"],
        ).pack(pady=(0, 4))

        tk.Label(
            self.frm_p2, text="Tell us about Player 2",
            font=self.F["body"], fg=C["muted"], bg=C["surface"],
        ).pack(pady=(0, 16))

        tk.Label(
            self.frm_p2, text="PLAYER 2 NAME",
            font=self.F["label"], fg=C["muted"], bg=C["surface"],
        ).pack(anchor="w")

        self.entry_p2 = self._make_entry(self.frm_p2, placeholder="Player #2")
        self.entry_p2.pack(fill="x", pady=(4, 14))

        tk.Label(
            self.frm_p2, text="PLAYER 2 SYMBOL",
            font=self.F["label"], fg=C["muted"], bg=C["surface"],
        ).pack(anchor="w")

        # A read-only display box showing the auto-assigned symbol.
        # We keep a reference so we can update the text when Player 1
        # changes their symbol choice.
        sym_box = tk.Frame(
            self.frm_p2, bg=C["surf2"],
            highlightbackground=C["border"], highlightthickness=1,
        )
        sym_box.pack(fill="x", pady=(4, 18))

        self.lbl_p2_auto_sym = tk.Label(
            sym_box, text="○", font=self.F["symbol"], fg=C["o"], bg=C["surf2"],
        )
        self.lbl_p2_auto_sym.pack(pady=(8, 2))

        tk.Label(
            sym_box, text="Auto-assigned (opposite of Player 1)",
            font=self.F["label"], fg=C["muted"], bg=C["surf2"],
        ).pack(pady=(0, 8))

        self._primary_button(
            self.frm_p2, "Start Game →", self._on_p2_continue,
        ).pack(fill="x")

    # ──────────────────────────────────────────────────────
    # GAME SCREEN BUILDER
    # ──────────────────────────────────────────────────────

    def _build_game_screen(self):
        """
        Create the main game layout: a title at the top, then two
        columns below — the board on the left and the scoreboard on
        the right.  Everything is hidden until _show_game_screen()
        is called.
        """
        self.frm_game = tk.Frame(self.root, bg=C["bg"])

        # Game title at the top of the game screen.
        tk.Label(
            self.frm_game, text="Tic-Tac-Toe",
            font=self.F["title"], fg=C["accent"], bg=C["bg"],
        ).pack(pady=(14, 10))

        # A horizontal frame to hold the two columns side by side.
        columns = tk.Frame(self.frm_game, bg=C["bg"])
        columns.pack(padx=20, pady=(0, 20))

        self._build_board_column(columns)       # left column
        self._build_scoreboard_column(columns)  # right column

    def _build_board_column(self, parent):
        """
        Build the left column: a dark card containing a square Canvas
        widget.  The board is drawn on the Canvas using shapes, not
        widget buttons — this gives us full control over the appearance.
        """
        # The card frame acts as a visual border / background for the canvas.
        board_frame = tk.Frame(
            parent, bg=C["surface"],
            highlightbackground=C["border"], highlightthickness=1,
        )
        board_frame.pack(side="left", padx=(0, 16))

        # Calculate how large the canvas needs to be.
        # 3 cells wide + 2 gaps + 2 edge insets (same formula on both axes
        # because the board is a square).
        canvas_size = CELL_PX * 3 + GAP_PX * 2 + INSET_PX * 2

        # tk.Canvas is a blank rectangle we can draw shapes on.
        # highlightthickness=0 removes the default focus ring border.
        self.canvas = tk.Canvas(
            board_frame,
            width=canvas_size, height=canvas_size,
            bg=C["surface"], highlightthickness=0,
        )
        self.canvas.pack(padx=6, pady=6)

        # EVENT BINDING:
        #   .bind("<EventName>", handler_function) tells Tkinter:
        #   "whenever <EventName> happens on this widget, call handler_function".
        #
        #   <Button-1>  = left mouse button click
        #   <Motion>    = mouse moved while over the widget
        #   <Leave>     = mouse left the widget area
        #
        self.canvas.bind("<Button-1>", self._on_cell_click)
        self.canvas.bind("<Motion>",   self._on_mouse_move)
        # lambda e: ignores the event object (e) we don't need it here.
        self.canvas.bind("<Leave>",    lambda e: self._set_hover(-1))

    def _build_scoreboard_column(self, parent):
        """
        Build the right column:
          • Score card  — two player tiles (symbol, name, win count) + games played
          • Status card — "Sid's Turn" / "Computer is thinking…"
          • Two action buttons — Reset Scores, New Game Setup
        """
        # width=252 gives the right column a fixed width.
        # pack_propagate(False) stops the frame from shrinking to fit its children.
        right = tk.Frame(parent, bg=C["bg"], width=252)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        # ── Score card ──────────────────────────────────
        score_card = tk.Frame(
            right, bg=C["surface"],
            highlightbackground=C["border"], highlightthickness=1,
        )
        score_card.pack(fill="x", pady=(0, 10))

        # Horizontal row for the two player tiles and the "VS" badge.
        tiles_row = tk.Frame(score_card, bg=C["surface"])
        tiles_row.pack(padx=10, pady=10, fill="x")

        # _player_tile() builds a tile AND stores label references
        # (self._sym0, self._name0, self._wins0, etc.) so we can
        # update them later without keeping local variables.
        self.tile_p1 = self._player_tile(tiles_row, player_index=0)
        self.tile_p1.pack(side="left", expand=True, fill="both")

        tk.Label(
            tiles_row, text="VS",
            font=self.F["label"], fg=C["muted"], bg=C["surface"],
        ).pack(side="left", padx=6)

        self.tile_p2 = self._player_tile(tiles_row, player_index=1)
        self.tile_p2.pack(side="left", expand=True, fill="both")

        # A 1-pixel-tall frame acts as a horizontal divider line.
        tk.Frame(score_card, bg=C["border"], height=1).pack(fill="x", padx=10)

        # Games-played row: label on the left, number on the right.
        games_row = tk.Frame(score_card, bg=C["surface"])
        games_row.pack(fill="x", padx=10, pady=8)
        tk.Label(
            games_row, text="Games Played",
            font=self.F["body"], fg=C["muted"], bg=C["surface"],
        ).pack(side="left")
        # We keep this label reference so we can update the number later.
        self.lbl_games = tk.Label(
            games_row, text="0",
            font=self.F["heading"], fg=C["text"], bg=C["surface"],
        )
        self.lbl_games.pack(side="right")

        # ── Status card ─────────────────────────────────
        status_card = tk.Frame(
            right, bg=C["surface"],
            highlightbackground=C["border"], highlightthickness=1,
        )
        status_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            status_card, text="CURRENT TURN",
            font=self.F["label"], fg=C["muted"], bg=C["surface"],
        ).pack(pady=(10, 2))

        # Reference kept so we can update the player name each turn.
        self.lbl_turn = tk.Label(
            status_card, text="—",
            font=self.F["status"], fg=C["accent"], bg=C["surface"],
        )
        self.lbl_turn.pack(pady=(0, 10))

        # ── Action buttons ───────────────────────────────
        self._secondary_button(
            right, "↺  Reset Scores", self._reset_scores,
        ).pack(fill="x", pady=(0, 6))

        self._danger_button(
            right, "⊕  New Game Setup", self._go_to_setup,
        ).pack(fill="x")

    # ──────────────────────────────────────────────────────
    # REUSABLE WIDGET FACTORY METHODS
    #
    # A "factory" method is one whose job is to CREATE and
    # return a widget.  We factor out common widget patterns
    # so we don't repeat the same configuration code in
    # multiple places.
    # ──────────────────────────────────────────────────────

    def _mode_card(self, parent, icon, title, description, command):
        """
        Build and return one large, clickable mode-selection card.

        WHY BIND TO THE FRAME AND ALL ITS CHILDREN?
          A tk.Frame is a container.  When you click on a Label
          inside the frame, Tkinter fires the event on the Label,
          not on the Frame.  So if we only bound the click to the
          Frame, clicking on the icon or the text wouldn't work.
          We loop over [frame] + list(frame.winfo_children()) to
          bind the same handlers to every widget in the card.
        """
        frame = tk.Frame(
            parent, bg=C["surf2"], cursor="hand2",
            highlightbackground=C["border"], highlightthickness=2,
        )

        tk.Label(frame, text=icon,        font=self.F["emoji"],   bg=C["surf2"]).pack(pady=(14, 4))
        tk.Label(frame, text=title,       font=self.F["heading"], fg=C["text"],  bg=C["surf2"]).pack()
        tk.Label(frame, text=description, font=self.F["label"],   fg=C["muted"], bg=C["surf2"]).pack(pady=(2, 14))

        # Bind click + hover highlight to every widget in the card.
        # f=frame captures the current frame value in the lambda's
        # default argument — without this, all lambdas would share
        # the last value of `frame` (a common Python closure pitfall).
        all_widgets = [frame] + list(frame.winfo_children())
        for widget in all_widgets:
            widget.bind("<Button-1>", lambda e: command())
            widget.bind("<Enter>",
                        lambda e, f=frame: f.config(highlightbackground=C["accent"]))
            widget.bind("<Leave>",
                        lambda e, f=frame: f.config(highlightbackground=C["border"]))

        return frame

    def _symbol_card(self, parent, symbol, label_text, color, string_var):
        """
        Build and return a clickable card for choosing X or O.

        HOW THE SELECT CLOSURE WORKS:
          `select` is a function defined inside _symbol_card.  It
          "closes over" the variables `symbol`, `string_var`,
          `self.sym_card_x`, and `self.sym_card_o` — meaning it
          remembers them even after _symbol_card has finished running.
          When the user clicks the card, Tkinter calls select(),
          which updates the StringVar and redraws both card borders.

        WHY USE StringVar INSTEAD OF A PLAIN STRING?
          We need to READ the chosen symbol later (in _on_p1_continue).
          A plain string variable can't be "observed" by Tkinter.
          StringVar is a special container that lets multiple widgets
          share and react to the same value.
        """
        char  = "✕" if symbol == "X" else "○"

        # X card starts with accent border (pre-selected); O card starts plain.
        frame = tk.Frame(
            parent, bg=C["surf2"], cursor="hand2",
            highlightbackground=C["accent"] if symbol == "X" else C["border"],
            highlightthickness=2,
        )

        tk.Label(frame, text=char,       font=self.F["symbol"], fg=color,    bg=C["surf2"]).pack(pady=(10, 2))
        tk.Label(frame, text=label_text, font=self.F["label"],  fg=C["muted"], bg=C["surf2"]).pack(pady=(0, 10))

        def select():
            # Update the shared StringVar to record which symbol was chosen.
            string_var.set(symbol)
            # Visually update BOTH cards: selected one gets accent border,
            # the other gets the plain border colour back.
            self.sym_card_x.config(
                highlightbackground=C["accent"] if string_var.get() == "X" else C["border"],
            )
            self.sym_card_o.config(
                highlightbackground=C["accent"] if string_var.get() == "O" else C["border"],
            )

        for widget in [frame] + list(frame.winfo_children()):
            widget.bind("<Button-1>", lambda e: select())

        return frame

    def _player_tile(self, parent, player_index):
        """
        Build and return the score tile for one player.
        The tile shows:  symbol  /  name  /  big win number  /  "WINS" label

        HOW setattr WORKS:
          setattr(self, "_sym0", lbl_sym) is exactly the same as
          writing self._sym0 = lbl_sym  — but it lets us build the
          attribute name dynamically using an f-string.
          We use this so _refresh_scoreboard_labels() can loop over
          both players with  getattr(self, f"_sym{i}")  instead of
          having two separate if-branches.
        """
        sym_color = C["x"] if player_index == 0 else C["o"]

        frame = tk.Frame(
            parent, bg=C["surf2"],
            highlightbackground=C["border"], highlightthickness=2,
        )

        # Symbol label (large ✕ or ○)
        lbl_sym = tk.Label(
            frame,
            text="✕" if player_index == 0 else "○",
            font=self.F["symbol"], fg=sym_color, bg=C["surf2"],
        )
        lbl_sym.pack(pady=(8, 0))

        # Player name — wraplength=90 allows long names to wrap.
        lbl_name = tk.Label(
            frame,
            text=f"Player {player_index + 1}",
            font=self.F["body"], fg=C["text"], bg=C["surf2"],
            wraplength=90,
        )
        lbl_name.pack(pady=(2, 4))

        # Win count — large gold number
        lbl_wins = tk.Label(
            frame, text="0",
            font=self.F["score"], fg=C["win"], bg=C["surf2"],
        )
        lbl_wins.pack()

        tk.Label(
            frame, text="WINS",
            font=self.F["label"], fg=C["muted"], bg=C["surf2"],
        ).pack(pady=(0, 8))

        # Dynamically create attributes like self._sym0, self._name0, self._wins0
        # so they can be updated later without if/else branches.
        setattr(self, f"_sym{player_index}",  lbl_sym)
        setattr(self, f"_name{player_index}", lbl_name)
        setattr(self, f"_wins{player_index}", lbl_wins)

        return frame

    def _make_entry(self, parent, placeholder):
        """
        Build and return a text-entry box with placeholder behaviour.

        WHAT IS A PLACEHOLDER?
          Placeholder text is the greyed-out hint shown inside an empty
          input box (e.g. "Player #1").  When the user clicks into the
          box the hint disappears; if they leave without typing anything,
          the hint comes back.

        HOW WE IMPLEMENT IT:
          We use two nested functions (on_focus_in and on_focus_out) and
          bind them to FocusIn and FocusOut events.
            FocusIn  fires when the widget gains keyboard focus (user clicks it).
            FocusOut fires when the widget loses focus (user clicks elsewhere).

          We distinguish between "real" content and the placeholder by
          checking the text colour.  Placeholder text is C["muted"] (grey);
          real user input is C["text"] (white).  We store the placeholder
          string on the entry widget itself (entry._placeholder) so we
          can read it back in _read_entry().
        """
        entry = tk.Entry(
            parent,
            font=self.F["body"],
            bg=C["surf2"],
            fg=C["muted"],            # greyed-out placeholder colour
            insertbackground=C["text"],  # cursor (insertion point) colour
            relief="flat",            # no 3-D raised border
            bd=8,                     # padding inside the entry box
            highlightbackground=C["border"],
            highlightcolor=C["accent"],  # border colour when focused
            highlightthickness=1,
        )

        # Attach the placeholder string as a custom attribute.
        entry._placeholder = placeholder
        entry.insert(0, placeholder)    # pre-fill the box with placeholder text

        def on_focus_in(e):
            # User clicked into the box.  If it still shows the placeholder,
            # clear it and switch to real-text colour.
            if entry.get() == entry._placeholder and entry["fg"] == C["muted"]:
                entry.delete(0, "end")
                entry.config(fg=C["text"])

        def on_focus_out(e):
            # User left the box.  If they didn't type anything, restore
            # the placeholder text and grey colour.
            if not entry.get():
                entry.insert(0, entry._placeholder)
                entry.config(fg=C["muted"])

        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        return entry

    def _read_entry(self, entry):
        """
        Safely read the real value from an entry made by _make_entry().

        WHY NOT JUST CALL entry.get()?
          If the user never clicked the box, entry.get() returns the
          placeholder string (e.g. "Player #1"), not an empty string.
          We want to treat the placeholder as "no input" so we can
          fall back to the default name.  We detect the placeholder by
          checking whether the text matches AND the colour is muted grey.
          If so, we return "" so the caller can apply the default.
        """
        value = entry.get()
        if value == entry._placeholder and entry["fg"] == C["muted"]:
            return ""     # placeholder is still showing — treat as empty
        return value.strip()   # strip() removes leading/trailing whitespace

    def _primary_button(self, parent, text, command):
        """
        Styled accent-purple button (used for the main call-to-action).
        relief="flat" and bd=0 remove the default 3-D border so it looks modern.
        """
        return tk.Button(
            parent, text=text, font=self.F["button"], command=command,
            bg=C["accent"], fg="white",
            activebackground="#6d28d9", activeforeground="white",
            relief="flat", bd=0, pady=10, cursor="hand2",
        )

    def _secondary_button(self, parent, text, command):
        """Styled grey button (used for less critical actions like Reset)."""
        return tk.Button(
            parent, text=text, font=self.F["button"], command=command,
            bg=C["surf2"], fg=C["muted"],
            activebackground=C["surf3"], activeforeground=C["text"],
            relief="flat", bd=0, pady=8, cursor="hand2",
            highlightbackground=C["border"], highlightthickness=1,
        )

    def _danger_button(self, parent, text, command):
        """
        Red-tinted button (used for destructive actions like New Game Setup,
        which discards all progress and returns to the start screen).
        The colour signals caution to the user.
        """
        return tk.Button(
            parent, text=text, font=self.F["button"], command=command,
            bg="#2d1a1f", fg=C["x"],
            activebackground="#3d2a2f", activeforeground=C["x"],
            relief="flat", bd=0, pady=8, cursor="hand2",
            highlightbackground="#5d2030", highlightthickness=1,
        )

    # ──────────────────────────────────────────────────────
    # SCREEN NAVIGATION
    # ──────────────────────────────────────────────────────

    def _show_setup_screen(self):
        """
        Bring the setup modal into view.

        HOW SHOW / HIDE WORKS IN TKINTER:
          Tkinter's layout manager (pack) tracks which widgets are
          "managed" (visible).  pack_forget() tells pack to stop
          managing a widget — it becomes invisible but still exists.
          pack() tells pack to manage it again — it becomes visible.
          This is much faster than destroying and recreating widgets.
        """
        self.frm_game.pack_forget()          # hide the game screen
        self.frm_setup.pack(expand=True, fill="both")  # show the setup screen
        self._show_step(self.frm_mode)       # make sure step 1 is visible
        self._center_window(500, 420)        # resize and centre the window

    def _show_game_screen(self):
        """
        Switch from the setup screen to the game board.
        We calculate the needed window size from the board dimensions
        so the window is always exactly the right size.
        """
        self.frm_setup.pack_forget()
        self.frm_game.pack(expand=True, fill="both")

        # Calculate the total width:
        #   canvas width  +  canvas outer padding  +  column gap
        #                 +  right panel width  +  outer margins
        canvas_size = CELL_PX * 3 + GAP_PX * 2 + INSET_PX * 2
        w = canvas_size + 12 + 16 + 252 + 60
        h = canvas_size + 12 + 110   # canvas + title area + bottom padding
        self._center_window(w, h)

    def _show_step(self, step_frame):
        """
        Show exactly ONE of the three setup steps and hide the others.
        We always hide all three first, then show the one we want.
        This guarantees no two steps are visible at the same time,
        even if the code calls this function unexpectedly.
        """
        for frame in (self.frm_mode, self.frm_p1, self.frm_p2):
            frame.pack_forget()   # hide all three steps
        step_frame.pack(fill="both")  # show only the requested one

    def _center_window(self, width, height):
        """
        Resize the main window and move it to the centre of the screen.

        HOW TKINTER WINDOW GEOMETRY WORKS:
          root.geometry("WxH+X+Y") sets the window to W pixels wide,
          H pixels tall, and positions its top-left corner at (X, Y).

          winfo_screenwidth()  → total screen width  in pixels
          winfo_screenheight() → total screen height in pixels

          To centre, we calculate:
            X = (screen_width  - window_width)  // 2
            Y = (screen_height - window_height) // 2
          (//)  is integer division — discards any decimal remainder.

          update_idletasks() tells Tkinter to process any pending layout
          work before we measure the screen; without it the measurements
          might be wrong.
        """
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - width)  // 2
        y  = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # ──────────────────────────────────────────────────────
    # SETUP FLOW  —  what happens when the user clicks things
    # ──────────────────────────────────────────────────────

    def _on_mode_chosen(self, mode):
        """
        Called when the user clicks 'Single Player' or 'Two Players'.
        We save the mode, update the Player 1 form title to match,
        and advance to step 2.
        """
        self.state["mode"] = mode

        # Customise the heading text for the next step.
        if mode == "single":
            self.lbl_p1_title.config(text="Your Setup")
            self.lbl_p1_sub.config(text="Set up your profile")
        else:
            self.lbl_p1_title.config(text="Player 1 Setup")
            self.lbl_p1_sub.config(text="Tell us about Player 1")

        self._show_step(self.frm_p1)
        self.entry_p1.focus()   # move keyboard focus into the name box

    def _on_p1_continue(self):
        """
        Called when the user clicks 'Continue' on the Player 1 form.

        We read the name (defaulting to 'Player #1' if blank), read
        the chosen symbol, and save both into the state dictionary.
        Then we either start the game immediately (single-player) or
        advance to the Player 2 form (two-player).

        THE "or" TRICK FOR DEFAULT VALUES:
          _read_entry returns "" when the box is blank.
          "" is falsy in Python, so:
              "" or "Player #1"   →  "Player #1"
              "Sid" or "Player #1" →  "Sid"
          This is a common Python idiom for setting defaults.
        """
        name   = self._read_entry(self.entry_p1) or "Player #1"
        symbol = self.p1_symbol_var.get()    # "X" or "O"
        self.state["players"][0] = {"name": name, "symbol": symbol}

        if self.state["mode"] == "single":
            # The computer always gets the opposite symbol.
            # If player chose X, computer gets O, and vice versa.
            comp_symbol = "O" if symbol == "X" else "X"
            self.state["players"][1] = {"name": "Computer", "symbol": comp_symbol}
            self._start_game()
        else:
            # Two-player: update the auto-assigned symbol display
            # on the Player 2 form before showing it.
            p2_symbol = "O" if symbol == "X" else "X"
            self.state["players"][1]["symbol"] = p2_symbol
            self.lbl_p2_auto_sym.config(
                text="✕" if p2_symbol == "X" else "○",
                fg=C["x"]  if p2_symbol == "X" else C["o"],
            )
            self._show_step(self.frm_p2)
            self.entry_p2.focus()

    def _on_p2_continue(self):
        """
        Called when the user clicks 'Start Game' on the Player 2 form.
        Save Player 2's name (with the same blank-default logic) and
        then start the game.
        """
        name = self._read_entry(self.entry_p2) or "Player #2"
        self.state["players"][1]["name"] = name
        self._start_game()

    # ──────────────────────────────────────────────────────
    # GAME LIFECYCLE
    # ──────────────────────────────────────────────────────

    def _start_game(self):
        """
        Called once when players finish the setup flow.
        Updates the scoreboard labels to show the real player names
        and symbols (which were just confirmed), then shows the game
        screen and starts the first round.

        WHY TWO SEPARATE METHODS (_start_game and _new_round)?
          _start_game handles the one-time transition from setup to game:
            updating labels, switching screens.
          _new_round handles resetting between games (the board clears
            but the scores and player names stay the same).
          Keeping them separate means Play Again only needs _new_round.
        """
        self._refresh_scoreboard_labels()    # put real names/symbols in tiles
        self._refresh_scoreboard_numbers()   # make sure scores start at 0
        self._show_game_screen()             # switch to the board view
        self._new_round()                    # start the first round

    def _new_round(self):
        """
        Reset the board and start a fresh game round.
        Scores and player info are preserved.

        KEY CONCEPT — starting player alternation:
          self.state["starter"] holds the index of who goes first.
          Each time Play Again is clicked, we flip it:
            1 - 0 = 1  (Player 2 goes next)
            1 - 1 = 0  (Player 1 goes after that)
          The flip happens in _show_result_popup's play_again function.
          Here we just read "starter" and set "current" to match.
        """
        s = self.state
        s["board"]     = [None] * 9   # empty all 9 squares
        s["current"]   = s["starter"] # who goes first this round
        s["over"]      = False        # game is not yet over
        s["win_cells"] = []           # no winning squares to highlight
        s["thinking"]  = False        # computer is not mid-move
        self._hovered_cell = -1       # no cell is being hovered

        self._draw_board()           # render the empty board
        self._refresh_turn_label()   # show whose turn it is

        # Special case: if the computer goes first (because starter==1),
        # we trigger its move automatically with a short delay.
        if s["mode"] == "single" and s["current"] == 1:
            self._schedule_computer_move()

    # ──────────────────────────────────────────────────────
    # BOARD DRAWING
    # ──────────────────────────────────────────────────────
    #
    # The board is drawn by painting shapes onto a tk.Canvas.
    # Every time the board changes (a move is made, a cell is
    # hovered) we call _draw_board() which clears the canvas
    # and repaints everything from scratch.
    #
    # This "clear and redraw" approach is simple and reliable.
    # The alternative — updating only the changed cell — is
    # faster but much more complex to implement.
    # ──────────────────────────────────────────────────────

    def _cell_rect(self, index):
        """
        Convert a board index (0–8) into the pixel rectangle that
        the cell occupies on the canvas.  Returns (x1, y1, x2, y2).

        HOW THE MATHS WORKS:
          The board has 3 columns and 3 rows.  Given index 0–8:

            row = index // 3    (// = integer division, drops remainder)
              index 0,1,2 → row 0  (top row)
              index 3,4,5 → row 1  (middle row)
              index 6,7,8 → row 2  (bottom row)

            col = index % 3     (% = modulo, gives the remainder)
              index 0,3,6 → col 0  (left column)
              index 1,4,7 → col 1  (middle column)
              index 2,5,8 → col 2  (right column)

          Then we convert row/col into pixels:
            x1 = INSET_PX + col * (CELL_PX + GAP_PX)
            y1 = INSET_PX + row * (CELL_PX + GAP_PX)
            x2 = x1 + CELL_PX
            y2 = y1 + CELL_PX
        """
        row = index // 3
        col = index % 3
        x1  = INSET_PX + col * (CELL_PX + GAP_PX)
        y1  = INSET_PX + row * (CELL_PX + GAP_PX)
        return x1, y1, x1 + CELL_PX, y1 + CELL_PX

    def _cell_at_pixel(self, px, py):
        """
        Given a canvas pixel coordinate (px, py), find which cell
        index (0–8) contains that point.  Returns -1 if the point
        is not inside any cell (e.g. it's in the gap or the inset).

        WHY NOT JUST DIVIDE BY CELL SIZE?
          The gaps and insets mean the maths isn't a simple division.
          The safest approach is to check all 9 cells one by one using
          _cell_rect() — that reuses the exact same formula that draws
          them, so the hit areas always match the visual cells exactly.
        """
        for i in range(9):
            x1, y1, x2, y2 = self._cell_rect(i)
            if x1 <= px <= x2 and y1 <= py <= y2:
                return i
        return -1   # pixel is between cells or in the inset area

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=14, **kwargs):
        """
        Draw a rectangle with rounded corners on the canvas.

        WHY NOT canvas.create_rectangle()?
          Tkinter's built-in rectangle has sharp right-angle corners.
          For the modern rounded look we use a polygon (a shape with
          many points) and ask Tkinter to smooth the corners with
          smooth=True.

        HOW THE POINTS WORK:
          We place two control points near each corner.  The smooth
          algorithm then draws a gentle curve between them.  The
          'radius' parameter controls how rounded the corners are:
          a bigger radius = a rounder corner.

        **kwargs lets callers pass any extra arguments (fill, outline,
        width…) straight through to create_polygon().
        """
        r = radius
        points = [
            x1+r, y1,   x2-r, y1,   # top edge
            x2,   y1,   x2,   y1+r, # top-right corner control points
            x2,   y2-r, x2,   y2,   # right edge
            x2-r, y2,   x1+r, y2,   # bottom edge
            x1,   y2,   x1,   y2-r, # bottom-left corner control points
            x1,   y1+r, x1,   y1,   # left edge
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def _draw_board(self):
        """
        Erase the canvas completely and repaint all 9 cells plus any
        symbols on them.

        LOOP BREAKDOWN:
          for i in range(9):  iterates over indices 0, 1, 2, … 8.
          We compute three Boolean flags for each cell:
            is_winning — this cell is part of the winning line (highlight gold)
            is_hovered — mouse is over this empty cell (highlight purple)
          Then we pick the correct colours and draw the cell background.
          Finally, if the cell has a symbol ("X" or "O"), we draw it.
        """
        self.canvas.delete("all")   # wipe the entire canvas clean
        s = self.state

        for i in range(9):
            x1, y1, x2, y2 = self._cell_rect(i)

            # Is this one of the 3 winning squares?
            is_winning = i in s["win_cells"]

            # Is the mouse hovering over this cell, and is it empty,
            # and is the game still going?
            is_hovered = (
                i == self._hovered_cell
                and s["board"][i] is None
                and not s["over"]
            )

            # Choose background and border colour based on cell state.
            if is_winning:
                fill, outline = "#2a1f00", C["win"]    # dark gold tint + gold border
            elif is_hovered:
                fill, outline = C["surf3"], C["accent"] # slightly lighter + purple border
            else:
                fill, outline = C["surf2"], C["border"] # default dark + subtle border

            self._draw_rounded_rect(x1, y1, x2, y2,
                                    fill=fill, outline=outline, width=2)

            # Draw the symbol if this cell has been played.
            value = s["board"][i]
            if value:
                # Winning symbols turn gold; others keep their normal colour.
                color = C["win"] if is_winning else (C["x"] if value == "X" else C["o"])
                self._draw_symbol(value, x1, y1, x2, y2, color)

    def _draw_symbol(self, symbol, x1, y1, x2, y2, color):
        """
        Draw an X or O inside the given cell rectangle.

        X is drawn as two diagonal lines crossing each other.
        O is drawn as a circle (oval that fits a square = circle).

        SYM_PAD shrinks the drawing inward from the cell edges so the
        symbol doesn't touch the cell border — it gives visual breathing
        room.  capstyle="round" makes the line ends circular (no sharp
        edges on the X strokes).
        """
        p = SYM_PAD   # inset amount from each edge of the cell

        if symbol == "X":
            # Line 1: top-left to bottom-right  \
            self.canvas.create_line(
                x1+p, y1+p, x2-p, y2-p,
                fill=color, width=7, capstyle="round",
            )
            # Line 2: top-right to bottom-left  /
            self.canvas.create_line(
                x2-p, y1+p, x1+p, y2-p,
                fill=color, width=7, capstyle="round",
            )
        else:   # "O"
            # Oval with equal width/height bounds → perfect circle.
            self.canvas.create_oval(
                x1+p, y1+p, x2-p, y2-p,
                outline=color, width=7,
            )

    # ──────────────────────────────────────────────────────
    # BOARD INTERACTION  —  click and hover events
    # ──────────────────────────────────────────────────────

    def _on_cell_click(self, event):
        """
        Called by Tkinter whenever the user left-clicks on the canvas.
        event.x and event.y are the pixel coordinates of the click.

        GUARD CLAUSES — "fail fast" pattern:
          Instead of nesting all the logic inside if-statements,
          we check each invalid condition at the top and return early
          (exit the function immediately) if it applies.  This keeps
          the "happy path" at the bottom without deep nesting.
        """
        index = self._cell_at_pixel(event.x, event.y)
        s     = self.state

        # Guard 1: Click wasn't inside any cell (e.g. in the gap area).
        if index == -1:
            return

        # Guard 2: The game is already over, or the cell is occupied,
        # or the computer hasn't finished its move yet.
        if s["over"] or s["board"][index] or s["thinking"]:
            return

        # Guard 3: Single-player mode and it's the computer's turn (index 1).
        # Human is always player 0.
        if s["mode"] == "single" and s["current"] == 1:
            return   # ignore — wait for the computer to move

        # All checks passed — make the move.
        self._place_move(index, s["current"])

    def _on_mouse_move(self, event):
        """
        Called whenever the mouse moves over the canvas.
        We figure out which cell the mouse is over and update
        the hover highlight.
        """
        self._set_hover(self._cell_at_pixel(event.x, event.y))

    def _set_hover(self, index):
        """
        Update which cell is highlighted as 'hovered'.
        We ONLY redraw the board when the hover cell actually changes —
        moving the mouse within the same cell won't cause a redraw.
        This avoids unnecessary work.
        """
        if index != self._hovered_cell:
            self._hovered_cell = index
            self._draw_board()   # repaint with new hover state

    # ──────────────────────────────────────────────────────
    # GAMEPLAY LOGIC
    # ──────────────────────────────────────────────────────

    def _place_move(self, index, player_index):
        """
        The core game step: place a symbol, then check for an ending.

        FLOW:
          1. Write the player's symbol into the board list.
          2. Redraw the board so the symbol appears.
          3. Check for a winner → if found, end the game as a win.
          4. Check for a draw   → if found, end the game as a draw.
          5. Otherwise, switch turns and (if single-player and now the
             computer's turn) trigger the computer's move.

        SWITCHING TURNS — the 1 - n trick:
          player_index is either 0 or 1.
            1 - 0 = 1  (switch from Player 1 to Player 2)
            1 - 1 = 0  (switch from Player 2 to Player 1)
          This is a neat one-liner to toggle between two values.
        """
        s = self.state
        s["board"][index] = s["players"][player_index]["symbol"]
        self._draw_board()   # show the freshly placed symbol

        winner_cells = find_winner(s["board"])
        if winner_cells:
            self._end_game(result="win",  player_index=player_index,
                           win_cells=winner_cells)
        elif is_draw(s["board"]):
            self._end_game(result="draw", player_index=-1, win_cells=[])
        else:
            # Game continues — switch turns.
            s["current"] = 1 - player_index

            if s["mode"] == "single" and s["current"] == 1:
                # It's now the computer's turn.
                s["thinking"] = True          # block human clicks
                self._refresh_turn_label()    # show "Computer is thinking…"
                self._schedule_computer_move()
            else:
                self._refresh_turn_label()    # show the next player's name

    def _end_game(self, result, player_index, win_cells):
        """
        Handle the end of a game (win or draw).

        WHY root.after() INSTEAD OF time.sleep()?
          time.sleep(0.75) would freeze the ENTIRE application for
          750 ms — no redraws, no events.  The board highlight
          would never appear before the popup opened.

          root.after(delay_ms, function) asks Tkinter to call
          `function` after `delay_ms` milliseconds, but lets the
          main loop keep running in the meantime.  The board redraws
          with the golden win-cell highlight, the user sees it for
          three-quarters of a second, and THEN the popup appears.
          This feels much more polished.
        """
        s = self.state
        s["over"]      = True
        s["win_cells"] = win_cells
        s["thinking"]  = False   # clear thinking flag (game is over anyway)

        if result == "win":
            s["wins"][player_index] += 1   # +=1 increments the win counter

        s["games"] += 1            # always increment total games played

        self._draw_board()                    # repaint with gold win highlights
        self._refresh_scoreboard_numbers()    # update the score tiles
        self._refresh_turn_label()            # clear the "current turn" label

        # Schedule the popup AFTER a short pause so the final board is visible.
        delay_ms = 750 if result == "win" else 500
        self.root.after(delay_ms, lambda: self._show_result_popup(result, player_index))

    # ──────────────────────────────────────────────────────
    # COMPUTER AI  —  scheduling and executing
    # ──────────────────────────────────────────────────────

    def _schedule_computer_move(self):
        """
        Ask Tkinter to call _do_computer_move after 650 milliseconds.

        WHY 650 MS?
          Without a delay the computer would respond instantly, which
          feels robotic and gives the human no time to register what
          just happened.  A short pause makes the computer feel like
          it's "thinking" and gives the game a natural rhythm.

          root.after(650, self._do_computer_move) is non-blocking —
          the game window stays responsive while waiting.
        """
        self.root.after(650, self._do_computer_move)

    def _do_computer_move(self):
        """
        Look up the best move for the computer and play it.
        This method is called by root.after() once the delay expires.
        We pass the board and both symbols to best_move() (defined at
        the top of the file as a pure function).
        """
        s         = self.state
        comp_sym  = s["players"][1]["symbol"]
        human_sym = s["players"][0]["symbol"]
        move_index = best_move(s["board"], comp_sym, human_sym)

        s["thinking"] = False   # thinking is done
        self._place_move(move_index, player_index=1)

    # ──────────────────────────────────────────────────────
    # UI REFRESH METHODS
    #
    # These methods READ from self.state and UPDATE the widgets
    # to match.  They never change the game logic — only the
    # display.  Keeping display code separate from logic code
    # is called "separation of concerns" and makes both parts
    # easier to read, test, and change.
    # ──────────────────────────────────────────────────────

    def _refresh_scoreboard_labels(self):
        """
        Update the symbol character, symbol colour, and player name
        in both score tiles to match the current state.

        HOW getattr WORKS:
          getattr(self, "_sym0") is the same as self._sym0.
          Using getattr with an f-string lets us loop over both
          players instead of writing two identical blocks.
        """
        for i, player in enumerate(self.state["players"]):
            sym_char  = "✕" if player["symbol"] == "X" else "○"
            sym_color = C["x"] if player["symbol"] == "X" else C["o"]
            getattr(self, f"_sym{i}").config(text=sym_char, fg=sym_color)
            getattr(self, f"_name{i}").config(text=player["name"])

    def _refresh_scoreboard_numbers(self):
        """
        Update the win counts in both score tiles and the
        games-played counter.

        str(n) converts an integer to a string because Tkinter's
        label .config(text=…) expects a string, not a number.
        """
        s = self.state
        self._wins0.config(text=str(s["wins"][0]))
        self._wins1.config(text=str(s["wins"][1]))
        self.lbl_games.config(text=str(s["games"]))

    def _refresh_turn_label(self):
        """
        Update the 'Current Turn' status card and highlight the
        active player's score tile with a purple border.

        Three possible states:
          1. Game is over    → show "—", no tile highlighted
          2. AI is thinking  → show "Computer is thinking…", highlight tile 2
          3. Normal turn     → show "[Name]'s Turn", highlight that player's tile
        """
        s     = self.state
        tiles = [self.tile_p1, self.tile_p2]

        if s["over"]:
            self.lbl_turn.config(text="—")
            tiles[0].config(highlightbackground=C["border"])
            tiles[1].config(highlightbackground=C["border"])

        elif s["thinking"]:
            self.lbl_turn.config(text="Computer is thinking…")
            tiles[0].config(highlightbackground=C["border"])
            tiles[1].config(highlightbackground=C["accent"])  # highlight computer

        else:
            cp   = s["current"]    # index of the current player (0 or 1)
            name = s["players"][cp]["name"]
            self.lbl_turn.config(text=f"{name}'s Turn")
            # Highlight the active tile, un-highlight the other.
            tiles[0].config(highlightbackground=C["accent"] if cp == 0 else C["border"])
            tiles[1].config(highlightbackground=C["accent"] if cp == 1 else C["border"])

    # ──────────────────────────────────────────────────────
    # RESULT POPUP
    # ──────────────────────────────────────────────────────

    def _show_result_popup(self, result, player_index):
        """
        Show a small popup window announcing the winner or a draw,
        with Play Again and Quit buttons.

        WHAT IS tk.Toplevel?
          Toplevel is a second window (child of the main window).
          We use it for the popup because it appears on top of the
          main window and can block interaction with it.

        grab_set():
          Forces all mouse and keyboard events to go to the popup
          until it's closed.  This prevents the user from clicking
          the board or the scoreboard buttons while the popup is open.

        transient(self.root):
          Links the popup's lifetime to the main window.  If the
          main window is minimised or closed, the popup follows.

        NESTED FUNCTIONS — play_again and quit_to_setup:
          These are defined INSIDE _show_result_popup so they can
          "close over" the `popup` variable and call popup.destroy()
          to close the window.  This is cleaner than passing `popup`
          as an argument to separate methods.
        """
        popup = tk.Toplevel(self.root)
        popup.title("")                    # no title bar text
        popup.resizable(False, False)
        popup.configure(bg=C["surface"])
        popup.grab_set()                   # block the main window
        popup.transient(self.root)         # tie to main window

        # Centre the popup over the main window.
        pw, ph = 340, 270
        rx = self.root.winfo_x() + (self.root.winfo_width()  - pw) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - ph) // 2
        popup.geometry(f"{pw}x{ph}+{rx}+{ry}")

        # Choose content based on result.
        if result == "win":
            winner_name = self.state["players"][player_index]["name"]
            emoji  = "🏆"
            title  = f"{winner_name} Wins!"
            color  = C["win"]
            detail = "Congratulations — what a game!"
        else:
            emoji  = "🤝"
            title  = "It's a Draw!"
            color  = C["muted"]
            detail = "Great effort from both players!"

        tk.Label(popup, text=emoji, font=self.F["emoji"],
                 bg=C["surface"]).pack(pady=(22, 4))
        tk.Label(popup, text=title, font=self.F["title"],
                 fg=color, bg=C["surface"]).pack()
        tk.Label(popup, text=detail, font=self.F["body"],
                 fg=C["muted"], bg=C["surface"]).pack(pady=(4, 20))

        btn_row = tk.Frame(popup, bg=C["surface"])
        btn_row.pack(padx=24)

        def play_again():
            """Close the popup and start another round."""
            popup.destroy()
            # Flip the starter: 1-0=1, 1-1=0 — fair alternation every game.
            self.state["starter"] = 1 - self.state["starter"]
            self._new_round()

        def quit_to_setup():
            """Close the popup and return to the mode-selection screen."""
            popup.destroy()
            self._go_to_setup()

        self._primary_button(
            btn_row, "Play Again", play_again,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._secondary_button(
            btn_row, "Quit", quit_to_setup,
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    # ──────────────────────────────────────────────────────
    # CONTROL BUTTON CALLBACKS
    # ──────────────────────────────────────────────────────

    def _reset_scores(self):
        """
        Zero out the win counters and games-played count, then
        refresh the scoreboard display.
        The board, current players, and game mode are all kept.
        """
        self.state["wins"]  = [0, 0]
        self.state["games"] = 0
        self._refresh_scoreboard_numbers()

    def _go_to_setup(self):
        """
        Return to the very beginning: wipe the state, reset the
        form inputs to their defaults, and show the mode-selection
        screen.

        WHY new_state() INSTEAD OF MANUALLY RESETTING EACH KEY?
          Calling new_state() gives us a fresh dictionary in one line
          and guarantees we can't forget to reset any key.  If we add
          a new key to new_state() later, this reset is automatically
          correct — we don't have to remember to add a reset line here.
        """
        self.state = new_state()   # full state reset

        # Reset both name-entry boxes back to their placeholder text.
        for entry, placeholder in [(self.entry_p1, "Player #1"),
                                   (self.entry_p2, "Player #2")]:
            entry.delete(0, "end")          # clear all text
            entry.insert(0, placeholder)    # restore placeholder
            entry.config(fg=C["muted"])     # restore grey placeholder colour

        # Reset symbol cards: X is selected, O is deselected.
        self.p1_symbol_var.set("X")
        self.sym_card_x.config(highlightbackground=C["accent"])
        self.sym_card_o.config(highlightbackground=C["border"])

        self._show_setup_screen()


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
#
#  __name__ is a special variable Python sets automatically.
#  When you run this file directly with "python tic_tac_toe.py",
#  Python sets __name__ to "__main__".
#  When another file imports this file (e.g. for testing),
#  Python sets __name__ to the filename instead.
#
#  The "if __name__ == '__main__':" guard means this block only
#  runs when you execute the file directly — NOT when it's
#  imported.  This is a universal Python best practice.
#
#  WHAT THE THREE LINES DO:
#    tk.Tk()          — create the main window (the OS window object)
#    TicTacToe(root)  — create our game, wiring it to that window
#    root.mainloop()  — hand control to Tkinter.  It sits in an
#                       infinite loop processing mouse clicks,
#                       keyboard events, and redraws until the
#                       window is closed.
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app  = TicTacToe(root)
    root.mainloop()
