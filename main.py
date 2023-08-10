import openai
import re
import time

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from keys import open_ai_key


app = Flask(__name__)

openai.api_key = open_ai_key

def generate_custom_keywords(keyword):
    try:
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads keywords."},
            {"role": "user", "content": f"Based on this keyword, generate 20 unique Google Ads keywords:\n\n{keywords_input}" "Insert a line break after every keyword."}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.8,
        )

        keywords = response["choices"][0]["message"]["content"].replace("-","").lower().strip().split("\n")[:20]

        return keywords  # Return the list of keywords instead of the formatted

    except openai.error.APIError as e:
        print(e)
    except openai.error.ServiceUnavailableError as e:
        print(e)
        time.sleep(5)


def remove_numbers(text_list):
    try:
        cleaned_list = [re.sub(r'\d', '', text, count=2) for text in text_list]
        cleaned_list = [text.lstrip('.') for text in cleaned_list]
        cleaned_list = [text.strip() for text in cleaned_list]
        cleaned_list = [text.replace("'", "") for text in cleaned_list]
        cleaned_list = [text.replace('"', "") for text in cleaned_list]
        cleaned_list = [text.replace(":", "") for text in cleaned_list]
        cleaned_list = [text.replace("-", "") for text in cleaned_list]
        cleaned_list = [text.replace("(", "") for text in cleaned_list]
        cleaned_list = [text.replace(")", "") for text in cleaned_list]
        cleaned_list = [text.replace("  ", " ") for text in cleaned_list]
        cleaned_list = [text.replace("&", "And") for text in cleaned_list]
    except TypeError as e:
        print(e)
        return text_list
    return cleaned_list


@app.route('/', methods=['GET', 'POST'])
def index():
    app.logger.info('Processing request for the root path')
    return render_template('index.html')


@app.route('/custom_keywords', methods=['GET'])
def custom_keywords():
    keyword = request.args.get('keyword', '')
    if keyword:
        custom_keywords = remove_numbers(generate_custom_keywords(keyword))
        return jsonify(keywords=custom_keywords)
    else:
        return jsonify(error="Please enter a keyword."), 400


if __name__ == '__main__':
    app.run(debug=True)
