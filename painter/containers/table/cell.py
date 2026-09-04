from __future__ import annotations
from painter.containers.container import Container


class Cell(Container):
    _coordinates: tuple[int, int] = (0, 0)
    _table = None

    def _changed(self, field):
        self._update_pixels()
        if self._table:
            self._table._changed("update")

    @property
    def outline_width(self):
        return self._outline_width

    @outline_width.setter
    def outline_width(self, value):
        if self.outline_width == value:
            return

        self._outline_width = value
        self._left_outline_width = value
        self._right_outline_width = value
        self._top_outline_width = value
        self._bottom_outline_width = value
        self._update_pixels()

        if self._table:
            self._table._changed("outline_width")

    @property
    def left_outline_width(self):
        return self._left_outline_width

    @left_outline_width.setter
    def left_outline_width(self, value):
        if self.left_outline_width == value:
            return

        self._left_outline_width = value
        self._outline_width = None
        self._update_pixels()
        if self._table:
            self._table._changed("outline_width")

    @property
    def right_outline_width(self):
        return self._right_outline_width

    @right_outline_width.setter
    def right_outline_width(self, value):
        if self.right_outline_color == value:
            return

        self._right_outline_width = value
        self._outline_width = None
        self._update_pixels()
        self._table._changed("outline_width")

    @property
    def top_outline_width(self):
        return self._top_outline_width

    @top_outline_width.setter
    def top_outline_width(self, value):
        if self.top_outline_width == value:
            return

        self._top_outline_width = value
        self._outline_width = None
        self._update_pixels()
        self._table._changed("outline_width")

    @property
    def bottom_outline_width(self):
        return self._bottom_outline_width

    @bottom_outline_width.setter
    def bottom_outline_width(self, value):
        if self.bottom_outline_width == value:
            return

        self._bottom_outline_width = value
        self._outline_width = None
        self._update_pixels()
        self._table._changed("outline_width")

    @property
    def vertical_alignment(self):
        return self._vertical_alignment

    @vertical_alignment.setter
    def vertical_alignment(self, value):
        if self._vertical_alignment == value:
            return

        self._vertical_alignment = value
        self._update_pixels()
        if self._table:
            self._table._changed("vertical_alignment")

    @property
    def horizontal_alignment(self):
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, value):
        if self._horizontal_alignment == value:
            return

        self._horizontal_alignment = value
        self._update_pixels()
        if self._table:
            self._table._changed("horizontal_alignment")

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

    @property
    def row(self):
        return self.coordinates[0]

    @row.setter
    def row(self, value):
        self.coordinates = (value, self.column)

    @property
    def column(self):
        return self.coordinates[1]

    @column.setter
    def column(self, value):
        self.coordinates = (self.row, value)
