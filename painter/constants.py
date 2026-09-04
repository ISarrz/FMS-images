import os

from PIL import Image, ImageDraw, ImageFont
# from modules.images_updater.style import *
# from .style import *
# from .cell import TextStyle

colors = {
    'white': '#FFFFFF',
    'black': '#000000',
    'red': '#FF0000',
    'gray': '#808080',
    "yellow": "#FFFF00",
    'discord1': '#424549',
    'discord2': '#36393e',
    'discord3': '#282b30',
    'discord4': '#1e2124'
}


im = Image.new('RGB', (500, 500), colors['white'])
draw = ImageDraw.Draw(im)
