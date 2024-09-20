import google.ads.googleads.errors
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
from google.cloud import logging


# Instantiates a client
logging_client = logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module.
logger = logging_client.logger('feedback-logger')

app = Flask(__name__)
app.secret_key = "ghostfailurecurry"

openai.api_key = open_ai_key
model = "gpt-4o" #directs what GPT model to use.


@app.before_request
def set_default_session_variables():
    if 'language' not in session:
        session['language'] = "english"
    if 'keyword_engine' not in session:
        session['keyword_engine'] = "both"  # Default to "both", could be "spyfu" or "googlekeywordplanner"
    if 'idea_engine' not in session:
        session['idea_engine'] = "openai"  # Default to "openai", could be "googlekeywordplanner"
    if 'url_idea_engine' not in session:
        session['url_idea_engine'] = "openai"  # Default to "openai", could be "openai"
    if 'iterative_generation' not in session:
        session['iterative_generation'] = False


def get_variables():
    # Convert session variables to local variables
    language = session.get('language', "english")  # Default to "English" if not set
    keyword_engine = session.get('keyword_engine', "both")  # Default to "both"
    idea_engine = session.get('idea_engine', "openai")  # Default to "openai"
    url_idea_engine = session.get('url_idea_engine', "openai")  # Default to "googlekeywordplanner"
    iterative_generation = session.get('iterative_generation', False)
    return language, keyword_engine, idea_engine, url_idea_engine, iterative_generation


def generate_broad_ad_group_ideas(keyword, language):
    try:
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads Ad Group Ideas."},
            {"role": "user", "content": f"Based on this keyword, generate 20 unique Google Ads Ad Groups:\n\n{keywords_input}"
                                        f"Each Ad Group Idea should be between 2 and 4 words. Do not concatenate words." 
                                        "Insert a line break after every Ad Group Idea and return as a numbered list."
                                        "Do not return anything but the idea list."
                                        f"Your responses must be in the {language} language."}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.8,
        )

        # Process the response content to remove empty strings and return the list of keywords
        keywords = [line.strip() for line in response["choices"][0]["message"]["content"].split("\n") if line.strip()]

        return keywords  # Return the list of keywords instead of the formatted

    except openai.error.APIError as e:
        print(e)
    except openai.error.ServiceUnavailableError as e:
        print(e)
        time.sleep(5)


def iterative_generation_function(input, language):
    try:
        keywords_input = input
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads Ad Group Ideas."},
            {"role": "user", "content": f"Based on this input, generate at least 20 unique Google Ads Ad Group Ideas:\n\n{keywords_input}"
                                        f"Each Ad Group Idea should be between 2 and 4 words. Do not concatenate words."
                                        f"Each Ad Group Idea should be relevant to the others."
                                        "Insert a line break after every Ad Group and return as a list."
                                        f"Your responses must be in the {language} language."}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.8,
        )

        keywords = response["choices"][0]["message"]["content"].lower().lstrip().strip().split("\n")[:20]
        print(f"Debug: {response}")
        return keywords  # Return the list of keywords instead of the formatted

    except openai.error.APIError as e:
        print(e)
    except openai.error.ServiceUnavailableError as e:
        print(e)
        time.sleep(5)


def generate_tight_keyword_list(keyword, language):
    try:
        keywords_input = keyword
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates Google Ads keywords."},
            {"role": "user", "content": f"Here is an input keyword: {keywords_input}."
                                        f"Use this keyword to generate 20 new unique keywords based on the following principles:"
                                        f"First, put the words in a different order as long as it doesn't change the meaning too much."
                                        "Second, use all fluent grammatical forms of essential words (e.g., compliance, comply, complying, complied)"
                                        "Third, substitute nouns and adjectives with synonyms where possible."
                                        
                                        f"Finally, your responses must be in the {language} language."
                                        "When you have a list of 20 keywords, wrap them in the characters ** so they can be easily extracted."}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.8,
        )

        keywords = response["choices"][0]["message"]["content"].lower().lstrip().strip()

        # print(f"Debug: {response, keywords}")

        return keywords  # Return the list of keywords instead of the formatted

    except openai.error.APIError as e:
        print(e)
    except openai.error.ServiceUnavailableError as e:
        print(e)
        time.sleep(5)


def extract_keywords(text):
    # Compile a regular expression pattern that matches text enclosed in **
    pattern = re.compile(r'\*\*(.*?)\*\*')

    # Find all occurrences of the pattern
    matches = pattern.findall(text)

    return matches


