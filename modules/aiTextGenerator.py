import openai

class AiTextGenerator:
    def __init__(self, api_key: str, model: str = "gpt-5"):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )
        return response.output_text


