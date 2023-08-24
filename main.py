import openai
import re
import time

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from keys import open_ai_key
from models import Keyword
from spyFuAPI import get_keyword_data


app = Flask(__name__)

openai.api_key = open_ai_key

def generate_custom_keywords(keyword):
    try:
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads keywords."},
            {"role": "user", "content": f"Based on this keyword, generate 20 unique Google Ads keywords:\n\n{keywords_input}" 
                                        "Insert a line break after every keyword and return as a numbered list."}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.8,
        )

        keywords = response["choices"][0]["message"]["content"].lower().lstrip().strip().split("\n")[:20]

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


def kw_obj_constructor(string): #TODO Handle a scenario in which the SpyFu database does not return a result.
    kw_objs = []
    count = 1
    kw_data = get_keyword_data(string) # There is a bug here that does not always get 21 results.
    print(kw_data)
    for result in kw_data["results"]:
        print(result)
        keyword = result['keyword']
        search_volume = result['searchVolume']
        clicks = result['totalMonthlyClicks']
        kw = Keyword(count, keyword, search_volume, clicks)
        kw_objs.append(kw)
        count += 1
    return kw_objs


@app.route('/', methods=['GET', 'POST'])
def index():
    app.logger.info('Processing request for the root path')
    return render_template('index.html')


@app.route('/custom_keywords', methods=['GET'])
def custom_keywords():
    print("Button Clicked! Generating Keywords...")
    keyword = request.args.get('keyword', '')
    if keyword:
        custom_keywords = generate_custom_keywords(keyword)
        cleaned_list = [keyword]
        for item in custom_keywords:
            try:
                cleaned_item = item.split(" ", 1)[1]  # Split at the first space
                cleaned_list.append(cleaned_item)
            except IndexError:  # If split fails, keep the original item
                cleaned_list.append(item)
        list_as_str = ", ".join(cleaned_list)  # Converts list to string for API query.
        print(len(list_as_str))
        kw_objects = kw_obj_constructor(list_as_str)
        sorted_kw_objects = sorted(kw_objects, key=lambda x: x.volume if x.volume is not None else 0, reverse=True)
        keyword_names = [kw.name for kw in sorted_kw_objects]  #Allows the keywords to be easily rendered into the text box.
        if len(keyword_names) < 20:
            keyword_names = cleaned_list
            # Workaround for API input limit bug. This can be removed later.

        return render_template("index.html", keywords=sorted_kw_objects, keyword_names=keyword_names)
    else:
        return render_template("index.html", error="Please enter a keyword.")


if __name__ == '__main__':
    app.run(debug=True)



    # list = kw_obj_constructor("test, observe")
    # print(len(list))
    # print(list)
    # for item in list:
    #     print(item.name)

