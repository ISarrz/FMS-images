from __future__ import annotations

from painter.containers.simple_container import SimpleContainer


class Pixels:
    # container: SimpleContainer
    _left_top: tuple[int, int] = (0, 0)
    _right_bottom: tuple[int, int] = (0, 0)
    _padding: int = 0
    _margin: int = 0
    _container: SimpleContainer = SimpleContainer()

    def __init__(self, container=None, left_top=(0, 0), right_bottom=(0, 0), padding=0, margin=0):
        self.left_top = left_top
        self.right_bottom = right_bottom
        self.padding = padding
        self.margin = margin
        self.container = container

    @property
    def container(self) -> SimpleContainer:
        return self._container

    @container.setter
    def container(self, container: SimpleContainer):
        self._container = container

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, value):
        if self.padding == value:
            return
        self._padding = value
        if self.container:
            self._container._changed("padding")

    @property
    def center_x(self):
        return self.center[0]

    @property
    def center_y(self):
        return self.center[1]

    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, value):
        if self.margin == value:
            return
        self._margin = value
        if self.container:
            self._container._changed("margin")

    @property
    def left_top(self):
        return self._left_top

    @property
    def right_bottom(self):
        return self._right_bottom

    @property
    def left_x(self):
        return self.left_top[0]

    @property
    def top_y(self):
        return self.left_top[1]

    @property
    def right_x(self):
        return self.right_bottom[0]

    @property
    def bottom_y(self):
        return self.right_bottom[1]

    @property
    def width(self):
        return self.right_x - self.left_x + 1

    @property
    def height(self):
        return self.bottom_y - self.top_y + 1

    @property
    def center(self):
        return (self.left_x + self.right_x) // 2, (self.top_y + self.bottom_y) // 2

    @left_top.setter
    def left_top(self, value: tuple[int, int]):
        if self.left_top == value:
            return

        width = self.width
        height = self.height
        self._left_top = value
        self._right_bottom = self.left_x + width - 1, self.top_y + height - 1

        if self.container:
            self._container._changed("left_top")

    @right_bottom.setter
    def right_bottom(self, value: tuple[int, int]):
        if self.right_bottom == value:
            return

        width = self.width
        height = self.height
        self._right_bottom = value
        self._left_top = self.right_x - width + 1, self.bottom_y - height + 1

        if self.container:
            self._container._changed("right_bottom")

    @width.setter
    def width(self, value):
        value = int(value)
        if self.width == value:
            return
        self._right_bottom = self.left_top[0] + value - 1, self.right_bottom[1]

        if self.container:
            self._container._changed("width")

    @height.setter
    def height(self, value):
        value = int(value)
        if self.height == value:
            return
        self._right_bottom = self.right_bottom[0], self.left_top[1] + value - 1

        if self.container:
            self._container._changed("height")

    @center.setter
    def center(self, value):
        if self.center == value:
            return
        width = self.width
        height = self.height
        left_width = (width + 1) // 2
        right_width = width // 2
        top_height = (height + 1) // 2
        bottom_height = (height + 1) // 2

        self.left_top = value[0] - left_width, value[1] - top_height
        self.right_bottom = value[0] + right_width, value[1] + bottom_height

        if self.container:
            self._container._changed("center")


if __name__ == "__main__":
    container = SimpleContainer()
    pixels = Pixels()
    pixels.container = container
