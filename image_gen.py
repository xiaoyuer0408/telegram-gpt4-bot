from PIL import Image, ImageDraw, ImageFont

def generate_image(text, output_filename="generated_image.png", font_file="arial.ttf", image_size=(500, 200)):
    """
    生成包含给定文本的图像
    参数：
        text - 要在图像上显示的文本
        output_filename - 可选参数，生成图像的文件名，默认为 "generated_image.png"
        font_file - 可选参数，字体文件名，默认为 "arial.ttf"
        image_size - 可选参数，生成图像的尺寸，默认为 (500, 200)
    """
    image = Image.new("RGB", image_size, (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(font_file, 20)
    except IOError:
        print(f"Font file {font_file} not found. Using default font.")
        font = ImageFont.load_default()

    draw.text((10, 10), text, fill=(0, 0, 0), font=font)

    with open(output_filename, "wb") as f:
        image.save(f)
