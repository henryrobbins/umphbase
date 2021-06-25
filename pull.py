import json
import os
import xmltodict
import pandas as pd
import subprocess


# TODO: Determine issue with direction parameter
def get_df(request: str,
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
    result = subprocess.run(['curl', url], stdout=subprocess.PIPE)
    txt = result.stdout.decode()
    if form == 'json':
        df_dict = json.loads(txt)['data']
    elif form == 'xml':
        df_dict = json.loads(json.dumps(xmltodict.parse(txt)))
        df_dict = df_dict['results']['result']
    return pd.DataFrame(df_dict)


# Create pandas dataframes
# ========================

shows_df = get_df('shows', 'json')
venues_df = get_df('venues', 'json')
jamcharts_df = get_df('jamcharts', 'json')
songs_df = get_df('songs', 'xml').set_index('@id')

# Some songs in songs_df do not have live performaces
# for one of the following reasons:
#  - In the discography with no live performace
#  - Appears as a tease/jam without its own entry in a set
# This list keeps track of songs that fall in this category
no_live_performs = []

setlists_df = pd.DataFrame()
for slug in songs_df['slug']:
    try:
        # E.T.I By Blue Öyster Cult has typo in database
        # Blue �yster Cult can't be parsed by JSON so use XML
        # Ringo response is large so use XML
        use_xml = ['eti', 'ringo']
        form = 'xml' if slug in use_xml else 'json'
        df = get_df('setlists/slug/%s' % slug, form)
        setlists_df = setlists_df.append(df)
        if len(df) == 0:
            no_live_performs.append(slug)
    except json.JSONDecodeError:
        print("Not parsed: %s" % slug)
setlists_df

# Write dataframes as CSV files
# =============================

db_path = 'atu_database'
if not os.path.exists(db_path):
    os.mkdir(db_path)
df_names = {
    'songs': songs_df,
    'shows': shows_df,
    'setlists': setlists_df,
    'jamcharts': jamcharts_df,
    'venues': venues_df
}
for name in df_names:
    df_names[name].to_csv(db_path + '/%s.csv' % name)