def generate_from_scrape(page_text):
    summary = None #Init summary
    language = session.get('language', "english")
    #First summarize the text.
    try:
        keywords_input = str(page_text)
        messages = [
            {"role": "system", "content": "You are a helpful assistant that creates useful summaries out of scraped web page text."},
            {"role": "user", "content": f"Summarize this text: {keywords_input}."
                                        f"Do not return anything but the summary. Do not use the word 'summary' or 'article' in your response."
             }
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.8,
        )

        # print("Debug", response)
        summary = response["choices"][0]["message"]["content"].lower()
        print(f"Debug Summary: {summary}")
        flash(f"Summary: {summary}")

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
                                        f"Third, each idea should be no more than four words in length. Do not concatenate words."
                                        "Fourth, When you have a list of 20 keywords, insert a line break after every keyword and return as a numbered list."
                                        f"Fifth, Your responses must be in the {language} language."
                                        "Finally, Return only the numbered list."

             }
        ]
        response = openai.ChatCompletion.create(
            model=model,
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

        # Replace hyphens that are not between alphabetical characters
        def replace_hyphens(text):
            # This regex replaces hyphens that are not surrounded by alphabets
            return re.sub(r'(?<![a-zA-Z])-|-(?![a-zA-Z])', '', text)

        cleaned_list = [replace_hyphens(text) for text in cleaned_list]

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


def update_keyword_objects(kw_objs, api_data, source):
    """Updates keyword objects with data from a given API source."""
    if source == "spyfu":
        results = api_data.get("results", [])
    elif source == "googlekeywordplanner":
        results = api_data.results
    else:
        return kw_objs
    for result in results:
        if source == "spyfu":
            keyword = result['keyword'].replace("'", "").lower()
        elif source == "googlekeywordplanner":
            keyword = result.text.lower()
        for kw in kw_objs:
            if kw.name.lower() == keyword:
                if source == "spyfu":
                    kw.volume = result.get('searchVolume', 0)
                    kw.clicks = result.get('totalMonthlyClicks', 0)
                elif source == "googlekeywordplanner":
                    #If the google metrics are worse, skip them.
                    if result.keyword_metrics.avg_monthly_searches is not None and kw.volume is not None:
                        if int(result.keyword_metrics.avg_monthly_searches) > kw.volume:
                            kw.volume = result.keyword_metrics.avg_monthly_searches
                    else:
                        break
                print(f"Updated {kw.name} with {source} data.")
    return kw_objs

def kw_obj_constructor(string, list):
    kw_objs = []
    keyword_engine = session.get('keyword_engine', "both")
    language = session.get('language', "english")
    count = 1
    kw_data = None

    try:
        # Construct the initial object based on the list:
        for keyword in list:
            print(f"Debug: {keyword}")
            if keyword:
                kw = Keyword(count, keyword)
                if isinstance(kw, Keyword):
                    kw_objs.append(kw)
                    count += 1
            else:
                print("Not a Keyword object:", type(kw), kw)

        # Run the keyword engine requests:
        if keyword_engine in ["spyfu", "both"]:
            spyfu_kw_data = get_keyword_data(string)
            # print(f"Debug Spyfu Data: {spyfu_kw_data}")
            kw_objs = update_keyword_objects(kw_objs, spyfu_kw_data, "spyfu")

        if keyword_engine in ["googlekeywordplanner", "both"]:
            google_kw_data = generate_historical_metrics(client, "9136996873", language, list)
            # print(f"Debug Google Data: {google_kw_data}")
            kw_objs = update_keyword_objects(kw_objs, google_kw_data, "googlekeywordplanner")

    except TypeError as e:
        print(e)
        print(f"Debug: This keyword caused the error: {keyword}")
        flash(str(e))
    except google.ads.googleads.errors.GoogleAdsException as e:
        print(e)
        flash(str(e))
    except Exception as e:
        print(f"Error {type(e)}during Keyword Object creation. Error: {e}")
        flash(str(e))
        return kw_objs

    return kw_objs




def add_to_history(keyword):
    history = session.get("history", [])
    #Truncate if the keyword is too big.
    if len(keyword) > 20:
        keyword = keyword[:30] + "..."
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
    url_idea_engine = session.get('url_idea_engine', "openai")  # Default to "googlekeywordplanner"
    iterative_generation = session.get('iterative_generation', False)
    # Now you can use these local variables for your logic, calculations, or pass them to your template
    # For example, passing them to a template to display
    print(f"Debug Settings: {language}, {keyword_engine}, {idea_engine}, {url_idea_engine}, {iterative_generation}")
    return render_template('index.html', language=language, keyword_engine=keyword_engine, idea_engine=idea_engine,
                           url_idea_engine=url_idea_engine, iterative_generation=iterative_generation)

@app.route('/custom_keywords', methods=['GET'])
def custom_keywords():
    print("Button Clicked!")
    print("Generating Ad Group Ideas...")
    language = session.get('language', "english")  # Default to "English" if not set
    keyword_engine = session.get('keyword_engine', "both")  # Default to "both"
    idea_engine = session.get('idea_engine', "openai")  # Default to "openai"
    url_idea_engine = session.get('url_idea_engine', "openai")  # Default to "googlekeywordplanner"
    iterative_generation = session.get('iterative_generation', False)
    keyword = request.args.get('keyword', '')
    history = add_to_history(keyword)
    input_is_chunk = False
    input_type = "text"
    print(f"Debug! Input: {keyword}")
    try:
        if keyword: #Check to see if keyword exists.
            if validators.url(keyword):
                input_type = "url"
                print("URL found!")
                if url_idea_engine == "openai":
                    custom_keywords = remove_numbers(scrape_suggest(keyword))
                elif url_idea_engine == "googlekeywordplanner":
                    custom_keywords = kw_ideas(client, "9136996873", str(keyword))
            if len(keyword) > 20:  # This indicates a text chunk, so handle it differently
                input_is_chunk = True
                input_type = "chunk"
                print("Debug: Input is chunk.")
                custom_keywords = remove_numbers(generate_from_scrape(keyword))
            elif keyword == "error_debug": #This is a dev-designed debug string designed to force an error,
                raise Exception("Debug Error Message")
            else:
                # Handle the case where the keyword is neither a URL nor a long text chunk
                print("Short text or keyword found, handling differently.")
                custom_keywords = remove_numbers(generate_broad_ad_group_ideas(keyword, language))

            #TODO This module does not work as intended.
            #If we're using the GKP URL module, then the entries are already in a list.
            # if url_idea_engine != "googlekeywordplanner" or input_is_chunk:
            #     for item in custom_keywords:
            #         try:
            #             cleaned_item = item.split(" ", 1)[1]  # Split at the first space
            #             print("Debug 430: ", cleaned_item)
            #             cleaned_list.append(cleaned_item)
            #         except IndexError:  # If split fails, keep the original item
            #             cleaned_list.append(item)
            # else:
            #     cleaned_list = custom_keywords
                # #Ensure that the list also includes the keyword in the first position
                # cleaned_list.insert(0, keyword)

            cleaned_list = custom_keywords
            if input_type == "text":
                cleaned_list.append(keyword)

            # This ensures that entries with commas are treated as single entries
            quoted_keywords = ['"{}"'.format(kw) for kw in cleaned_list]
            print("Debug 440: ", cleaned_list)

            # Now join the items, they're safely quoted
            list_as_str = ", ".join(quoted_keywords)

            print("Debug 444:", list_as_str)

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

            session['last_input'] = input_type # Saves the last input type to the session.
            return render_template("index.html", keywords=sorted_kw_objects, keyword_names=keyword_names, history=history, iterative_generation=iterative_generation)

        else:
            return render_template("index.html", error="Please enter a keyword.")
    except TypeError as e:
        app.logger.error(f"An error occurred: {e}")
        flash(str(e))
        return render_template("error_page.html")
    except AttributeError as e:
        app.logger.error(f"An error occurred: {e}")
        flash(str(e))
        return render_template("error_page.html")
    except Exception as e:
        print(e)
        app.logger.error(f"An error occurred: {e}")
        flash(str(e))
        return render_template("error_page.html")


@app.route('/targeted_keywords', methods=['GET'])
def generate_targeted_keywords():
    print("Button Clicked!")
    print("Generating targeted keywords...")
    input_type = "targeted"
    session['last_input'] = input_type  # Saves the last input type to the session.
    language = session.get('language', "english")  # Default to "English" if not set
    og_keyword = request.args.get('keyword', '')
    print(og_keyword)

    if og_keyword:
        tight_kw = generate_tight_keyword_list(og_keyword, language)
        tight_kw = remove_numbers(extract_keywords(tight_kw)) #Use RegEx to extract the keywords into a list. Then clean them of numbers if necessary
        if og_keyword not in tight_kw:
            tight_kw.append(og_keyword)
        history = session["history"]
        # print(f"Debug: {tight_kw}")

        # for item in tight_kw:
        #     try:
        #         cleaned_item = item.split(" ", 1)[1]  # Split at the first space
        #         cleaned_list.append(cleaned_item)
        #     except IndexError:  # If split fails, keep the original item
        #         cleaned_list.append(item)

        # This ensures that entries with commas are treated as single entries
        quoted_keywords = ['"{}"'.format(kw) for kw in tight_kw]

        # Now join the items, they're safely quoted
        list_as_str = ", ".join(quoted_keywords)

        # print(f"Debug: {list_as_str, cleaned_list}")


        kw_objects = kw_obj_constructor(list_as_str, tight_kw)
        sorted_kw_objects = sorted(kw_objects, key=lambda x: x.volume if x.volume is not None else 0, reverse=True)
        keyword_names = [kw.name for kw in
                         sorted_kw_objects]  # Allows the keywords to be easily rendered into the text box.
        if len(keyword_names) < 20:
            no_data = []
            for item in tight_kw:
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
        session['iterative_generation'] = request.form.get('iterativeGeneration', session['iterative_generation'])

        # Redirect to a new page or back to the form page after processing.
        # You might want to redirect to a confirmation page or back to the form
        # with a success message. For simplicity, we'll redirect back to the form.
        return redirect(url_for('index'))

    # If method is GET, just render the template.
    return render_template('options.html',
                           current_language=session.get('language', 'english'),
                           current_keyword_engine=session.get('keyword_engine', 'both'),
                           current_idea_engine=session.get('idea_engine', 'openai'),
                           current_url_idea_engine=session.get('url_idea_engine', 'openai'),
                           current_iterative_generation=session.get('iterative_generation', False))


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback_type = request.form['feedback']
    last_input = session.get('last_input', 'default_value')
    # Log the feedback using Google Cloud Logging
    print("Debug: Feedback logged.")
    logger.log_text(f"Feedback received: {feedback_type}, {last_input}", severity='INFO')

    # Create a single log entry with all session information
    session_info = (
        f"Session Info - Language: {session.get('language', 'Not set')}, "
        f"Keyword Engine: {session.get('keyword_engine', 'Not set')}, "
        f"Idea Engine: {session.get('idea_engine', 'Not set')}, "
        f"URL Idea Engine: {session.get('url_idea_engine', 'Not set')}, "
        f"Iterative Generation: {session.get('iterative_generation', 'Not set')}, "
        f"Feedback received: {feedback_type}"
    )
    logger.log_text(session_info, severity='INFO')

    # Process and store the feedback as needed
    return jsonify(success=True, message='Feedback received')

@app.route('/selected_keywords', methods=['POST'])
def handle_keywords():
    data = request.get_json()
    keywords = data['keywords']
    print(keywords)
    # Init
    history = add_to_history(keywords)
    language = session.get('language', "english")
    keyword_engine = session.get('keyword_engine', "both")
    iterative_generation = session.get('iterative_generation', False)
    input_type = "iterative"
    session['last_input'] = input_type  # Saves the last input type to the session.

    #Generate the ideas
    try:
        custom_keywords = remove_numbers(iterative_generation_function(keywords, language))
    except Exception as e:
        print(e)
        flash(str(e))
        flash("This error occured during ad group idea generation.")
        return render_template("error_page.html")

    #Get engine data and convert to objects

    #insert input keywords to list.
    for item in keywords:
        custom_keywords.insert(0, item)
    cleaned_list = custom_keywords

    # This ensures that entries with commas are treated as single entries
    quoted_keywords = ['"{}"'.format(kw) for kw in cleaned_list]

    # Now join the items, they're safely quoted
    list_as_str = ", ".join(quoted_keywords)

    print(list_as_str)

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

    return render_template("index.html", keywords=sorted_kw_objects, keyword_names=keyword_names, history=history, iterative_generation=iterative_generation)


if __name__ == '__main__':
    app.run(debug=True)
    # print(iterative_generation(["Museums Near Me", "Art Museums", "Museum Tours"], "english"))
    # keywords = generate_tight_keyword_list("bullshit", "english")
    # print(keywords)
    # print(remove_numbers(extract_keywords(keywords)))

