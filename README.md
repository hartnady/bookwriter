# bookwriter

- Python GPT Book Writer
- Author: Initially created by Mark Hartnady (http://hartnady.com) on 22 Feb 2023

## Setup

- Install the required modules: `pip install -r requirements.txt`
- create a .env file `touch .env` and add the line `OPENAI_API_KEY=[your OpenAI key]`
  - You can get an OpenAI key from (https://platform.openai.com/signup)

## How to use it

Think of a book title, a short summary of the book, and who the author is.

Then run the script `python3 run.py`

The result will be a text file, a JSON file, and a formatted MS Word document containing your book's contents.
