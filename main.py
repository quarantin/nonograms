#!/usr/bin/env python

import pygame

from button import Button, MouseButton
from grid import Grid, GridValue
from nonogram import NonogramPuzzle


pygame.init()

puzzle = NonogramPuzzle("Nonogram 1")

SAVE_FILE = "save.json"
CELL_SIZE = 30
WIDTH = puzzle.columns * CELL_SIZE + puzzle.columns // 5 - 1
HEIGHT = puzzle.rows * CELL_SIZE + puzzle.rows // 5 - 1

screen = pygame.display.set_mode((WIDTH + 500, HEIGHT + 500))
pygame.display.set_caption("Pygame Window")

grid = Grid(screen, puzzle, 250, 250, CELL_SIZE)
grid.load(SAVE_FILE)

dragging = False
drag_value = None
clicked_value = None

moves = []

undo_stack = []
redo_stack = []

grouped_moves = []

def action_quit():
    global running
    running = False


def action_reset():
    grid.reset()

def action_undo():
    if undo_stack:
        moves = undo_stack.pop()
        for row, col, prev, new in moves:
            grid.grid[row][col] = GridValue(prev)
        redo_stack.append(moves)

def action_redo():
    if redo_stack:
        moves = redo_stack.pop()
        for row, col, prev, new in moves:
            grid.grid[row][col] = GridValue(new)
        undo_stack.append(moves)

quit_button = Button(50, 50, 100, 40, "Quit", action_quit)
reset_button = Button(50, 100, 100, 40, "Reset", action_reset)
undo_button = Button(50, 150, 100, 40, "Undo", action_undo)
redo_button = Button(50, 200, 100, 40, "Redo", action_redo)

success = False
running = True
while running:

    grid.draw()

    quit_button.draw(screen)
    reset_button.draw(screen)
    undo_button.draw(screen)
    redo_button.draw(screen)

    for event in pygame.event.get():

        quit_button.handle_event(event)
        reset_button.handle_event(event)
        undo_button.handle_event(event)
        redo_button.handle_event(event)

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == MouseButton.LEFT:
                dragging = True
                drag_value = 1

            elif event.button == MouseButton.RIGHT:
                dragging = True
                drag_value = 0

            cell = grid.get_cell(event.pos)
            if cell is not None:
                moves = []
                clicked_value = grid.get_value(event.pos)
                move = grid.set_cell(event.pos, drag_value, clicked_value)
                if move:
                    moves.append(move)
                last_cell = cell

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                dragging = False
                drag_value = None
                clicked_value = None
                last_cell = None

                if moves:
                    moves.extend(grid.autofill_completed_lines())
                    undo_stack.append(moves)
                    redo_stack.clear()
                    moves = []

        elif event.type == pygame.MOUSEMOTION and dragging:
            current_cell = grid.get_cell(event.pos)
            if current_cell and current_cell != last_cell:
                move = grid.set_cell(event.pos, drag_value, clicked_value)
                if move:
                    moves.append(move)
                last_cell = current_cell

    pygame.display.flip()

    if success is False and puzzle.is_grid_valid(grid):
        success = True
        print("w00t")

grid.save(SAVE_FILE)
pygame.quit()
