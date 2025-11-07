import os
from django.core.management.base import BaseCommand
from django.conf import settings
from searchapp.models import ImageItem
from PIL import Image
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path  # NEW import

class Command(BaseCommand):
    help = 'Index images and PDFs under MEDIA_ROOT (extract text and pages)'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Root path to images/PDFs (default MEDIA_ROOT)')
        parser.add_argument('--poppler', type=str, help='Path to poppler bin folder (for PDFs)')

    def handle(self, *args, **options):
        root = options.get('path') or settings.MEDIA_ROOT
        root = os.path.abspath(root)
        poppler_path = options.get('poppler')  # required for PDF conversion
        if not os.path.isdir(root):
            self.stderr.write(self.style.ERROR(f'Path does not exist: {root}'))
            return

        # Configure tesseract
        if hasattr(settings, 'TESSERACT_CMD') and settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

        allowed_image = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        allowed_pdf = ('.pdf',)
        indexed = 0

        for dirpath, dirnames, filenames in os.walk(root):
            for fname in filenames:
                fullpath = os.path.join(dirpath, fname)
                rel = os.path.relpath(fullpath, root).replace('\\', '/')

                # ---------- PDF handling ----------
                if fname.lower().endswith(allowed_pdf):
                    try:
                        pages = convert_from_path(fullpath, dpi=300, poppler_path=poppler_path)
                        for i, page in enumerate(pages, start=1):
                            arr = np.array(page.convert('RGB'))
                            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                            text = pytesseract.image_to_string(thresh, lang='eng').strip()
                            # store each page as separate entry
                            ImageItem.objects.update_or_create(
                                file_relative_path=f"{rel}#page{i}",
                                defaults={'filename': fname, 'extracted_text': text, 'page_number': i}
                            )
                        indexed += len(pages)
                        self.stdout.write(f"Indexed PDF: {rel} ({len(pages)} pages)")
                    except Exception as e:
                        self.stderr.write(f"Failed PDF {fullpath} : {e}")
                    continue

                # ---------- Normal image ----------
                if fname.lower().endswith(allowed_image):
                    try:
                        pil_img = Image.open(fullpath).convert('RGB')
                        arr = np.array(pil_img)
                        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                        h, w = gray.shape
                        if max(h, w) < 800:
                            gray = cv2.resize(gray, (w*2, h*2), interpolation=cv2.INTER_LINEAR)
                        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        text = pytesseract.image_to_string(thresh, lang='eng').strip()

                        ImageItem.objects.update_or_create(
                            file_relative_path=rel,
                            defaults={'filename': fname, 'extracted_text': text, 'page_number': 0}
                        )
                        indexed += 1
                        self.stdout.write(f"Indexed image: {rel} (chars {len(text)})")
                    except Exception as e:
                        self.stderr.write(f"Failed image {fullpath} : {e}")
        self.stdout.write(self.style.SUCCESS(f"Indexing complete. Total indexed: {indexed}"))
