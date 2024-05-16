# import csv
import requests
# from concurrent.futures import TimeoutError
# from pebble import ProcessPool, ProcessExpired
from flask import flash
from bs4 import BeautifulSoup
# from pprint import pprint
from keys import oxy_creds


tags_to_remove = ["script", "style", "head", "nav", "footer",
                  "aside", "header", "a"]\
                 # + ["post-author-date",
                 #  "simplesocialbuttons-inline", "site-header",
                 #  "site-footer", "jeg_related"]

# Break an array into chunks of n size
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


# Here the "s" paramater is the string you are passing in
def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def scrape_page(url):
    try:

        # Structure payload.
        payload = {
            "source": "universal",
            "geo_location": "United States",
            "url": url,
        }

        response = requests.request(
            'POST',
            'https://realtime.oxylabs.io/v1/queries',
            auth=oxy_creds, #Your credentials go here
            json=payload,
        )

        result = response.json()
        # print(f"Debug: {result}")

        result_html = result['results'][0]['content']

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(result_html, "lxml")

        # Remove unnecessary tags
        for tag in soup(class_=tags_to_remove):
            tag.decompose()

        # Get visible text
        text = soup.get_text()
        # print(f"Debug: {text}")

        # Split the lines, remove leading and trailing space on each line
        lines = (line.strip() for line in text.splitlines())

        # Break multi-headlines into a line each, drop blank lines
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))


        # Check if chunks is empty
        if not chunks:
            print('No visible text found in page.')
            flash(('No visible text found in page.'))
            return []

        # Find the longest chunk of text
        longest_chunk = max(chunks, key=len)

        # # Exclude chunks of text that are less than 30 characters long
        result = url + " | " + '\n'.join(chunk for chunk in chunks if chunk)

        if result == url + " | ": # If the chunking process cut off all the text, just return the raw text.
            return text
        #
        # #Return only the largest chunk.
        # result = query + " | " + longest_chunk

        return result

    except Exception as e:
        print(e)
        return e

if __name__ == '__main__':
    scrape_page("https://socialsecurityreport.org/wep-and-gpo-to-repeal-or-not/")
