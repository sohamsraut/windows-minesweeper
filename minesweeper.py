import tkinter as tk
from tkinter import messagebox
import random
import time

# Number colors like original Minesweeper
NUMBER_COLORS = {
    1: "blue", 2: "green", 3: "red",
    4: "navy", 5: "maroon", 6: "teal",
    7: "black", 8: "gray"
}

class Cell:
    def __init__(self):
        self.is_mine = False
        self.adjacent_mines = 0
        self.revealed = False
        self.flagged = False

class MinesweeperGUI:
    def __init__(self, root, rows=9, cols=9, mines=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.first_click = True
        self.start_time = None
        self.timer_running = False

        self.board = []
        self.buttons = []

        self.create_menu()
        self.create_ui()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Beginner (9x9, 10 mines)", command=lambda: self.set_difficulty(9, 9, 10))
        game_menu.add_command(label="Intermediate (16x16, 40 mines)", command=lambda: self.set_difficulty(16, 16, 40))
        game_menu.add_command(label="Expert (16x30, 99 mines)", command=lambda: self.set_difficulty(16, 30, 99))
        menubar.add_cascade(label="Game", menu=game_menu)
        self.root.config(menu=menubar)

    def set_difficulty(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.reset_game()

    def create_ui(self):
        # Top control frame
        self.top_frame = tk.Frame(self.root, bg="lightgray", bd=3, relief=tk.SUNKEN)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.mine_count_var = tk.StringVar(value=f"{self.total_mines:03}")
        self.mine_label = tk.Label(self.top_frame, textvariable=self.mine_count_var,
                                   font=("Courier", 18, "bold"), bg="black", fg="red", width=3)
        self.mine_label.pack(side=tk.LEFT, padx=10)

        self.smiley_var = tk.StringVar(value="😊")
        self.smiley_btn = tk.Button(self.top_frame, textvariable=self.smiley_var, font=("Arial", 16),
                                    width=2, command=self.reset_game)
        self.smiley_btn.pack(side=tk.LEFT, expand=True)

        self.timer_var = tk.StringVar(value="000")
        self.timer_label = tk.Label(self.top_frame, textvariable=self.timer_var,
                                    font=("Courier", 18, "bold"), bg="black", fg="red", width=3)
        self.timer_label.pack(side=tk.RIGHT, padx=10)

        self.frame = tk.Frame(self.root, bg="gray", bd=3, relief=tk.SUNKEN)
        self.frame.pack()

        self.build_board()

    def build_board(self):
        self.board = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.frame, width=2, height=1, font=("Arial", 12, "bold"),
                                relief=tk.RAISED, bg="lightgray",
                                command=lambda r=r, c=c: self.on_left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.on_right_click(r, c))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

    def reset_game(self):
        self.first_click = True
        self.timer_running = False
        self.start_time = None
        self.timer_var.set("000")
        self.mine_count_var.set(f"{self.total_mines:03}")
        self.smiley_var.set("😊")

        for widget in self.frame.winfo_children():
            widget.destroy()
        self.build_board()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time()
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.timer_var.set(f"{elapsed:03}")
            self.root.after(1000, self.update_timer)

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r, c):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr != 0 or dc != 0:
                    nr, nc = r + dr, c + dc
                    if self.in_bounds(nr, nc):
                        yield nr, nc

    def place_mines(self, safe_r, safe_c):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)
                     if (r, c) != (safe_r, safe_c)]
        random.shuffle(positions)
        for i in range(self.total_mines):
            r, c = positions[i]
            self.board[r][c].is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c].adjacent_mines = sum(
                    self.board[nr][nc].is_mine for nr, nc in self.neighbors(r, c)
                )

    def on_left_click(self, r, c):
        cell = self.board[r][c]
        if cell.flagged or cell.revealed:
            return
        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False
            self.start_timer()

        if cell.is_mine:
            self.buttons[r][c].config(bg="red", text="💣")
            self.smiley_var.set("😵")
            self.game_over(False)
        else:
            self.reveal_cell(r, c)
            if self.check_win():
                self.smiley_var.set("😎")
                self.game_over(True)

    def on_right_click(self, r, c):
        cell = self.board[r][c]
        if cell.revealed:
            return
        cell.flagged = not cell.flagged
        self.buttons[r][c].config(text="🚩" if cell.flagged else "")
        remaining = self.total_mines - sum(self.board[i][j].flagged for i in range(self.rows) for j in range(self.cols))
        self.mine_count_var.set(f"{remaining:03}")

    def reveal_cell(self, r, c):
        cell = self.board[r][c]
        if cell.revealed or cell.flagged:
            return
        cell.revealed = True
        btn = self.buttons[r][c]
        btn.config(relief=tk.SUNKEN, bg="white")

        if cell.adjacent_mines > 0:
            btn.config(text=str(cell.adjacent_mines), fg=NUMBER_COLORS.get(cell.adjacent_mines, "black"))
        else:
            for nr, nc in self.neighbors(r, c):
                self.reveal_cell(nr, nc)

    def reveal_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.board[r][c]
                btn = self.buttons[r][c]
                if cell.is_mine:
                    btn.config(text="💣", bg="lightgray")
                elif cell.adjacent_mines > 0:
                    btn.config(text=str(cell.adjacent_mines), fg=NUMBER_COLORS.get(cell.adjacent_mines, "black"))

    def game_over(self, win):
        self.timer_running = False
        for r in range(self.rows):
            for c in range(self.cols):
                self.buttons[r][c].config(state=tk.DISABLED)
        self.reveal_all()
        if win:
            messagebox.showinfo("Victory", "🎉 You cleared the minefield!")
        else:
            messagebox.showinfo("Game Over", "💥 You hit a mine!")

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.board[r][c]
                if not cell.is_mine and not cell.revealed:
                    return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minesweeper")
    game = MinesweeperGUI(root, rows=9, cols=9, mines=10)  # Default beginner
    root.mainloop()
