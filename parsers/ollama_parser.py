import requests
import base64
import json
import time
from pathlib import Path
from parsers.base_parser import BaseVLMParser


class OllamaParser(BaseVLMParser):
    """
    VLM parser using Ollama (Llama 3.2 Vision) running locally.
    To swap for GPT-4o or Claude later — create a new class
    inheriting BaseVLMParser and implement the same two methods.
    """

    def __init__(self, model: str = "llama3.2-vision", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def health_check(self) -> bool:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=5)
            return r.status_code == 200
        except:
            return False

    def _encode_image(self, image_path: str) -> str:
        from PIL import Image
        import io
        img = Image.open(image_path)
        img.thumbnail((512, 512), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def extract_takeoff(self, image_path: str, context: str = "") -> dict:
        start = time.time()

        prompt = """List the construction materials and quantities from this blueprint image.
Return ONLY this JSON, no other text:
{"line_items":[{"material":"name","quantity":0.0,"unit":"SF","location":"area","confidence":0.8}]}
Extract every material you can see. Use null for unknown values."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [self._encode_image(image_path)],
            "stream": False,
            "options": {
                "num_predict": 2048,
                "temperature": 0.1
                        }}

        try:
            r = requests.post(f"{self.host}/api/generate", json=payload, timeout=300)
            raw = r.json().get("response", "")
            print("RAW RESPONSE:", raw[:500])

            parsed = self._parse_json_response(raw)
            line_items = parsed.get("line_items", [])

            standardized = [
                self.standard_line_item(
                    material=item.get("material"),
                    quantity=item.get("quantity"),
                    unit=item.get("unit"),
                    location=item.get("location"),
                    confidence=item.get("confidence", 0.7),
                    source="ollama_vlm"
                )
                for item in line_items
            ]

            result = self.standard_schema(
                line_items=standardized,
                parser_name=f"ollama_{self.model}",
                image_path=image_path,
                runtime_ms=int((time.time() - start) * 1000)
            )
            result["drawing_type"] = parsed.get("drawing_type")
            result["notes"] = parsed.get("notes")
            return result

        except Exception as e:
            return self.standard_schema(
                line_items=[],
                parser_name=f"ollama_{self.model}",
                image_path=image_path,
                runtime_ms=int((time.time() - start) * 1000)
            ) | {"error": str(e)}

    def _parse_json_response(self, raw: str) -> dict:
        raw = raw.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(raw)
        except:
            try:
                start = raw.find("{")
                if start == -1:
                    return {"line_items": [], "notes": "no JSON found"}
                depth = 0
                for i, ch in enumerate(raw[start:], start):
                    if ch == "{": depth += 1
                    if ch == "}": depth -= 1
                    if depth == 0:
                        return json.loads(raw[start:i+1])
            except:
                pass
            return {"line_items": [], "notes": f"parse error: {raw[:200]}"}


if __name__ == "__main__":
    parser = OllamaParser()

    print("Checking Ollama is running...")
    if not parser.health_check():
        print("Ollama not running. Start it with: ollama serve")
        exit(1)

    print("Running on blueprint page 3...")
    result = parser.extract_takeoff("data/images/sample1_page3.png")
    print(json.dumps(result, indent=2))
    print(f"\n✓ Extracted {len(result['line_items'])} items in {result['runtime_ms']}ms")
