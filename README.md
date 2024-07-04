# GPT-4o Scraper

This repository contains a pipeline for scraping articles websites (we do the The New York Times), processing the images, transcribing the text using GPT-4o, and combining the 
transcriptions into 
a single coherent article.

## Setup

### Prerequisites

- Python 3.x
- Chrome browser
- ChromeDriver (compatible with your Chrome browser version)

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/egoodman92/gpt-4o-scraper.git
    cd gpt-4o-scraper
    ```

2. **Create a virtual environment and activate it**:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set the OpenAI API key as an environment variable**:
    ```sh
    export OPENAI_API_KEY="your_openai_api_key_here"
    ```

## Usage

### Running the Pipeline

To run the entire pipeline, use the `run_pipeline.sh` script with the URL of the New York Times article you want to scrape:

```sh
./run_pipeline.sh "https://www.nytimes.com/article/how-to-grill-a-hot-dog.html"
```
