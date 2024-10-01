import validators
from keys import client
from flask import session

states = {'Alaska': 21132, 'Alabama': 21133, 'Arkansas': 21135, 'Arizona': 21136, 'California': 21137, 'Colorado': 21138,
          'Connecticut': 21139, 'District of Columbia': 21140, 'Delaware': 21141, 'Florida': 21142, 'Georgia': 21143,
          'Hawaii': 21144, 'Iowa': 21145, 'Idaho': 21146, 'Illinois': 21147, 'Indiana': 21148, 'Kansas': 21149,
          'Kentucky': 21150, 'Louisiana': 21151, 'Massachusetts': 21152, 'Maryland': 21153, 'Maine': 21154,
          'Michigan': 21155, 'Minnesota': 21156, 'Missouri': 21157, 'Mississippi': 21158, 'Montana': 21159,
          'North Carolina': 21160, 'North Dakota': 21161, 'Nebraska': 21162, 'New Hampshire': 21163, 'New Jersey': 21164,
          'New Mexico': 21165, 'Nevada': 21166, 'New York': 21167, 'Ohio': 21168, 'Oklahoma': 21169, 'Oregon': 21170,
          'Pennsylvania': 21171, 'Rhode Island': 21172, 'South Carolina': 21173, 'South Dakota': 21174, 'Tennessee': 21175,
          'Texas': 21176, 'Utah': 21177, 'Virginia': 21178, 'Vermont': 21179, 'Washington': 21180, 'Wisconsin': 21182,
          'West Virginia': 21183, 'Wyoming': 21184}

countries = {
    'Afghanistan': 2004,
    'Albania': 2008,
    'Antarctica': 2010,
    'Algeria': 2012,
    'American Samoa': 2016,
    'Andorra': 2020,
    'Angola': 2024,
    'Antigua and Barbuda': 2028,
    'Azerbaijan': 2031,
    'Argentina': 2032,
    'Australia': 2036,
    'Austria': 2040,
    'The Bahamas': 2044,
    'Bahrain': 2048,
    'Bangladesh': 2050,
    'Armenia': 2051,
    'Barbados': 2052,
    'Belgium': 2056,
    'Bhutan': 2064,
    'Bolivia': 2068,
    'Bosnia and Herzegovina': 2070,
    'Botswana': 2072,
    'Brazil': 2076,
    'Belize': 2084,
    'Solomon Islands': 2090,
    'Brunei': 2096,
    'Bulgaria': 2100,
    'Myanmar (Burma)': 2104,
    'Burundi': 2108,
    'Belarus': 2112,
    'Cambodia': 2116,
    'Cameroon': 2120,
    'Canada': 2124,
    'Cabo Verde': 2132,
    'Central African Republic': 2140,
    'Sri Lanka': 2144,
    'Chad': 2148,
    'Chile': 2152,
    'China': 2156,
    'Christmas Island': 2162,
    'Cocos (Keeling) Islands': 2166,
    'Colombia': 2170,
    'Comoros': 2174,
    'Republic of the Congo': 2178,
    'Democratic Republic of the Congo': 2180,
    'Cook Islands': 2184,
    'Costa Rica': 2188,
    'Croatia': 2191,
    'Cyprus': 2196,
    'Czechia': 2203,
    'Benin': 2204,
    'Denmark': 2208,
    'Dominica': 2212,
    'Dominican Republic': 2214,
    'Ecuador': 2218,
    'El Salvador': 2222,
    'Equatorial Guinea': 2226,
    'Ethiopia': 2231,
    'Eritrea': 2232,
    'Estonia': 2233,
    'South Georgia and the South Sandwich Islands': 2239,
    'Fiji': 2242,
    'Finland': 2246,
    'France': 2250,
    'French Polynesia': 2258,
    'French Southern and Antarctic Lands': 2260,
    'Djibouti': 2262,
    'Gabon': 2266,
    'Georgia': 2268,
    'The Gambia': 2270,
    'Germany': 2276,
    'Ghana': 2288,
    'Kiribati': 2296,
    'Greece': 2300,
    'Grenada': 2308,
    'Guam': 2316,
    'Guatemala': 2320,
    'Guinea': 2324,
    'Guyana': 2328,
    'Haiti': 2332,
    'Heard Island and McDonald Islands': 2334,
    'Vatican City': 2336,
    'Honduras': 2340,
    'Hungary': 2348,
    'Iceland': 2352,
    'India': 2356,
    'Indonesia': 2360,
    'Iraq': 2368,
    'Ireland': 2372,
    'Israel': 2376,
    'Italy': 2380,
    "Cote d'Ivoire": 2384,
    'Jamaica': 2388,
    'Japan': 2392,
    'Kazakhstan': 2398,
    'Jordan': 2400,
    'Kenya': 2404,
    'South Korea': 2410,
    'Kuwait': 2414,
    'Kyrgyzstan': 2417,
    'Laos': 2418,
    'Lebanon': 2422,
    'Lesotho': 2426,
    'Latvia': 2428,
    'Liberia': 2430,
    'Libya': 2434,
    'Liechtenstein': 2438,
    'Lithuania': 2440,
    'Luxembourg': 2442,
    'Madagascar': 2450,
    'Malawi': 2454,
    'Malaysia': 2458,
    'Maldives': 2462,
    'Mali': 2466,
    'Malta': 2470,
    'Mauritania': 2478,
    'Mauritius': 2480,
    'Mexico': 2484,
    'Monaco': 2492,
    'Mongolia': 2496,
    'Moldova': 2498,
    'Montenegro': 2499,
    'Morocco': 2504,
    'Mozambique': 2508,
    'Oman': 2512,
    'Namibia': 2516,
    'Nauru': 2520,
    'Nepal': 2524,
    'Netherlands': 2528,
    'Curacao': 2531,
    'Sint Maarten': 2534,
    'Caribbean Netherlands': 2535,
    'New Caledonia': 2540,
    'Vanuatu': 2548,
    'New Zealand': 2554,
    'Nicaragua': 2558,
    'Niger': 2562,
    'Nigeria': 2566,
    'Niue': 2570,
    'Norfolk Island': 2574,
    'Norway': 2578,
    'Northern Mariana Islands': 2580,
    'United States Minor Outlying Islands': 2581,
    'Micronesia': 2583,
    'Marshall Islands': 2584,
    'Palau': 2585,
    'Pakistan': 2586,
    'Panama': 2591,
    'Papua New Guinea': 2598,
    'Paraguay': 2600,
    'Peru': 2604,
    'Philippines': 2608,
    'Pitcairn Islands': 2612,
    'Poland': 2616,
    'Portugal': 2620,
    'Guinea-Bissau': 2624,
    'Timor-Leste': 2626,
    'Qatar': 2634,
    'Romania': 2642,
    'Russia': 2643,
    'Rwanda': 2646,
    'Saint Barthelemy': 2652,
    'Saint Helena, Ascension and Tristan da Cunha': 2654,
    'Saint Kitts and Nevis': 2659,
    'Saint Lucia': 2662,
    'Saint Martin': 2663,
    'Saint Pierre and Miquelon': 2666,
    'Saint Vincent and the Grenadines': 2670,
    'San Marino': 2674,
    'Sao Tome and Principe': 2678,
    'Saudi Arabia': 2682,
    'Senegal': 2686,
    'Serbia': 2688,
    'Seychelles': 2690,
    'Sierra Leone': 2694,
    'Singapore': 2702,
    'Slovakia': 2703,
    'Vietnam': 2704,
    'Slovenia': 2705,
    'Somalia': 2706,
    'South Africa': 2710,
    'Zimbabwe': 2716,
    'Spain': 2724,
    'South Sudan': 2728,
    'Sudan': 2736,
    'Suriname': 2740,
    'Eswatini': 2748,
    'Sweden': 2752,
    'Switzerland': 2756,
    'Tajikistan': 2762,
    'Thailand': 2764,
    'Togo': 2768,
    'Tokelau': 2772,
    'Tonga': 2776,
    'Trinidad and Tobago': 2780,
    'United Arab Emirates': 2784,
    'Tunisia': 2788,
    'Turkiye': 2792,
    'Turkmenistan': 2795,
    'Tuvalu': 2798,
    'Uganda': 2800,
    'Ukraine': 2804,
    'North Macedonia': 2807,
    'Egypt': 2818,
    'United Kingdom': 2826,
    'Guernsey': 2831,
    'Jersey': 2832,
    'Isle of Man': 2833,
    'Tanzania': 2834,
    'United States': 2840,
    'Burkina Faso': 2854,
    'Uruguay': 2858,
    'Uzbekistan': 2860,
    'Venezuela': 2862,
    'Wallis and Futuna': 2876,
    'Samoa': 2882,
    'Yemen': 2887,
    'Zambia': 2894}

