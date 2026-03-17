import fitz
import os
from pathlib import Path

class PDFToImages:
    def __init__(self, dpi=600):
        self.dpi = dpi

    def convert(self, pdf_path: str, output_dir: str = "data/images") -> list:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        pdf_name = Path(pdf_path).stem
        doc = fitz.open(pdf_path)
        image_paths = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            image_path = f"{output_dir}/{pdf_name}_page{page_num + 1}.png"
            pix.save(image_path)
            image_paths.append(image_path)
            print(f"✓ Page {page_num + 1} → {image_path}")

        doc.close()
        return image_paths


if __name__ == "__main__":
    converter = PDFToImages(dpi=600)
    paths = converter.convert("data/samples/sample1.pdf")
    print(f"\n✓ {len(paths)} pages converted")
    for p in paths:
        print(f"  {p}")