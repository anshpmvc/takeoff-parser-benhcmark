import fitz
import pdfplumber
import json
import time
import uuid
from datetime import datetime

class PyMuPDFParser:
    def __init__(self):
        self.parser_name = "pymupdf"
        self.parser_version = "1.0"

    def parse(self, pdf_path):
        start_time = time.time()
        line_items = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row:
                            continue
                        description = self._find_field(row, [2, 3, 4])
                        quantity = self._parse_number(self._find_field(row, [5, 6]))
                        unit = self._find_field(row, [6, 7])

                        if description and len(description) > 3:
                            line_items.append({
                                "material": description.strip(),
                                "quantity": quantity,
                                "unit": unit.strip() if unit else None,
                                "location": f"page_{page_num + 1}",
                                "confidence": 1.0,
                                "parser": self.parser_name
                            })

        runtime = int((time.time() - start_time) * 1000)

        return {
            "run_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "parser": self.parser_name,
            "parser_version": self.parser_version,
            "sample_id": pdf_path.split("/")[-1],
            "runtime_ms": runtime,
            "metadata": {
                "pages": len(fitz.open(pdf_path)),
                "extraction_method": "table_extraction"
            },
            "line_items": line_items
        }

    def _find_field(self, row, indices):
        for i in indices:
            if i < len(row) and row[i]:
                return str(row[i])
        return None

    def _parse_number(self, value):
        if not value:
            return None
        try:
            return float(str(value).replace(",", "").strip())
        except:
            return None


if __name__ == "__main__":
    parser = PyMuPDFParser()
    result = parser.parse("data/samples/sample1.pdf")
    print(json.dumps(result, indent=2))
    print(f"\n✓ Extracted {len(result['line_items'])} line items in {result['runtime_ms']}ms")

