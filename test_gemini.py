from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input="Reply with exactly: Gemini connection successful."
)

print(interaction.output_text)