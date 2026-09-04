from typing import List

from painter.containers.pixels import Pixels
from painter.containers.base_container import BaseContainer
import os
from PIL import Image, ImageDraw, ImageFont

fonts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")


def get_font(name, size=12):
    name = "_".join(name.split()) + ".ttf"
    path = os.path.join(fonts_path, name)

    return ImageFont.truetype(path, size=size)


BASE_FONT = get_font("Roboto Medium Regular", size=20)


class Text(BaseContainer):
    _font: ImageFont
    _fill: str
    _line_space: int = 3
    _lines: List
    _horizontal_alignment: str = "left"

    def __init__(self, value="", fill="black", font="Roboto Medium Regular", size=20, left_top=(0, 0)):
        self._font = get_font(font, size=size)
        self._size = size
        self._lines = value.split("\n")
        self._fill = fill
        self.pixels = Pixels(container=self)

        self._update_pixels()
        self.pixels.left_top = left_top

    def _update_pixels(self):
        width = 0
        height = 0
        for line in self._lines:
            pass
            bbox = self._font.getbbox(line)
            width = max(width, bbox[2])
            height += bbox[3]

        height += self._line_space * (len(self._lines) - 1)

        self.pixels.width = width
        self.pixels.height = height

    @property
    def lines(self):
        return self._lines

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def size(self):
        return self._font.size

    @size.setter
    def size(self, value):
        self._font = ImageFont.truetype(self._font.path, size=value)
        self._update_pixels()

    @property
    def horizontal_alignment(self):
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, value: str):
        self._horizontal_alignment = value

    def draw(self, canvas):
        cur_pos = self.pixels.left_top
        for line in self._lines:
            bbox = self._font.getbbox(line)
            line_width = bbox[2]
            line_height = bbox[3]
            if self._horizontal_alignment == "left":
                pass

            if self._horizontal_alignment == "center":
                line_left_x = self.pixels.center_x - line_width // 2
                cur_pos = (line_left_x, cur_pos[1])

            canvas.text(cur_pos, text=line, fill=self._fill, font=self._font)
            cur_pos = (self.pixels.left_x, cur_pos[1] + line_height + self._line_space)


if __name__ == "__main__":
    pass
    from PIL import Image, ImageDraw, ImageFont

    # Создаем пустое белое изображение
    image = Image.new("RGB", (300, 100), color="white")

    # Объект для рисования
    canvas = ImageDraw.Draw(image)

    left_top = (0, 0)
    fill_color = "black"

    text = Text(value="привет", fill=fill_color, left_top=left_top)
    text.size = 12
    print(text.pixels.center)
    print(text.size)
    text.draw(canvas)
    image.save("text_image.png")
    image.show()
