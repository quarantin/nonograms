import os
import json
import pygame

from enum import IntEnum


class GridValue(IntEnum):
    NONE = -1
    UNSET = 0
    SET = 1


class Grid:
    def __init__(self, screen, puzzle, x, y, cell_size):
        self.screen = screen
        self.puzzle = puzzle
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.rows = puzzle.rows
        self.columns = puzzle.columns
        self.width = cell_size * puzzle.columns
        self.height = cell_size * puzzle.rows
        self.border_width = 4
        self.grid_color = (0, 0, 0)
        self.default_color = (255, 255, 153)
        self.border_color = (0, 255, 0)
        self.enabled_color = (0, 0, 255)
        self.disabled_color = (255, 0, 0)
        self.background_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 24)
        self.grid = [
            [GridValue.NONE for _ in range(puzzle.columns)]
            for _ in range(puzzle.rows)
        ]

    def save(self, path):
        with open(path, "w") as fd:
            json.dump(self.grid, fd)

    def load(self, path):
        if os.path.exists(path):
            with open(path, "r") as fd:
                raw_grid = json.load(fd)
                self.grid = [[GridValue(cell) for cell in row] for row in raw_grid]

    def reset(self):
        for row in range(self.puzzle.rows):
            for column in range(self.puzzle.columns):
                self.grid[row][column] = GridValue.NONE

    def autofill_completed_rows(self):
        moves = []
        for row_idx, row in enumerate(self.grid):
            if self.puzzle.get_clues(row) == self.puzzle.get_row_clues(row_idx):
                for col_idx, cell_value in enumerate(row):
                    if cell_value == GridValue.NONE:
                        self.grid[row_idx][col_idx] = GridValue.UNSET
                        moves.append((row_idx, col_idx, GridValue.NONE, GridValue.UNSET))
        return moves

    def autofill_completed_columns(self):
        moves = []
        for col_idx in range(self.puzzle.columns):
            column = [self.grid[row_idx][col_idx] for row_idx in range(self.puzzle.rows)]
            if self.puzzle.get_clues(column) == self.puzzle.get_column_clues(col_idx):
                for row_idx in range(self.puzzle.rows):
                    cell_value = self.grid[row_idx][col_idx]
                    if cell_value == GridValue.NONE:
                        self.grid[row_idx][col_idx] = GridValue.UNSET
                        moves.append((row_idx, col_idx, GridValue.NONE, GridValue.UNSET))
        return moves

    def autofill_completed_lines(self):
        moves = []
        moves.extend(self.autofill_completed_rows())
        moves.extend(self.autofill_completed_columns())
        return moves

    def get_value(self, pos):
        cell = self.get_cell(pos)
        if cell is None:
            return None

        row, col = cell
        return self.grid[row][col]

    def get_cell(self, pos):

        mouse_x, mouse_y = pos

        if not (self.x <= mouse_x < self.x + self.width and self.y <= mouse_y < self.y + self.height):
            return None

        x_offset = mouse_x - self.x
        y_offset = mouse_y - self.y

        def compute_index(offset, count):
            raw = offset // self.cell_size
            extras = max(0, (raw // 5) - (1 if raw == count else 0))
            adjusted = (offset - extras) // self.cell_size
            return adjusted

        col = compute_index(x_offset, self.puzzle.columns)
        row = compute_index(y_offset, self.puzzle.rows)

        return (row, col)

    def set_cell(self, pos, value, clicked_value):

        cell = self.get_cell(pos)
        if cell is None:
            return None

        row, col = cell
        current = self.grid[row][col]
        if current != clicked_value:
            return None

        previous_value = current

        if value == GridValue.UNSET:

            if current == GridValue.NONE:
                self.grid[row][col] = GridValue.UNSET

            elif current == GridValue.UNSET:
                self.grid[row][col] = GridValue.NONE

        elif value == GridValue.SET:

            if current == GridValue.NONE:
                self.grid[row][col] = GridValue.SET

            elif current == GridValue.SET:
                self.grid[row][col] = GridValue.NONE

        new_value = self.grid[row][col]
        if new_value != previous_value:
            return (row, col, previous_value, new_value)

        return None

    def draw_cell(self, row, column):
        x = self.x + column * self.cell_size + max(0, (column // 5))
        y = self.y + row * self.cell_size + max(0, (row // 5))
        rectangle = (x, y, self.cell_size, self.cell_size)
        value = self.grid[row][column]
        if value in [GridValue.NONE, GridValue.UNSET]:
            color = self.default_color

        elif value == GridValue.SET:
            color = self.enabled_color

        else:
            raise Exception(f"Invalid value: {value}")

        pygame.draw.rect(self.screen, color, rectangle)

        if value == GridValue.UNSET:
            self.draw_cross(x, y)

    def get_clue_font_color(self, user_row_or_column, puzzle_row_or_column):

        if user_row_or_column == puzzle_row_or_column:
            return (150, 150, 150)

        if GridValue.NONE not in user_row_or_column:
            return (255, 0, 0)

        return (0, 0, 0)

    def draw_row_clues(self):
        for i, clues in enumerate(self.puzzle.get_all_row_clues()):

            user_row = self.grid[i]
            puzzle_row = self.puzzle.grid[i]
            color = self.get_clue_font_color(user_row, puzzle_row)

            y = self.y + i * self.cell_size + self.cell_size // 2

            for j, number in enumerate(reversed(clues)):
                x = self.x - (j + 1) * 20
                text = self.font.render(str(number), True, color)
                self.screen.blit(text, (x, y - text.get_height() // 2))

    def draw_column_clues(self):
        for i, clues in enumerate(self.puzzle.get_all_column_clues()):

            user_column = [self.grid[row][i] for row in range(self.puzzle.rows)]
            puzzle_column = [self.puzzle.grid[row][i] for row in range(self.puzzle.rows)]
            color = self.get_clue_font_color(user_column, puzzle_column)

            x = self.x + i * self.cell_size + self.cell_size // 2

            for j, number in enumerate(reversed(clues)):
                y = self.y - (j + 1) * 20
                text = self.font.render(str(number), True, color)
                self.screen.blit(text, (x - text.get_width() // 2, y))

    def draw_clues(self):
        self.draw_row_clues()
        self.draw_column_clues()

    def draw_cross(self, x, y):

        margin = self.cell_size // 6

        start_x = x + margin
        end_x = x + self.cell_size - margin

        start_y = y + margin
        end_y = y + self.cell_size - margin

        pygame.draw.line(self.screen, (100, 100, 100), (start_x, start_y), (end_x, end_y), 5)
        pygame.draw.line(self.screen, (100, 100, 100), (start_x, end_y), (end_x, start_y), 5)

    def draw(self):

        self.screen.fill(self.background_color)

        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                self.draw_cell(row_index, col_index)
 
        x = self.x
        for column in range(self.puzzle.columns + 1):
            is_wide_line = column % 5 == 0 and column != 0 and column != self.puzzle.columns
            line_width = 2 if is_wide_line else 1
            pygame.draw.line(self.screen, self.grid_color, (x, self.y), (x, self.y + self.height), width=line_width)
            x += self.cell_size
            if is_wide_line:
                x += 1

        y = self.y
        for row in range(self.puzzle.rows + 1):
            is_wide_line = row % 5 == 0 and row != 0 and row != self.puzzle.rows
            line_width = 2 if is_wide_line else 1
            pygame.draw.line(self.screen, self.grid_color, (self.x, y), (self.x + self.width, y), width=line_width)
            y += self.cell_size
            if is_wide_line:
                y += 1

        border_rectangle = (
            self.x - self.border_width + 1,
            self.y - self.border_width + 1,
            self.width + self.border_width * 2 - 1,
            self.height + self.border_width *2 - 1,
        )

        pygame.draw.rect(self.screen, self.border_color, border_rectangle, width=self.border_width)
        self.draw_clues()
