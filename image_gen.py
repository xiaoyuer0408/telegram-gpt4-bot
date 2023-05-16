from PIL import Image, ImageDraw, ImageFont

# 图片生成函数
def generate_image(text):
    image = Image.new("RGB", (500, 200), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    image.save("generated_image.png")
