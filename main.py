import tkinter as tk
from tkinter import ttk
import random
import json
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import os

# ============================
# CONSTANTS
# ============================
CHOICES = ["rock", "paper", "scissors"]
COUNTER_MOVE = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
DATA_FILE = "ai_memory.json"

BG = "#121212"
FG = "#ffffff"
PANEL = "#1f1f1f"
BTN = "#2e2e2e"


# ============================
# AI CLASS
# ============================
class SmartAI:
    def __init__(self):
        self.transitions = defaultdict(Counter)
        self.last_move = None
        self.load_memory()

    def update(self, prev_move, current_move):
        if prev_move:
            self.transitions[prev_move][current_move] += 1
        self.last_move = current_move
        self.save_memory()

    def predict(self):
        if not self.last_move:
            return random.choice(CHOICES)

        counter = self.transitions[self.last_move]
        if not counter:
            return random.choice(CHOICES)

        predicted = counter.most_common(1)[0][0]
        return COUNTER_MOVE[predicted]

    def save_memory(self):
        with open(DATA_FILE, "w") as f:
            json.dump(
                {k: dict(v) for k, v in self.transitions.items()}, f
            )

    def load_memory(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                for k, v in data.items():
                    self.transitions[k] = Counter(v)


# ============================
# GAME STATS CLASS
# ============================
class GameStats:
    def __init__(self):
        self.reset()

    def reset(self):
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.rounds = 0
        self.ai_correct = 0


# ============================
# MAIN GAME GUI
# ============================
class RPSGameGUI:
    def __init__(self, root):
        self.root = root
        self.ai = SmartAI()
        self.stats = GameStats()
        self.player_history = []

        self.difficulty = tk.StringVar(value="Easy")
        self.setup_ui()

    # ---------------- UI ----------------
    def setup_ui(self):
        self.root.title("Rock Paper Scissors – Smart AI")
        self.root.geometry("550x650")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        tk.Label(
            self.root, text="🎮 Rock Paper Scissors",
            font=("Segoe UI", 20, "bold"), fg=FG, bg=BG
        ).pack(pady=10)

        tk.Label(
            self.root, text="Adaptive Predictive AI | Dark Mode",
            font=("Segoe UI", 10), fg="#b0bec5", bg=BG
        ).pack()

        self.create_difficulty_panel()
        self.create_buttons()
        self.create_result_area()
        self.create_history()
        self.create_actions()

        self.update_stats()

    def create_difficulty_panel(self):
        panel = tk.LabelFrame(
            self.root, text=" AI Difficulty ",
            font=("Segoe UI", 10, "bold"),
            fg=FG, bg=PANEL, padx=10, pady=10
        )
        panel.pack(pady=12)

        ttk.Combobox(
            panel, textvariable=self.difficulty,
            values=["Easy", "Medium", "Hard"],
            state="readonly", width=20
        ).pack()

        tk.Label(
            panel,
            text="Easy: Random | Medium: Mixed | Hard: Predictive",
            fg="#b0bec5", bg=PANEL, font=("Segoe UI", 9)
        ).pack(pady=4)

    def create_buttons(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(pady=10)

        for i, choice in enumerate(CHOICES):
            tk.Button(
                frame,
                text=choice.capitalize(),
                width=12,
                height=2,
                font=("Segoe UI", 11, "bold"),
                bg=BTN, fg=FG, bd=0,
                command=lambda c=choice: self.play(c)
            ).grid(row=0, column=i, padx=6)

    def create_result_area(self):
        self.result_label = tk.Label(
            self.root, text="", font=("Segoe UI", 12),
            fg=FG, bg=BG
        )
        self.result_label.pack(pady=6)

        self.status_label = tk.Label(
            self.root, text="", font=("Segoe UI", 16, "bold"),
            bg=BG
        )
        self.status_label.pack()

        self.score_label = tk.Label(
            self.root, font=("Segoe UI", 11),
            fg="#80cbc4", bg=BG
        )
        self.score_label.pack(pady=4)

        self.accuracy_label = tk.Label(
            self.root, font=("Segoe UI", 11),
            fg="#ffcc80", bg=BG
        )
        self.accuracy_label.pack()

    def create_history(self):
        tk.Label(
            self.root, text="📜 Round History",
            fg=FG, bg=BG, font=("Segoe UI", 11, "bold")
        ).pack(pady=4)

        self.history_box = tk.Listbox(
            self.root, width=55, height=8,
            bg=PANEL, fg=FG
        )
        self.history_box.pack()

    def create_actions(self):
        tk.Button(
            self.root, text="📊 Show Performance Graph",
            width=30, bg="#009688", fg="white",
            bd=0, command=self.show_graph
        ).pack(pady=6)

        tk.Button(
            self.root, text="🔄 Reset Game",
            width=30, bg="#ff7043", fg="white",
            bd=0, command=self.reset_game
        ).pack(pady=6)

        tk.Label(
            self.root, text="Built with Python & Smart AI",
            fg="#9e9e9e", bg=BG, font=("Segoe UI", 9)
        ).pack(side="bottom", pady=6)

    # ---------------- GAME LOGIC ----------------
    def ai_choice(self):
        if self.difficulty.get() == "Easy":
            return random.choice(CHOICES)

        if self.difficulty.get() == "Medium":
            return self.ai.predict() if random.random() > 0.5 else random.choice(CHOICES)

        return self.ai.predict()

    def play(self, player):
        ai_move = self.ai_choice()
        prev = self.player_history[-1] if self.player_history else None

        self.player_history.append(player)
        self.ai.update(prev, player)
        self.stats.rounds += 1

        if self.ai.predict() == ai_move:
            self.stats.ai_correct += 1

        result = self.decide_winner(player, ai_move)
        self.update_ui(player, ai_move, result)

    def decide_winner(self, p, a):
        if p == a:
            self.stats.draws += 1
            return "DRAW"
        if (p, a) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            self.stats.wins += 1
            return "WIN"
        self.stats.losses += 1
        return "LOSS"

    # ---------------- UI UPDATES ----------------
    def update_ui(self, p, a, result):
        self.result_label.config(
            text=f"You: {p.upper()}   AI: {a.upper()}"
        )

        colors = {"WIN": "#4caf50", "LOSS": "#f44336", "DRAW": "#ffeb3b"}
        self.status_label.config(text=result, fg=colors[result])

        self.history_box.insert(
            tk.END,
            f"Round {self.stats.rounds}: You {p} | AI {a} → {result}"
        )

        self.update_stats()

    def update_stats(self):
        acc = (self.stats.ai_correct / self.stats.rounds * 100) if self.stats.rounds else 0

        self.score_label.config(
            text=f"Rounds: {self.stats.rounds}  Wins: {self.stats.wins}  "
                 f"Losses: {self.stats.losses}  Draws: {self.stats.draws}"
        )
        self.accuracy_label.config(text=f"🤖 AI Accuracy: {acc:.2f}%")

    # ---------------- EXTRAS ----------------
    def show_graph(self):
        plt.bar(["Wins", "Losses", "Draws"],
                [self.stats.wins, self.stats.losses, self.stats.draws])
        plt.title("Game Performance")
        plt.show()

    def reset_game(self):
        self.stats.reset()
        self.player_history.clear()
        self.history_box.delete(0, tk.END)
        self.status_label.config(text="Game Reset ✔", fg="white")
        self.update_stats()


# ============================
# RUN APP
# ============================
if __name__ == "__main__":
    root = tk.Tk()
    RPSGameGUI(root)
    root.mainloop()
