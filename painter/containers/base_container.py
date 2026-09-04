from painter.containers.pixels import Pixels
from painter.containers.simple_container import SimpleContainer


class BaseContainer(SimpleContainer):
    pixels: Pixels

    def draw(self, canvas):
        pass
