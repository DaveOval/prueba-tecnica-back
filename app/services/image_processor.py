from PIL import Image, ImageFilter, ImageEnhance


def proccess_image(file_path: str, output_path: str, filter_name: str):
    image = Image.open(file_path)

    if filter_name == "grayscale":
        image = image.convert("L")
    
    elif filter_name == "blur":
        image = image.filter(ImageFilter.BLUR)
    
    elif filter_name == "thumbnail":
        image.thumbnail((100, 100))
    
    elif filter_name == "sepia":
        # Convert to grayscale first
        image = image.convert("L")
        # Create sepia filter
        sepia_filter = Image.new("RGB", image.size, (255, 240, 192))
        # Convert grayscale to RGB for blending
        image = image.convert("RGB")
        # Blend the images
        image = Image.blend(image, sepia_filter, 0.5)
    
    elif filter_name == "invert":
        image = Image.eval(image, lambda x: 255 - x)
    
    elif filter_name == "brightness":
        # Always increase brightness by 50%
        image = ImageEnhance.Brightness(image).enhance(1.5)

    image.save(output_path)