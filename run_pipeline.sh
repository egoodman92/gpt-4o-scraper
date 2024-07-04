#!/bin/bash

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <NYT_URL>"
    exit 1
fi

NYT_URL=$1

# Extract a clean name from the URL
ARTICLE_NAME=$(echo "$NYT_URL" | sed 's/https\?:\/\///' | sed 's/[^a-zA-Z0-9]/_/g')

# Create a directory for the article
ARTICLE_DIR="./article_$ARTICLE_NAME"
mkdir -p "$ARTICLE_DIR"

# Clear out the directories
echo "Clearing out the directories..."
rm -rf "$ARTICLE_DIR/images"/*
rm -rf "$ARTICLE_DIR/transcriptions"/*

# Run the first Python script with the URL and the article directory
echo "Running 1_gpt-web-scraper.py with URL: $NYT_URL $ARTICLE_DIR"
python3 1_gpt-web-scraper.py "$NYT_URL" "$ARTICLE_DIR"

# Run the second Python script to transcribe images
echo "Running 2_image_dir_to_gpt4.py $ARTICLE_DIR"
python3 2_image_dir_to_gpt4.py "$ARTICLE_DIR"

# Run the third Python script to combine transcriptions
echo "Running 3_combine_transcriptions.py $ARTICLE_DIR"
python3 3_combine_transcriptions.py "$ARTICLE_DIR"

echo "Pipeline completed for $NYT_URL. The final article is saved in 
$ARTICLE_DIR/final.txt"
