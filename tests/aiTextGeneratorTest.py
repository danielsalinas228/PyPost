import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from modules.aiTextGenerator import AiTextGenerator

# Load API key from a JSON file
api_key_path = Path("../Secrets/openApi_key.json")
with open(api_key_path, "r", encoding="utf-8") as f:
    api_data = json.load(f)
    api_key = api_data["api_key"]

generator = AiTextGenerator(api_key=api_key, model="gpt-5-mini")

prompt = "Write one creative email subject line in Spanish about receiving a letter, with one or two emojis. Output only the line."
response = generator.generate(prompt)

print("Prompt:", prompt)
print("AI Generated Response:", response)