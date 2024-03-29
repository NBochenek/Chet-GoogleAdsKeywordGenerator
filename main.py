import openai
import re
import time
import validators

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from keys import open_ai_key, client
from models import Keyword
from spyFuAPI import get_keyword_data
from scraper import scrape_page
from googleKeywordPlannerAPI import generate_historical_metrics, kw_ideas


app = Flask(__name__)
app.secret_key = "ghostfailurecurry"

openai.api_key = open_ai_key


@app.before_request
def set_default_session_variables():
    if 'language' not in session:
        session['language'] = "english"
    if 'keyword_engine' not in session:
        session['keyword_engine'] = "both"  # Default to "both", could be "spyfu" or "googlekeywordplanner"
    if 'idea_engine' not in session:
        session['idea_engine'] = "openai"  # Default to "openai", could be "googlekeywordplanner"
    if 'url_idea_engine' not in session:
        session['url_idea_engine'] = "googlekeywordplanner"  # Default to "googlekeywordplanner", could be "openai"


def get_variables():
    # Convert session variables to local variables
    language = session.get('language', "english")  # Default to "English" if not set
    keyword_engine = session.get('keyword_engine', "both")  # Default to "both"
    idea_engine = session.get('idea_engine', "openai")  # Default to "openai"
    url_idea_engine = session.get('url_idea_engine', "googlekeywordplanner")  # Default to "googlekeywordplanner"
    return language, keyword_engine, idea_engine, url_idea_engine


