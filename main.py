import os

from openai import OpenAI


def main() -> None:
	client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
	response = client.responses.create(
		model="gpt-4o-mini",
		input="Say hello in one sentence.",
	)
	print(response.output_text)


if __name__ == "__main__":
	main()
