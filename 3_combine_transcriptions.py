import os
import sys
import requests

if len(sys.argv) < 2:
    print("Usage: python3 3_combine_transcriptions.py <ARTICLE_DIR>")
    sys.exit(1)

ARTICLE_DIR = sys.argv[1]

# OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Path to your transcriptions directory
transcriptions_dir = os.path.join(ARTICLE_DIR, 'transcriptions')
output_dir = ARTICLE_DIR

# Create directory for the final article if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Read and concatenate all transcribed text files
transcriptions = ""
for file in sorted(os.listdir(transcriptions_dir)):
    if file.lower().endswith('.txt'):
        with open(os.path.join(transcriptions_dir, file), "r") as f:
            transcriptions += f.read() + "\n\n"

print("Got transcriptions", transcriptions)

# Define the content to be sent to the OpenAI API
content = [
    {
        "role": "user",
        "content": transcriptions
    },
    {
        "role": "user",
        "content": """Please synthesize the above transcriptions into a coherent single 
article. Include every single word that you are presented with, we don't want any 
summarization at all. However, make sure the title is only included once."""
    }
]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4o",
    "messages": content,
    "max_tokens": 4096
}

response = requests.post("https://api.openai.com/v1/chat/completions", 
headers=headers, json=payload)

# Get the synthesized article from the response
response_json = response.json()
if response_json.get("choices"):
    synthesized_article = response_json["choices"][0]["message"]["content"]
else:
    synthesized_article = "No article generated."

# Write the synthesized article to a file
output_file_path = os.path.join(output_dir, "scraped_article.html")
with open(output_file_path, "w") as output_file:
    output_file.write(synthesized_article)

# Print the response
print("Synthesized article saved to", output_file_path)
