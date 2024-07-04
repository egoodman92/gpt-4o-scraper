import os
import sys
import base64
import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

if len(sys.argv) < 2:
    print("Usage: python3 2_image_dir_to_gpt4.py <ARTICLE_DIR>")
    sys.exit(1)

ARTICLE_DIR = sys.argv[1]

api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not set")

GPT4O_TOKEN_COSTS = {"million_tokens_in": 5, "million_tokens_out": 15}

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function for natural sorting
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in 
re.split('([0-9]+)', s)]

# Path to your image directory
images_dir = os.path.join(ARTICLE_DIR, 'images')
transcriptions_dir = os.path.join(ARTICLE_DIR, 'transcriptions')

# Create directory for transcriptions if it doesn't exist
if not os.path.exists(transcriptions_dir):
    os.makedirs(transcriptions_dir)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Get a sorted list of image files in the directory
image_files = sorted([file for file in os.listdir(images_dir) if 
file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))], 
key=natural_sort_key)

def process_batch(batch, batch_index, retries=10):
    content = [
        {
            "type": "text",
            "text": """Please do OCR on these images to piece together a fragment of an 
article. Only return the article text, no additional chattiness. Do not include 
anything in the article header or footers. Put titles, headers, and text in the 
appropriate HTML tags.""",
        }
    ]
    
    for image_file in batch:
        image_path = os.path.join(images_dir, image_file)
        base64_image = encode_image(image_path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "max_tokens": 300
    }
    
    attempt = 0
    while attempt < retries:
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", 
headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()

            # Get the transcribed text from the response
            if response_json.get("choices"):
                transcribed_text = response_json["choices"][0]["message"]["content"]
            else:
                transcribed_text = "No transcription available."

            # Write the transcribed text to a file
            transcribed_file_path = os.path.join(transcriptions_dir, 
f"transcribed_{batch_index}.txt")
            with open(transcribed_file_path, "w") as transcribed_file:
                transcribed_file.write(transcribed_text)
            
            # Print the response
            print(f"Response for batch {batch_index + 1}:")
            print(response_json)
            print(f"Transcribed text saved to {transcribed_file_path}")
            print("\n")
            
            # Print the number of input and output tokens used
            if 'usage' in response_json:
                input_tokens = response_json['usage']['prompt_tokens']
                output_tokens = response_json['usage']['completion_tokens']
                total_tokens = response_json['usage']['total_tokens']
                print(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total tokens: {total_tokens}")
                print(f"Cost of call is $", input_tokens/(10**6)*GPT4O_TOKEN_COSTS['million_tokens_in'] + output_tokens/(10**6)*GPT4O_TOKEN_COSTS['million_tokens_out'])
            else:
                print("No token usage information available.")
            print("\n")
            return

        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"Attempt {attempt} failed for batch {batch_index + 1}: {e}")
            time.sleep(2)  # Wait before retrying
    
    print(f"Batch processing failed for batch {batch_index + 1} after {retries} attempts.")

# Process images in batches of 1 in parallel
batch_size = 1
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for i in range(0, len(image_files), batch_size):
        batch = image_files[i:i + batch_size]
        futures.append(executor.submit(process_batch, batch, i//batch_size))
    
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Batch processing generated an exception: {e}. This is for batch {i}")
