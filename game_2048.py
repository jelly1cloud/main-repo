# file: game_2048.py
# Requires: Python 3 (tkinter included in standard library)
# Usage: python game_2048.py

import tkinter as tk
import random
import sys

GRID_LEN = 4
CELL_SIZE = 100
PADDING = 10
BACKGROUND_COLOR = "#bbada0"
EMPTY_CELL_COLOR = "#cdc1b4"
FONT = ("Verdana", 24, "bold")

# color map for tiles
TILE_COLORS = {
    0: ("#cdc1b4", "#776e65"),
    2: ("#eee4da", "#776e65"),
    4: ("#ede0c8", "#776e65"),
    8: ("#f2b179", "#f9f6f2"),
    16: ("#f59563", "#f9f6f2"),
    32: ("#f67c5f", "#f9f6f2"),
    64: ("#f65e3b", "#f9f6f2"),
    128: ("#edcf72", "#f9f6f2"),
    256: ("#edcc61", "#f9f6f2"),
    512: ("#edc850", "#f9f6f2"),
    1024: ("#edc53f", "#f9f6f2"),
    2048: ("#edc22e", "#f9f6f2"),
}

class Game2048:
    def __init__(self, master):
        self.master = master
        master.title("2048")
        self.reset_game()

        self.main_grid = tk.Frame(master, bg=BACKGROUND_COLOR, bd=3, width=GRID_LEN*CELL_SIZE, height=GRID_LEN*CELL_SIZE)
        self.main_grid.grid(padx=10, pady=10)
        self.cells = []
        self.init_grid()
        self.update_grid_cells()

        # score label and buttons
        self.score = 0
        self.score_label = tk.Label(master, text=f"Score: {self.score}", font=("Helvetica", 14))
        self.score_label.grid()
        btn_frame = tk.Frame(master)
        btn_frame.grid(pady=6)
        tk.Button(btn_frame, text="New Game", command=self.new_game).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Undo", command=self.undo).grid(row=0, column=1, padx=6)
        tk.Button(btn_frame, text="Quit", command=master.quit).grid(row=0, column=2, padx=6)

        master.bind("<Key>", self.key_handler)

    def reset_game(self):
        self.grid = [[0] * GRID_LEN for _ in range(GRID_LEN)]
        self.previous_grid = None
        self.previous_score = 0
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()

    def new_game(self):
        self.reset_game()
        self.update_grid_cells()

    def init_grid(self):
        for i in range(GRID_LEN):
            row = []
            for j in range(GRID_LEN):
                cell_frame = tk.Frame(
                    self.main_grid,
                    bg=EMPTY_CELL_COLOR,
                    width=CELL_SIZE,
                    height=CELL_SIZE
                )
                cell_frame.grid(row=i, column=j, padx=PADDING//2, pady=PADDING//2)
                label = tk.Label(cell_frame, text="", bg=EMPTY_CELL_COLOR, justify=tk.CENTER, font=FONT, width=4, height=2)
                label.pack(expand=True, fill=tk.BOTH)
                row.append(label)
            self.cells.append(row)

    def update_grid_cells(self):
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                value = self.grid[i][j]
                bg_color, fg_color = TILE_COLORS.get(value, ("#3c3a32", "#f9f6f2"))
                self.cells[i][j].configure(text=str(value) if value != 0 else "", bg=bg_color, fg=fg_color)
        self.score_label.configure(text=f"Score: {self.score}")
        self.master.update_idletasks()

    def add_random_tile(self):
        empty = [(i, j) for i in range(GRID_LEN) for j in range(GRID_LEN) if self.grid[i][j] == 0]
        if not empty:
            return False
        i, j = random.choice(empty)
        self.grid[i][j] = 4 if random.random() < 0.1 else 2
        return True

    # movement helpers
    @staticmethod
    def compress(row):
        """Slide non-zero to the left"""
        new_row = [num for num in row if num != 0]
        new_row += [0] * (len(row) - len(new_row))
        return new_row

    @staticmethod
    def merge(row):
        """Merge row after compressing; returns new row and score gained"""
        score_gain = 0
        for i in range(len(row)-1):
            if row[i] != 0 and row[i] == row[i+1]:
                row[i] *= 2
                row[i+1] = 0
                score_gain += row[i]
        return row, score_gain

    def move_left(self):
        moved = False
        total_gain = 0
        new_grid = []
        for i in range(GRID_LEN):
            compressed = self.compress(self.grid[i])
            merged, gain = self.merge(compressed)
            final = self.compress(merged)
            new_grid.append(final)
            if final != self.grid[i]:
                moved = True
            total_gain += gain
        if moved:
            self.previous_grid = [row[:] for row in self.grid]
            self.previous_score = self.score
            self.grid = new_grid
            self.score += total_gain
            self.add_random_tile()
        return moved

    def move_right(self):
        self.reflect_horizontal()
        moved = self.move_left()
        self.reflect_horizontal()
        return moved

    def move_up(self):
        self.transpose()
        moved = self.move_left()
        self.transpose()
        return moved

    def move_down(self):
        self.transpose()
        moved = self.move_right()
        self.transpose()
        return moved

    def transpose(self):
        self.grid = [list(row) for row in zip(*self.grid)]

    def reflect_horizontal(self):
        self.grid = [list(reversed(row)) for row in self.grid]

    def can_move(self):
        # if any empty cell, can move
        if any(self.grid[i][j] == 0 for i in range(GRID_LEN) for j in range(GRID_LEN)):
            return True
        # check merges possible
        for i in range(GRID_LEN):
            for j in range(GRID_LEN-1):
                if self.grid[i][j] == self.grid[i][j+1]:
                    return True
        for j in range(GRID_LEN):
            for i in range(GRID_LEN-1):
                if self.grid[i][j] == self.grid[i+1][j]:
                    return True
        return False

    def key_handler(self, event):
        key = event.keysym
        moved = False
        if key in ("Left", "a", "A"):
            moved = self.move_left()
        elif key in ("Right", "d", "D"):
            moved = self.move_right()
        elif key in ("Up", "w", "W"):
            moved = self.move_up()
        elif key in ("Down", "s", "S"):
            moved = self.move_down()
        elif key in ("r", "R"):
            self.new_game()
            return
        else:
            # ignore other keys
            return

        if moved:
            self.update_grid_cells()
            if not self.can_move():
                self.game_over()

    def game_over(self):
        self.update_grid_cells()
        over = tk.Toplevel(self.master)
        over.title("Game Over")
        tk.Label(over, text=f"Game Over\nScore: {self.score}", font=("Helvetica", 16)).pack(padx=20, pady=10)
        tk.Button(over, text="New Game", command=lambda:[over.destroy(), self.new_game()]).pack(pady=5)
        tk.Button(over, text="Quit", command=self.master.quit).pack(pady=5)

    def undo(self):
        if self.previous_grid is not None:
            self.grid = [row[:] for row in self.previous_grid]
            self.score = self.previous_score
            self.previous_grid = None
            self.update_grid_cells()

def main():
    root = tk.Tk()
    # Center window
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    w = GRID_LEN * CELL_SIZE + 40
    h = GRID_LEN * CELL_SIZE + 120
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    game = Game2048(root)
    root.mainloop()

if __name__ == "__main__":
    main()
