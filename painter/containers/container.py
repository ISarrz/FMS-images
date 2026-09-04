from painter.containers.pixels import Pixels
from painter.containers.text import Text
from painter.containers.base_container import BaseContainer


class Container(BaseContainer):
    pixels: Pixels
    _outline_width: int = 1
    _left_outline_width: int = 1
    _right_outline_width: int = 1
    _top_outline_width: int = 1
    _bottom_outline_width: int = 1

    _outline_color: str = "black"
    _left_outline_color: str = "black"
    _right_outline_color: str = "black"
    _top_outline_color: str = "black"
    _bottom_outline_color: str = "black"

    _fill: str = None
    _content:  BaseContainer = None
    _vertical_alignment = "top"
    _horizontal_alignment = "left"

    def __init__(self, fill=None, left_top=(0, 0), width=0, height=0):
        self._fill = fill
        self.pixels = Pixels(container=self)
        self.pixels.left_top = left_top
        self.pixels.width = width + self.left_outline_width + self.right_outline_width
        self.pixels.height = height
        self._update_pixels()

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, value):
        self._outline_color = value
        self.top_outline_color = value
        self.bottom_outline_color = value
        self.left_outline_color = value
        self.right_outline_color = value

    @property
    def left_outline_color(self):
        return self._left_outline_color

    @left_outline_color.setter
    def left_outline_color(self, value):
        self._left_outline_color = value
        self._outline_color = None

    @property
    def right_outline_color(self):
        return self._right_outline_color

    @right_outline_color.setter
    def right_outline_color(self, value):
        self._right_outline_color = value
        self._outline_color = None

    @property
    def top_outline_color(self):
        return self._top_outline_color

    @top_outline_color.setter
    def top_outline_color(self, value):
        self._top_outline_color = value
        self._outline_color = None

    @property
    def bottom_outline_color(self):
        return self._bottom_outline_color

    @bottom_outline_color.setter
    def bottom_outline_color(self, value):
        self._bottom_outline_color = value
        self._outline_color = None

    @property
    def outline_width(self):
        return self._outline_width

    @outline_width.setter
    def outline_width(self, value):
        self._outline_width = value
        self._left_outline_width = value
        self._right_outline_width = value
        self._top_outline_width = value
        self._bottom_outline_width = value
        self._update_pixels()

    @property
    def left_outline_width(self):
        return self._left_outline_width

    @left_outline_width.setter
    def left_outline_width(self, value):
        self._left_outline_width = value
        self._outline_width = None
        self._update_pixels()

    @property
    def right_outline_width(self):
        return self._right_outline_width

    @right_outline_width.setter
    def right_outline_width(self, value):
        self._right_outline_width = value
        self._outline_width = None
        self._update_pixels()

    @property
    def top_outline_width(self):
        return self._top_outline_width

    @top_outline_width.setter
    def top_outline_width(self, value):
        self._top_outline_width = value
        self._outline_width = None
        self._update_pixels()

    @property
    def bottom_outline_width(self):
        return self._bottom_outline_width

    @bottom_outline_width.setter
    def bottom_outline_width(self, value):
        self._bottom_outline_width = value
        self._outline_width = None
        self._update_pixels()

    @property
    def fill(self):
        return self._fill

    @fill.setter
    def fill(self, value):
        self._fill = value

    @property
    def vertical_alignment(self):
        return self._vertical_alignment

    @vertical_alignment.setter
    def vertical_alignment(self, value):
        self._vertical_alignment = value
        self._update_pixels()

    @property
    def horizontal_alignment(self):
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, value):
        self._horizontal_alignment = value
        self._update_pixels()

    def _update_width(self):
        self.pixels.width = max(self.pixels.width,
                                2 * self.pixels.padding + self.left_outline_width + self.right_outline_width)
        if self.content:
            self.pixels.width = max(self.pixels.width,
                                    self.content.pixels.width + 2 * self.pixels.padding + self.content.pixels.margin * 2 +
                                    self.left_outline_width + self.right_outline_width)

    def _update_height(self):
        self.pixels.height = max(self.pixels.height,
                                 2 * self.pixels.padding + self.top_outline_width + self.bottom_outline_width)
        if self.content:
            self.pixels.height = max(self.pixels.height,
                                     self.content.pixels.height + 2 * self.pixels.padding + self.content.pixels.margin * 2 +
                                     self.top_outline_width + self.bottom_outline_width)

    def draw_content(self, canvas):
        if self._content is not None:
            self._content.draw(canvas)

    def draw_outline(self, canvas):
        left_x = self.pixels.left_x
        right_x = self.pixels.right_x
        top_y = self.pixels.top_y
        bottom_y = self.pixels.bottom_y

        left_top = (left_x, top_y)
        right_top = (right_x, top_y)
        left_bottom = (left_x, bottom_y)
        right_bottom = (right_x, bottom_y)

        if self.top_outline_width:
            gap1 = (self.top_outline_width - 1) // 2
            gap2 = self.top_outline_width // 2
            canvas.line((left_x, top_y, right_x + gap2, top_y), fill=self._top_outline_color,
                        width=self._top_outline_width)

        if self.bottom_outline_width:
            gap1 = (self.bottom_outline_width - 1) // 2
            gap2 = self.bottom_outline_width // 2
            canvas.line((left_x, bottom_y, right_x, bottom_y),
                        fill=self._bottom_outline_color,
                        width=self._bottom_outline_width)

        if self.left_outline_width:
            gap1 = (self.left_outline_width - 1) // 2
            gap2 = self.left_outline_width // 2
            canvas.line((left_x, top_y - gap1, left_x, bottom_y + gap2), fill=self._left_outline_color,
                        width=self._left_outline_width)

        if self.right_outline_width:
            gap1 = (self.right_outline_width - 1) // 2
            gap2 = self.right_outline_width // 2
            canvas.line((right_x, top_y - gap1, right_x, bottom_y + gap2), fill=self._right_outline_color,
                        width=self._right_outline_width)

    def draw_inside(self, canvas):
        cords = (self.pixels.left_x, self.pixels.top_y, self.pixels.right_x, self.pixels.bottom_y)
        canvas.rectangle(cords,
                         fill=self._fill,
                         outline=None,
                         width=0)

    def draw(self, canvas):
        self.draw_inside(canvas)
        self.draw_outline(canvas)
        self.draw_content(canvas)

    def _changed(self, field):
        self._update_pixels()
        # if field == "padding":
        #     self._update_pixels()
        #
        # if field == "left_top":
        #     self._update_pixels()
        #
        # if field == "width":
        #     self._update_pixels()
        #
        # if field == "height":
        #     self._update_pixels()


    def _update_pixels(self):
        self._update_width()
        self._update_height()
        self._update_content()

    def squeeze(self):
        self.pixels.height = 0
        self.pixels.width = 0
        self._update_pixels()

    def _update_content(self):
        if not self.content:
            return



        if self._vertical_alignment == "top":
            self._content.pixels.left_top = self.pixels.left_x, self.pixels.top_y + self.pixels.padding + self.content.pixels.margin + self.top_outline_width

        if self._horizontal_alignment == "left":
            self._content.pixels.left_top = self.pixels.left_x + self.pixels.padding + self.content.pixels.margin + self.left_outline_width, self._content.pixels.top_y

        if self._horizontal_alignment == "center":
            center_x = self.pixels.center[0]
            self._content.pixels.center = center_x, self._content.pixels.center[1]

        if self._vertical_alignment == "center":
            center_y = self.pixels.center[1]
            self._content.pixels.center = self._content.pixels.center[0], center_y

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value: BaseContainer):
        self._content = value
        self._update_pixels()


