from __future__ import annotations
from painter.containers.table.cell import Cell


class UnitedCell(Cell):
    parent: None  = None
    width: int
    height: int
    left_top: tuple[int, int]
    right_bottom: tuple[int, int]

    @property
    def left_column(self):
        return self.left_top[1]

    @staticmethod
    def convert_cell_to_united_cell(cell: Cell) -> UnitedCell:
        united_cell = UnitedCell()
        united_cell._table = cell._table
        united_cell.fill = cell.fill

        united_cell.pixels = cell.pixels
        united_cell.content = cell.content
        united_cell.coordinates = cell.coordinates
        united_cell.left_top = cell.coordinates
        united_cell.right_bottom = cell.coordinates

        united_cell.horizontal_alignment = cell.horizontal_alignment
        united_cell.vertical_alignment = cell.vertical_alignment
        # united_cell.outline_width = cell.outline_width
        united_cell.outline_color = cell.outline_color

        united_cell.set_main(united_cell, united_cell)

        return united_cell

    @property
    def right_column(self):
        return self.right_bottom[1]

    @property
    def top_row(self):
        return self.left_top[0]

    @property
    def bottom_row(self):
        return self.right_bottom[0]

    def set_parent(self, parent, child_cell):
        self.pixels.width = 0
        self.pixels.height = 0
        self.parent = parent
        self.width = 1
        self.height = 1
        self.coordinates = child_cell.coordinates
        self.left_top = self.coordinates

    def set_main(self, main_cell: UnitedCell, child_cell: UnitedCell):
        self.content = main_cell.content
        self._table = main_cell._table
        self.pixels.left_top = main_cell.pixels.left_top
        self.pixels.width = child_cell.pixels.right_x - main_cell.pixels.left_x + 1
        self.pixels.height = child_cell.pixels.bottom_y - main_cell.pixels.top_y + 1

        self.width = child_cell.right_column - main_cell.left_column + 1
        self.height = child_cell.bottom_row - main_cell.top_row + 1

        self.coordinates = main_cell.coordinates
        self.left_top = main_cell.coordinates
        self.right_bottom = (self.top_row + self.height - 1, self.left_column + self.width - 1)
        self.pixels.padding = main_cell.pixels.padding

        self.fill = main_cell.fill
        self.vertical_alignment = main_cell.vertical_alignment
        self.horizontal_alignment = main_cell.horizontal_alignment
        self.outline_color = main_cell.outline_color
