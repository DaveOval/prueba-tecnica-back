from PIL import Image, ImageFilter
import os


def proccess_image(file_path: str, output_path:str, transformations: list):
    image = Image.open(file_path)

    if "grayscale" in transformations:
        image

    if "blur" in transformations:
        image = image.filter(ImageFilter.BLUR)

    if "thumbnail" in transformations:
        image.thumbnail((100, 100))

    if "rotate" in transformations:
        image = image.rotate(90)

    if "resize" in transformations:
        image = image.resize((800, 600))

    if "flip" in transformations:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    
    if "crop" in transformations:
        image = image.crop((100, 100, 400, 400))

    image.save(output_path)