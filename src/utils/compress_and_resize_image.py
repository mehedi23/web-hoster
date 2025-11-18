# shop/utils.py (বা যেকোনো জায়গায়)
import os
from PIL import Image
from io import BytesIO
from django.core.files import File
import logging

logger = logging.getLogger(__name__)

def compress_and_resize_image(image_path, max_size=(200, 200), max_file_size_kb=30):
    if not os.path.exists(image_path):
        return

    try:
        with Image.open(image_path) as img:
            # PNG/JPEG/WEBP সাপোর্ট
            img_format = img.format if img.format else 'JPEG'
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # রিসাইজ (aspect ratio রেখে)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # কম্প্রেশন লুপ (30KB এর নিচে আনতে)
            quality = 95
            temp_path = image_path + '.temp.jpg'

            while quality > 10:
                with BytesIO() as buffer:
                    img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    file_size_kb = len(buffer.getvalue()) / 1024

                    if file_size_kb <= max_file_size_kb:
                        # সফল! ফাইল ওভাররাইট করো
                        with open(temp_path, 'wb') as f:
                            f.write(buffer.getvalue())
                        break
                quality -= 5
            else:
                # খুব ছোট হলে সর্বনিম্ন কোয়ালিটি
                with BytesIO() as buffer:
                    img.save(buffer, format='JPEG', quality=10, optimize=True)
                    with open(temp_path, 'wb') as f:
                        f.write(buffer.getvalue())

            # মূল ফাইল রিপ্লেস
            os.replace(temp_path, image_path)

    except Exception as e:
        logger.error(f"Image compression failed: {e}")