def generate_broad_ad_group_ideas(keyword, language):
    try:
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads Ad Group Ideas."},
            {"role": "user", "content": f"Based on this keyword, generate 20 unique Google Ads Ad Groups:\n\n{keywords_input}"
                                        f"Each Ad Group should be fewer than 4 words." 
                                        "Insert a line break after every Ad Group and return as a numbered list."
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
        language = session.get('language', "english")
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads keywords."},
            {"role": "user", "content": f"Here is an input keyword: {keywords_input}."
                                        f"Use this keyword to generate 20 new unique keywords based on the following principles:"
                                        f" First, put the words in a different order as long as it doesn't change the meaning too much."
                                        "Second, use all fluent grammatical forms of essential words (e.g., compliance, comply, complying, complied)"
                                        "Third, substitute nouns and adjectives with synonyms where possible."
                                        
                                        f"Finally, your responses must be in the {language} language."
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
    language = session.get('language', "english")
    #First summarize the text.
    try:
        keywords_input = page_text
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads Ad Groups and Keywords."},
            {"role": "user", "content": f"Summarize this text: {keywords_input}."
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

        summary = response["choices"][0]["message"]["content"].lower()
        print(f"Debug Summary: {summary}")

    except openai.error.APIError as e:
        print(e)
    except openai.error.ServiceUnavailableError as e:
        print(e)
        time.sleep(5)

    #Use the generated summary to create ad group ideas.
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads Ad Groups and Keywords."},
            {"role": "user", "content": f"First, here is a summary: {summary}."
                                        f"Second, Use this summary to generate 20 unique ad group ideas based on the summary."
                                        f"Third, each idea should be no more than four words in length."
                                        "Fourth, When you have a list of 20 keywords, insert a line break after every keyword and return as a numbered list."
                                        f"Fifth, Your responses must be in the {language} language."
                                        "Finally, Return only the numbered list."

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
        # Initial processing
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

        # Remove all characters before the first letter
        final_list = []
        for item in cleaned_list:
            match = re.search("[a-zA-Z]", item)
            if match:
                cleaned_item = item[match.start():]
                final_list.append(cleaned_item)
            else:
                final_list.append(item)
    except TypeError as e:
        print(e)
        return text_list
    return final_list


def kw_obj_constructor(string, list): #TODO Create a dict for each keyword in string. Then, run the request to get search info. If the keys(names) match, update the data.
    kw_objs = []
    keyword_engine = session.get('keyword_engine', "both")
    language = session.get('language', "english")
    count = 1
    try:
        #Construct the initial object based on the list:
        for keyword in list:
            kw = Keyword(count, keyword)
            count += 1
            kw_objs.append(kw)

        # for kw in kw_objs:
        #     # print(kw.stats())
        try:
            if keyword_engine == "spyfu":
                # Now run the SpyFu query and return the results.
                kw_data = get_keyword_data(string)
            if keyword_engine == "googlekeywordplanner":
                kw_data = generate_historical_metrics(client, "9136996873", language, list)
            elif keyword_engine == "both":
                spyfu_kw_data = get_keyword_data(string)
                google_kw_data = generate_historical_metrics(client, "9136996873", language, list)
        except TypeError as e:
            print(e)
            flash(str(e))
        # print(kw_data)
        try:
            if keyword_engine == "spyfu":
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
            if keyword_engine =="googlekeywordplanner":
                #Loop through kw data results:
                for result in kw_data.results:
                    # Loop through the keyword objects to look for matches. If found, update the data.
                    for kw in kw_objs:
                        if kw.name == result.text:
                            kw.volume = result.keyword_metrics.avg_monthly_searches
                            print(f"Updated {kw.name} with Google Keyword Planner Data")
                            break

                    # print(f"{result.text}")
                    # print(f"{result.keyword_metrics.avg_monthly_searches}")
                return kw_objs
            elif keyword_engine == "both":
                #Process Spyfu Results
                for result in spyfu_kw_data["results"]:
                    # print(result)
                    keyword = result['keyword'].replace("'", "")
                    for kw in kw_objs: #Loop through the keyword objects to look for matches. If found, update the data.
                        if kw.name == keyword:

                            search_volume = result.get('searchVolume', 0)
                            clicks = result.get('totalMonthlyClicks', 0)

                            kw.volume = search_volume
                            kw.clicks = clicks

                            print(f"Updated {kw.name} with Spyfu Data")
                #Process GKW Results
                for result in google_kw_data.results:
                    # Loop through the keyword objects to look for matches. If found, update the data.
                    for kw in kw_objs:
                        if kw.name == result.text:
                            if kw.volume is None or kw.volume < result.keyword_metrics.avg_monthly_searches:
                                kw.volume = result.keyword_metrics.avg_monthly_searches
                                print(f"Updated {kw.name} with Google Keyword Planner Data")
                                break
                            else:
                                print(f"Did not update {kw.name} with Google Keyword Planner Data")

                    # print(f"{result.text}")
                    # print(f"{result.keyword_metrics.avg_monthly_searches}")
                return kw_objs
        except Exception as e:
            print(e)
            flash(str(e))
            return render_template("error_page.html")
    except Exception as e:
        print(e)
        flash(str(e))
        return render_template("error_page.html")


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
    language = session.get('language', "english")  # Default to "English" if not set
    keyword_engine = session.get('keyword_engine', "both")  # Default to "both"
    idea_engine = session.get('idea_engine', "openai")  # Default to "openai"
    url_idea_engine = session.get('url_idea_engine', "googlekeywordplanner")  # Default to "googlekeywordplanner"
    # Now you can use these local variables for your logic, calculations, or pass them to your template
    # For example, passing them to a template to display
    print(f"Debug Settings: {language}, {keyword_engine}, {idea_engine}, {url_idea_engine}")
    return render_template('index.html', language=language, keyword_engine=keyword_engine, idea_engine=idea_engine,
                           url_idea_engine=url_idea_engine)

@app.route('/custom_keywords', methods=['GET'])
def custom_keywords():
    print("Button Clicked!")
    print("Generating Ad Group Ideas...")
    language = session.get('language', "english")  # Default to "English" if not set
    keyword_engine = session.get('keyword_engine', "both")  # Default to "both"
    idea_engine = session.get('idea_engine', "openai")  # Default to "openai"
    url_idea_engine = session.get('url_idea_engine', "googlekeywordplanner")  # Default to "googlekeywordplanner"
    keyword = request.args.get('keyword', '')
    history = add_to_history(keyword)
    try:
        if keyword: #Check to see if keyword exists.
            if validators.url(keyword) is True: #Check to see if keyword is a URL. If so, run a different function.
                print("URL Found!")
                try:
                    if url_idea_engine == "openai":
                        custom_keywords = remove_numbers(scrape_suggest(keyword))
                    elif url_idea_engine == "googlekeywordplanner":
                        custom_keywords = kw_ideas(client, "9136996873", str(keyword))
                except Exception as e:
                    print(e)
                    flash(str(e))
                    flash("This error occured during web scraping.")
                    return render_template("error_page.html")
                cleaned_list = []
            else:
                print("Not a URL.")
                try:
                    #TODO Create paths for the 3 idea engine options
                    custom_keywords = remove_numbers(generate_broad_ad_group_ideas(keyword, language))
                except Exception as e:
                    print(e)
                    flash(str(e))
                    flash("This error occured during ad group idea generation.")
                    return render_template("error_page.html")
                cleaned_list = [keyword]
            #If we're using the GKP URL module, then the entries are already in a list.
            if not url_idea_engine == "googlekeywordplanner":
                for item in custom_keywords:
                    try:
                        cleaned_item = item.split(" ", 1)[1]  # Split at the first space
                        cleaned_list.append(cleaned_item)
                    except IndexError:  # If split fails, keep the original item
                        cleaned_list.append(item)
            else:
                cleaned_list = custom_keywords

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
    except TypeError as e:
        app.logger.error(f"An error occurred: {e}")
        flash(str(e))
        return render_template("error_page.html")
    except AttributeError as e:
        print(e)
        flash(str(e))
        return render_template("error_page.html")
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        flash(str(e))
        return render_template("error_page.html")


@app.route('/targeted_keywords', methods=['GET'])
def generate_targeted_keywords():
    print("Button Clicked!")
    print("Generating targeted keywords...")
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


        kw_objects = kw_obj_constructor(list_as_str, cleaned_list)
        sorted_kw_objects = sorted(kw_objects, key=lambda x: x.volume if x.volume is not None else 0, reverse=True)
        keyword_names = [kw.name for kw in
                         sorted_kw_objects]  # Allows the keywords to be easily rendered into the text box.
        if len(keyword_names) < 20:
            no_data = []
            for item in cleaned_list:
                if item not in keyword_names:
                    no_data.append(item)
            # keyword_names = cleaned_list
            flash(f"No keyword data found for some entries: \n{no_data}")
            no_data.clear()
        return render_template("keyword_table.html", keywords=sorted_kw_objects, keyword_names=keyword_names, history=history, original_kw=og_keyword)
    else:
        flash("Error loading keyword")
        return redirect(url_for('index'))


@app.route('/options', methods=['GET', 'POST'])
def options():
    if request.method == 'POST':
        # Update session variables from form inputs
        session['language'] = request.form.get('language', session['language'])
        session['keyword_engine'] = request.form.get('keywordEngine', session['keyword_engine'])
        session['idea_engine'] = request.form.get('ideaEngine', session['idea_engine'])
        session['url_idea_engine'] = request.form.get('urlIdeaEngine', session['url_idea_engine'])

        # Redirect to a new page or back to the form page after processing.
        # You might want to redirect to a confirmation page or back to the form
        # with a success message. For simplicity, we'll redirect back to the form.
        return redirect(url_for('index'))

    # If method is GET, just render the template.
    return render_template('options.html',
                           current_language=session.get('language', 'english'),
                           current_keyword_engine=session.get('keyword_engine', 'both'),
                           current_idea_engine=session.get('idea_engine', 'openai'),
                           current_url_idea_engine=session.get('url_idea_engine', 'googlekeywordplanner'))


if __name__ == '__main__':
    app.run(debug=True)

