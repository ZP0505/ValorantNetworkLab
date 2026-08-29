from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SIZE = 512
OUT = Path(__file__).with_name('app.ico')


def polygon(draw, pts, fill, outline=None, width=1):
    draw.polygon(pts, fill=fill)
    if outline:
        draw.line(pts + [pts[0]], fill=outline, width=width, joint='curve')


def build_icon():
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    outer = [(256, 36), (430, 136), (430, 376), (256, 476), (82, 376), (82, 136)]
    inner = [(256, 66), (404, 151), (404, 361), (256, 446), (108, 361), (108, 151)]

    gd.line(outer + [outer[0]], fill=(55, 226, 239, 175), width=18, joint='curve')
    gd.ellipse((172, 172, 340, 340), outline=(44, 223, 240, 150), width=12)
    gd.line((256, 118, 256, 394), fill=(44, 223, 240, 155), width=8)
    gd.line((118, 256, 394, 256), fill=(44, 223, 240, 155), width=8)
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(glow)

    d = ImageDraw.Draw(img)
    polygon(d, outer, (20, 29, 35, 255), (176, 201, 212, 255), 10)
    polygon(d, inner, (8, 20, 27, 255), (32, 218, 232, 255), 7)

    d.ellipse((154, 154, 358, 358), fill=(9, 42, 58, 255), outline=(42, 220, 238, 255), width=5)
    d.arc((180, 154, 332, 358), 70, 290, fill=(41, 141, 174, 210), width=3)
    d.arc((180, 154, 332, 358), 250, 110, fill=(41, 141, 174, 210), width=3)
    d.arc((154, 200, 358, 312), 0, 360, fill=(41, 141, 174, 180), width=3)
    d.line((256, 128, 256, 384), fill=(46, 226, 241, 245), width=6)
    d.line((128, 256, 384, 256), fill=(46, 226, 241, 245), width=6)

    left = [(132, 180), (226, 228), (256, 382), (201, 310), (166, 230)]
    right = [(380, 180), (286, 228), (256, 382), (311, 310), (346, 230)]
    polygon(d, left, (218, 232, 238, 255), (72, 98, 110, 255), 4)
    polygon(d, right, (226, 235, 239, 255), (72, 98, 110, 255), 4)
    polygon(d, [(154, 205), (218, 239), (239, 328), (201, 286)], (34, 66, 80, 255))
    polygon(d, [(358, 205), (294, 239), (273, 328), (311, 286)], (44, 47, 58, 255))

    d.line((256, 258, 256, 370), fill=(255, 87, 72, 255), width=7)
    d.ellipse((234, 234, 278, 278), fill=(255, 97, 69, 255), outline=(255, 183, 109, 255), width=4)
    d.ellipse((246, 246, 266, 266), fill=(255, 238, 174, 255))

    for x, y in [(187, 203), (322, 198), (186, 319), (330, 315)]:
        d.ellipse((x-7, y-7, x+7, y+7), fill=(94, 238, 244, 255), outline=(210, 255, 255, 255), width=2)

    d.line((340, 320, 360, 300, 378, 326, 398, 286), fill=(255, 106, 69, 255), width=7, joint='curve')
    d.arc((360, 228, 430, 300), 290, 55, fill=(255, 118, 67, 255), width=6)
    d.arc((370, 218, 448, 310), 294, 48, fill=(255, 118, 67, 210), width=5)

    img = img.resize((256, 256), Image.Resampling.LANCZOS)
    img.save(OUT, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f'Generated: {OUT}')


if __name__ == '__main__':
    build_icon()
