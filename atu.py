import json
import requests
import xmltodict
import pandas as pd


# TODO: Determine issue with direction parameter
def request(request: str,
            form: str,
            order_by: str = "",
            # direction : str = "",
            limit: int = "0") -> pd.DataFrame:
    '''Return the response from a request to the ATU database.

    The ATU (All Things Umphrey's) database contains the history of
    setlists from Umphrey's McGee. This function takes a valid
    request to the API (v1). The form of valid requests can be found at
    https://allthings.umphreys.com/api/docs.

    Attributes:
        request (str): A valid request to the API (v1)
        form (str): {'json', 'xml'}.
        order_by (str): Column to order by. Defaults to None
        direction (str): {'asc', 'desc'}. Defaults to 'asc'
        limit (int): Maximum number of results to return

    Returns:
        pd.DataFrame: The pandas dataframe representing the response
    '''
    # &direction=%s" % (direction)
    query = "order_by=%s&limit=%s" % (order_by, str(limit))
    base = "https://allthings.umphreys.com/api/v1/"
    url = base + "%s.%s?%s" % (request, form, query)
    txt = requests.get(url).text
    print('Request: ' + "%s.%s?%s" % (request, form, query))
    if form == 'json':
        df_dict = json.loads(txt)['data']
    elif form == 'xml':
        df_dict = json.loads(json.dumps(xmltodict.parse(txt)))
        df_dict = df_dict['results']['result']
    return pd.DataFrame(df_dict)
