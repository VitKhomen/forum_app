import hashlib
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

# ====================== ПАЛІТРА ======================
PALETTE = [
    ('#CECBF6', '#3C3489'),
    ('#9FE1CB', '#085041'),
    ('#F5C4B3', '#712B13'),
    ('#F4C0D1', '#72243E'),
    ('#B5D4F4', '#0C447C'),
    ('#C0DD97', '#27500A'),
    ('#FAC775', '#633806'),
    ('#F7C1C1', '#791F1F'),
    ('#5DCAA5', '#0F6E56'),
    ('#AFA9EC', '#534AB7'),
]


# ====================== ДОПОМІЖНІ ФУНКЦІЇ ======================
def get_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper() if name else "??"


def get_avatar_color(name: str):
    h = int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16)
    return PALETTE[h % len(PALETTE)]


# ====================== ГЕНЕРАЦІЯ АВАТАРКИ ======================
def generate_avatar_png(name: str, size: int = 200) -> bytes:
    initials = get_initials(name)
    bg, fg = get_avatar_color(name)

    img = Image.new('RGB', (size, size), color=bg)
    draw = ImageDraw.Draw(img)

    font_size = int(size * 0.42)

    # Спроба завантажити нормальний шрифт
    try:
        font = ImageFont.truetype("arial.ttf", font_size)           # Windows
    except:
        try:
            font = ImageFont.truetype(
                "DejaVuSans-Bold.ttf", font_size)  # Linux
        except:
            try:
                font = ImageFont.truetype("LiberationSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()

    # Центрування тексту
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 3   # невелике коригування по висоті

    draw.text((x, y), initials, fill=fg, font=font)

    # Зберігаємо в пам'ять
    buffer = BytesIO()
    img.save(buffer, format='PNG', optimize=True, quality=95)
    buffer.seek(0)

    return buffer.getvalue()


def make_avatar_file(name: str) -> ContentFile:
    """Повертає готовий файл для присвоєння в ImageField/FileField"""
    content = generate_avatar_png(name)
    filename = f"avatar_{hashlib.md5(name.encode()).hexdigest()[:12]}.png"

    return ContentFile(content, name=filename)
