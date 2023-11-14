import openai
import re
import time
import validators

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from keys import open_ai_key
from models import Keyword
from spyFuAPI import get_keyword_data
from scraper import scrape_page


app = Flask(__name__)
app.secret_key = "ghostfailurecurry"

openai.api_key = open_ai_key

language = "English"


def generate_broad_ad_group_ideas(keyword):
    try:
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads keywords."},
            {"role": "user", "content": f"Based on this keyword, generate 20 unique Google Ads keywords:\n\n{keywords_input}" 
                                        "Insert a line break after every keyword and return as a numbered list."
                                        f"Your responses must be in the {language} language."}
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


def generate_tight_keyword_list(keyword):
    try:
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads keywords."},
            {"role": "user", "content": f"Here is an input keyword: {keywords_input}."
                                        f"Use this keyword to generate 20 new keywords based on the following principles:"
                                        f" First, put the words in a different order as long as it doesn't change the meaning too much."
                                        "Second, use all fluent grammatical forms of essential words (e.g., compliance, comply, complying, complied)"
                                        "Third, include query phrases (e.g., what is/are, how to, where is/are, why."
                                        f"Fourth, your responses must be in the {language} language."
                                        "When you have a list of 20 keywords, insert a line break after every keyword and return as a numbered list."}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
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


def generate_from_scrape(page_text):
    try:
        keywords_input = page_text
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads Ad Groups and Keywords."},
            {"role": "user", "content": f"First, summarize this text: {keywords_input}."
                                        f"Second, Use this summary to generate 20 ad group ideas based on the summary."
                                        "Third, When you have a list of 20 keywords, insert a line break after every keyword and return as a numbered list."
                                        f"Fourth, Your responses must be in the {language} language."
                                        "Finally, Do not return the summary. Return only the numbered list."

             }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
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
        # cleaned_list = [re.sub(r'\d', '', text, count=2) for text in text_list]
        cleaned_list = [text.lstrip('.') for text in text_list]
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


def kw_obj_constructor(string, list): #TODO Create a dict for each keyword in string. Then, run the request to get search info. If the keys(names) match, update the data.
    kw_objs = []
    count = 1
    try:
        #Construct the initial object based on the list:
        for keyword in list:
            kw = Keyword(count, keyword)
            count += 1
            kw_objs.append(kw)

        # for kw in kw_objs:
        #     # print(kw.stats())

        kw_data = get_keyword_data(string) # Now run the SpyFu query and return the results.
        # print(kw_data)
        try:
            for result in kw_data["results"]:
                # print(result)
                keyword = result['keyword'].replace("'", "")
                for kw in kw_objs: #Loop through the keyword objects to look for matches. If found, update the data.
                    if kw.name == keyword:

                        search_volume = result.get('searchVolume', 0)
                        clicks = result.get('totalMonthlyClicks', 0)

                        kw.volume = search_volume
                        kw.clicks = clicks

                        print(f"Updated {kw.name} with Spyfu Data")

            return kw_objs
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        return []


def add_to_history(keyword):
    history = session.get("history", [])
    history.append(keyword)
    if len(history) > 5:
        history.pop(0)
    session["history"] = history
    # history.reverse()
    return history


def scrape_suggest(url):
    #Scrape the url.
    page_text = scrape_page(url)

    #Feed text into AI Prompt.
    #Have AI generate list of 20 Ad Group Ideas.
    keywords = generate_from_scrape(page_text)
    print(f"Debug: {keywords}")

    return keywords


@app.route('/', methods=['GET', 'POST'])
def index():
    app.logger.info('Processing request for the root path')
    return render_template('index.html')

@app.route('/custom_keywords', methods=['GET'])
def custom_keywords():
    print("Button Clicked! Generating Keywords...")
    keyword = request.args.get('keyword', '')
    history = add_to_history(keyword)
    try:
        if keyword: #Check to see if keyword exists.
            if validators.url(keyword) is True: #Check to see if keyword is a URL. If so, run a different function.
                print("URL Found!")
                custom_keywords = remove_numbers(scrape_suggest(keyword))
                cleaned_list = []
            else:
                print("Not a URL.")
                custom_keywords = remove_numbers(generate_broad_ad_group_ideas(keyword))
                cleaned_list = [keyword]
            for item in custom_keywords:
                try:
                    cleaned_item = item.split(" ", 1)[1]  # Split at the first space
                    cleaned_list.append(cleaned_item)
                except IndexError:  # If split fails, keep the original item
                    cleaned_list.append(item)

            # This ensures that entries with commas are treated as single entries
            quoted_keywords = ['"{}"'.format(kw) for kw in cleaned_list]

            # Now join the items, they're safely quoted
            list_as_str = ", ".join(quoted_keywords)

            print(list_as_str)

            kw_objects = kw_obj_constructor(list_as_str, cleaned_list)
            sorted_kw_objects = sorted(kw_objects, key=lambda x: x.volume if x.volume is not None else 0, reverse=True)
            keyword_names = [kw.name for kw in sorted_kw_objects]  #Allows the keywords to be easily rendered into the text box.
            if len(keyword_names) < 20:
                no_data = []
                for item in cleaned_list:
                    if item not in keyword_names:
                        no_data.append(item)
                # keyword_names = cleaned_list
                flash(f"No keyword data found for some entries: \n{no_data}")
                no_data.clear()

            return render_template("index.html", keywords=sorted_kw_objects, keyword_names=keyword_names, history=history)
        else:
            return render_template("index.html", error="Please enter a keyword.")
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return render_template("error_page.html")


@app.route('/targeted_keywords', methods=['GET'])
def generate_targeted_keywords():
    og_keyword = request.args.get('keyword', '')
    print(og_keyword)

    if og_keyword:
        tight_kw = generate_tight_keyword_list(og_keyword)
        cleaned_list = [og_keyword]
        history = session["history"]
        for item in tight_kw:
            try:
                cleaned_item = item.split(" ", 1)[1]  # Split at the first space
                cleaned_list.append(cleaned_item)
            except IndexError:  # If split fails, keep the original item
                cleaned_list.append(item)

        # This ensures that entries with commas are treated as single entries
        quoted_keywords = ['"{}"'.format(kw) for kw in cleaned_list]

        # Now join the items, they're safely quoted
        list_as_str = ", ".join(quoted_keywords)


        kw_objects = kw_obj_constructor(list_as_str)
        sorted_kw_objects = sorted(kw_objects, key=lambda x: x.volume if x.volume is not None else 0, reverse=True)
        keyword_names = [kw.name for kw in sorted_kw_objects]  #Allows the keywords to be easily rendered into the text box.
        if len(keyword_names) < 20:
            no_data = []
            for item in cleaned_list:
                if item not in keyword_names:
                    no_data.append(item)
            keyword_names = cleaned_list
            flash(f"No keyword data found for some entries: \n{no_data}")
        return render_template("keyword_table.html", keywords=sorted_kw_objects, keyword_names=keyword_names, history=history, original_kw=og_keyword)
    else:
        flash("Error loading keyword")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