if __name__ == "__main__":
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (300, 200), color="white")
    text = Text(value="Hello, world!", left_top=(10, 10))
    # text2 = Text(value="Hello, world!", left_top=(10, 10))
    container = Container(left_top=(10, 10), fill=None)
    container.outline_width = 0
    container._outline_color = "blue"
    container.content = text


    canvas = ImageDraw.Draw(image)
    left_x = 10
    right_x = 113
    top_y = 10
    bottom_y = 10
    red_width = 1
    canvas.line((left_x, top_y + (red_width - 1) // 2, right_x, top_y + (red_width - 1) // 2), fill="red",
                width=red_width)
    # canvas.line((left_x, top_y+1, right_x, top_y+1), fill="black", width=1)
    # canvas.line((left_x, top_y+2, right_x, top_y+2), fill="black", width=1)
    # canvas.line((left_x, top_y+3, right_x, top_y+3), fill="black", width=1)
    # container.left_outline_width = 1
    # container.right_outline_width = 1
    container.outline_width = 2
    container.outline_color = "blue"
    # container.left_outline_color = "red"
    # container.bottom_outline_width = 0
    container.draw(canvas)
    print(container.pixels.width)
    print(container.pixels.height)
    # print(container.pixels.left_top)
    # print(container.pixels.right_bottom)
    print(text.pixels.width)
    print(text.pixels.height)
    # container.vertical_alignment = "center"
    # canvas.line((left_x, top_y, right_x, top_y), fill="red", width=1)
    # canvas.line((left_x, 50, right_x, 50), fill="red", width=1)
    # container2.draw(canvas)

    image.save("text_image.png")
    image.show()