def main(client, customer_id):
    """The main method that creates all necessary entities for the example.

    Args:
        client: an initialized GoogleAdsClient instance.
        customer_id: a client customer ID.
    """
    generate_historical_metrics(client, customer_id)

def convert_geotarget_values(geotargeting_status):
    print(f"Debug GeoTargeting Status: {geotargeting_status}")
    geo_codes = []
    #Based on the value of the geotargeting option, convert it to a list of codes that GKP can use.
    if geotargeting_status == "States":
        #Get the values of the states selected from the session.
        selected_states = session.get('selected_states', [])
        #For each selected states, look up its associated code in the constant list and return it as a list of codes.
        for state in selected_states:
            if state in states:
                geo_codes.append(states[state])
        # print(f"Debug geo codes: {geo_codes}")
        return geo_codes

    if geotargeting_status == "Countries":
        selected_countries = session.get('selected_countries', [])
        for country in selected_countries:
            if country in countries:
                geo_codes.append(countries[country])
        print(f"Debug geo codes: {geo_codes}")
        return geo_codes
    else: #Default return the US code in a one-item list.
        return ["2840"]


def generate_historical_metrics(client, customer_id, language, keyword_list, geo_targeting_status):
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
    #First, convert the geotarget values into the proper codes:
    geo_targeting_ids = convert_geotarget_values(geo_targeting_status)

    #For each area selected, append it to the constants array.
    for id in geo_targeting_ids:
        request.geo_target_constants.append(
            googleads_service.geo_target_constant_path(f"{id}")
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
    # kw_ideas(client, "9136996873", "https://bgcpbc.org/events/")
    test = generate_historical_metrics(client, "9136996873", "english", ["cats", "dogs"])
    print(test)