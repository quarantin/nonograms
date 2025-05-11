import json


class NonogramPuzzle:

    def __init__(self, name):
        with open("data.json") as fd:
            jsondata = json.loads(fd.read())

        nonograms = {x["name"]: x["grid"] for x in jsondata["nonograms"]}

        if name not in nonograms:
            raise Exception(f"No such nonogram `{name}`")

        self.grid = nonograms[name]
        self.rows = len(self.grid)
        self.columns = len(self.grid[0])

    def get_clues(self, row_or_column):
        result = []
        count = 0
        for value in row_or_column:

            if value == 1:
                count += 1

            elif count > 0:
                result.append(count)
                count = 0
                
        if count > 0:
            result.append(count)

        return result

    def get_row_clues(self, row):
        return self.get_clues(self.grid[row])

    def get_column_clues(self, column):
        data = [row[column] for row in self.grid]
        return self.get_clues(data)

    def get_all_row_clues(self):
        result = []

        for row in range(0, self.rows):
            result.append(self.get_row_clues(row))

        return result

    def get_all_column_clues(self):
        result = []

        for column in range(0, self.columns):
            result.append(self.get_column_clues(column))

        return result

    def is_grid_valid(self, user_grid):
        for puzzle_row, user_row in zip(self.grid, user_grid.grid):
            for puzzle_cell, user_cell in zip(puzzle_row, user_row):
                if puzzle_cell != user_cell:
                    return False
        return True

