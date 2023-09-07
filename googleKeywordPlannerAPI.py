from keys import client



def main(client, customer_id):
    """The main method that creates all necessary entities for the example.

    Args:
        client: an initialized GoogleAdsClient instance.
        customer_id: a client customer ID.
    """
    generate_historical_metrics(client, customer_id)


def generate_historical_metrics(client, customer_id):
    """Generates historical metrics and prints the results.

    Args:
        client: an initialized GoogleAdsClient instance.
        customer_id: a client customer ID.
    """
    googleads_service = client.get_service("GoogleAdsService")
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
    request.customer_id = customer_id
    request.keywords = ["mars cruise", "cheap cruise", "jupiter cruise"]
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
    request.language = googleads_service.language_constant_path("1000")

    response = keyword_plan_idea_service.generate_keyword_historical_metrics(
        request=request
    )

    for result in response.results:
        metrics = result.keyword_metrics
        # These metrics include those for both the search query and any variants
        # included in the response.
        print(
            f"The search query '{result.text}' (and the following variants: "
            f"'{result.close_variants if result.close_variants else 'None'}'), "
            "generated the following historical metrics:\n"
        )

        # Approximate number of monthly searches on this query averaged for the
        # past 12 months.
        print(f"\tApproximate monthly searches: {metrics.avg_monthly_searches}")

        # The competition level for this search query.
        print(f"\tCompetition level: {metrics.competition}")

        # The competition index for the query in the range [0, 100]. This shows
        # how competitive ad placement is for a keyword. The level of
        # competition from 0-100 is determined by the number of ad slots filled
        # divided by the total number of ad slots available. If not enough data
        # is available, undef will be returned.
        print(f"\tCompetition index: {metrics.competition_index}")

        # Top of page bid low range (20th percentile) in micros for the keyword.
        print(
            f"\tTop of page bid low range: {metrics.low_top_of_page_bid_micros}"
        )

        # Top of page bid high range (80th percentile) in micros for the
        # keyword.
        print(
            "\tTop of page bid high range: "
            f"{metrics.high_top_of_page_bid_micros}"
        )

        # Approximate number of searches on this query for the past twelve
        # months.
        for month in metrics.monthly_search_volumes:
            print(
                f"\tApproximately {month.monthly_searches} searches in "
                f"{month.month.name}, {month.year}"
            )

if __name__ == '__main__':
    main(client, "913-699-6873")