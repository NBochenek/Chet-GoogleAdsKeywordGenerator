import validators
from keys import client



def main(client, customer_id):
    """The main method that creates all necessary entities for the example.

    Args:
        client: an initialized GoogleAdsClient instance.
        customer_id: a client customer ID.
    """
    generate_historical_metrics(client, customer_id)


def generate_historical_metrics(client, customer_id, language, keyword_list):
    """Generates historical metrics and prints the results.

    Args:
        client: an initialized GoogleAdsClient instance.
        customer_id: a client customer ID.
    """
    googleads_service = client.get_service("GoogleAdsService")
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
    request.customer_id = customer_id
    request.keywords = keyword_list
    # Geo target constant 2840 is for USA.
    request.geo_target_constants.append(
        googleads_service.geo_target_constant_path("2840")
    )
    request.keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    )
    # Language criteria 1000 is for English. For the list of language criteria
    # IDs, see:
    # https://developers.google.com/google-ads/api/reference/data/codes-formats#languages

    #TODO Fill out more language codes.

    if language == "French":
        language_code = "1002"
    else:
        language_code = "1000"

    request.language = googleads_service.language_constant_path(f"{language_code}")

    response = keyword_plan_idea_service.generate_keyword_historical_metrics(
        request=request
    )

    return response\
        # , print(f"Debug GKP Response: {response}")


def kw_ideas(
        client, customer_id, input
):
    ideas_dict = {}
    #Convert the input to url or keyword based on the validator.
    if validators.url(input) is True:
        page_url = input
        keyword_texts = None
    else:
        keyword_texts = input
        page_url = None
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

    # Either keywords or a page_url are required to generate keyword ideas
    # so this raises an error if neither are provided.
    if not (keyword_texts or page_url):
        raise ValueError(
            "At least one of keywords or page URL is required, "
            "but neither was specified."
        )

    # Only one of the fields "url_seed", "keyword_seed", or
    # "keyword_and_url_seed" can be set on the request, depending on whether
    # keywords, a page_url or both were passed to this function.
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.include_adult_keywords = False

    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if page_url:
        request.url_seed.url = page_url

    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of StringValue objects.
    if keyword_texts:
        request.keyword_seed.keywords.extend(keyword_texts)

    # # To generate keyword ideas using both a list of keywords and a page_url we
    # # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # # "keywords" fields.
    # if keyword_texts and page_url:
    #     request.keyword_and_url_seed.url = page_url
    #     request.keyword_and_url_seed.keywords.extend(keyword_texts)

    keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(
        request=request
    )

    for idea in keyword_ideas:
        ideas_dict[idea.text] = idea.keyword_idea_metrics.avg_monthly_searches
    # Sorting the dictionary by value in descending order
    sorted_data = dict(sorted(ideas_dict.items(), key=lambda item: item[1], reverse=True))
    #Converts the dict to a list and trims it to the top 20 entries.
    sorted_keys = list(sorted_data.keys())[:50]
    # print(sorted_data, len(ideas_dict))
    print(sorted_keys)
    return sorted_keys


if __name__ == '__main__':
    kw_ideas(client, "9136996873", "https://bgcpbc.org/events/"
)