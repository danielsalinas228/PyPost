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

# Load prompt from template file
prompt_template_path = Path("../templates/email_subject_prompt_template.txt")
with open(prompt_template_path, "r", encoding="utf-8") as f:
    prompt = f.read().strip()

response = generator.generate(prompt)

print("Prompt:", prompt)
print("AI Generated Response:", response)