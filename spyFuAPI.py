import requests
from models import Keyword
from keys import spyfu_key


def get_keyword_data(keywords):
    url = f"https://www.spyfu.com/apis/keyword_api/v2/related/getKeywordInformation"
    headers = {
    }
    query_params = {
        "api_key": spyfu_key,
        "keywords": f"{keywords}"
    }

    response = requests.get(url, headers=headers, params=query_params)
    # print(response.text)

    if response.status_code == 200:
        # search_volume = response.json()["results"][0]["searchVolume"]
        # response_json = response.json()
        # print(response_json)
        # # Iterate through each JSON, grabbing the client name and Visitors Paid
        # data = dict()
        # for json in response_json:
        #     print(json)
        #     name = json.get('Customer', 'Key not found')
        #     visitors = json.get('Visitors_Paid', 'Key not found')
        #     data.update({f"{name}":f"{int(visitors)}"})
        # print(response.json())
        return response.json()
    else:
        print("Status code:", response.status_code)
        print("Response content:", response.text)

if __name__ == '__main__':
    kw_data = get_keyword_data("test, Jerry Garcia, Bob Weir")
    for result in kw_data["results"]:
        print(result)
        keyword = result['keyword']
        search_volume = result['searchVolume']
