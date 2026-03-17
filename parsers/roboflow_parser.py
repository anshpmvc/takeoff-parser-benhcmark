import time
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
from parsers.base_parser import BaseVLMParser

load_dotenv()

class RoboflowParser(BaseVLMParser):

    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=os.getenv("ROBOFLOW_API_KEY")
        )
        self.models = [
            "architectural-floor-plan/1"
        ]

    def health_check(self) -> bool:
        return bool(os.getenv("ROBOFLOW_API_KEY"))

    def extract_takeoff(self, image_path: str, context: str = "") -> dict:
        start = time.time()
        all_items = []

        for model_id in self.models:
            try:
                result = self.client.infer(image_path, model_id=model_id)
                for pred in result.get("predictions", []):
                    all_items.append(self.standard_line_item(
                        material=pred.get("class", "unknown"),
                        quantity=None,
                        unit=None,
                        location=f"x:{pred.get('x'):.0f} y:{pred.get('y'):.0f}",
                        confidence=round(pred.get("confidence", 0), 2),
                        source=f"roboflow_{model_id}"
                    ))
            except Exception as e:
                print(f"Model {model_id} error: {e}")

        return self.standard_schema(
            line_items=all_items,
            parser_name="roboflow",
            image_path=image_path,
            runtime_ms=int((time.time() - start) * 1000)
        )


if __name__ == "__main__":
    parser = RoboflowParser()
    result = parser.extract_takeoff("data/images/sample1_page3.png")
    print(json.dumps(result, indent=2))
    print(f"\n✓ {len(result['line_items'])} items in {result['runtime_ms']}ms")
