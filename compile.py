import math
import pandas as pd
pd.set_option('display.max_colwidth', 10000)
from datetime import datetime
import sql_util
from typing import List


ID_TO_CODE = pd.read_csv('data/song_codes.csv', index_col=0)['code'].to_dict()
SPECIAL_KEYS = ['$\\wedge$','*','H']
SET_CODES = {'1': 'S1',
             '2': 'S2',
             '3':'S3',
             '4': 'S4',
             'e': 'E',
             'e2': 'E2',
             'e3': 'E3'}
TRANSITIONS = {'None': '',
               ',' : ',',
               '>' : '\\textgreater{}',
               '->' : ' \\textrightarrow{}'}


def clean_text(text):
    if text is not None:
        return (text.replace('#039;', "'")
                    .replace('#39;', "'")
                    .replace('\R', '\\\\R')
                    .replace('\E', '\\\\E')
                    .replace('%', '\\%')
                    .replace('é', "\\'e")
                    .replace('&', "\\&")
                    .replace('#', "\\#")
                    .replace('$', "\\$")
                    .replace('\U0006fca0', "nor ")
                    .replace('>', '\\textgreater \\enspace ')
                    .replace('^', '$\\wedge$')
                    .replace('_', '\\char`_'))
    else:
        return None


def short_text(text: str, max_length: int):
    if len(text) > max_length:
        return text[:(max_length- 3)] + '...'
    else:
        return text


def table_tex(table: List[List[str]], widths: List[float]):
    widths = [str(w) + '\\columnwidth' for w in widths]
    rows = [''.join('\\cell{%s}{%s}' % (widths[i], row[i]) for i in range(len(row))) for row in table]
    return '\\newline\n'.join(rows)


def song_tex(song_id: int, jimmy_stewart: bool, with_lyrics: bool, hof: bool, text: str=None, superscript: bool=True, footnote:int=0) -> str:
    if text is None:
        text = ID_TO_CODE[song_id]
    special = [jimmy_stewart, with_lyrics, hof]
    if any(special):
        if superscript:
            ss = ''.join([SPECIAL_KEYS[i] for i in range(3) if special[i]])
            tex = '\\textbf{%s\\textsuperscript{%s}}' % (text, ss)
        else:
            tex = '\\textbf{%s}' % text
    else:
        tex = text
    if footnote != 0:
        return tex + '[%d]' % footnote
    else:
        return tex


def date_tex(date: datetime.date, jimmy_stewart: bool, with_lyrics: bool, hof: bool, superscript: bool=True) -> str:
    date_str = date.strftime('%m-%d-%y')
    special = [jimmy_stewart, with_lyrics, hof]
    if any(special):
        if superscript:
            ss = ''.join([SPECIAL_KEYS[i] for i in range(3) if special[i]])
            return '\\textbf{%s\\textsuperscript{%s}}' % (date_str, ss)
        else:
            return '\\textbf{%s}' % date_str
    else:
        return date_str


def song_codes_tex(row):
    name = clean_text(row['name'])
    return [short_text(name, 20), row['code']]


def compile_song_codes(credential):
    df = sql_util.get_table('songs', credential)
    df = df.sort_values('name')
    df['code'] = df['song_id'].apply(lambda x: ID_TO_CODE[x])
    df['tex'] = df.apply(lambda x: song_codes_tex(x), axis=1)
    with open('tex/song_codes.tex', 'w') as f:
        f.write(table_tex(list(df['tex']), [0.75, 0.25]))


def setlists_tex(row):
    date = row['show_date'].strftime('%m-%d-%Y')
    venue_name = clean_text(row['venue_name'])
    city = clean_text(row['city'])
    state = clean_text(row['state'])
    country = clean_text(row['country'])
    location = ', '.join([i for i in [city, state, country] if i != 'None'])
    title = ' | '.join([date, venue_name, location])

    def listify(string, set_split, item_split):
        string_split = string.split(set_split)
        return [i.split(item_split) for i in string_split]

    sets = row['set_number'].split(',')
    set_songs = listify(row['name'], '<sb>', '<|>')
    set_transitions = listify(row['transition'], '<sb>', '<|>')
    set_footnotes = listify(row['footnote'], '<sb>', '<|>')
    set_jimmy_stewart = listify(row['jimmy_stewart'], '<sb>', ',')
    set_with_lyrics = listify(row['with_lyrics'], '<sb>', ',')
    set_hof = listify(row['hof'], '<sb>', ',')

    i = 1
    footnotes = {}
    song_footnotes = []
    for set_footnote in set_footnotes:
        tmp = []
        for footnote in set_footnote:
            if footnote == 'None':
                tmp.append(0)
            else:
                if footnote not in footnotes.keys():
                    footnotes[footnote] = i
                    tmp.append(i)
                    i += 1
                else:
                    tmp.append(footnotes[footnote])
        song_footnotes.append(tmp)
    footnotes = {v: k for k, v in footnotes.items()}

    setlist_tex = ""
    for i in range(len(sets)):
        set_title = SET_CODES[sets[i]]
        set_song_objects = list(zip(*[set_songs[i], set_jimmy_stewart[i], set_with_lyrics[i], set_hof[i], song_footnotes[i]]))
        set_songs_tex = [song_tex(0, int(j), int(k), int(l), text=clean_text(i), footnote=w) for i,j,k,l,w in set_song_objects]
        songs_tex = ' '.join([set_songs_tex[j] + TRANSITIONS[set_transitions[i][j]] for j in range(len(set_songs_tex) - 1)] + [set_songs_tex[-1]])
        setlist_tex += '\\textbf{%s}: %s \\smallskip\n\n' % (set_title, songs_tex)

    notes_tex = ""
    for i in range(1,len(footnotes)+1):
        notes_tex += '[%d] %s\\smallskip\n\n' % (i, clean_text(footnotes[i]))
    if len(footnotes) > 0:
        notes_tex += '\\smallskip\n\n'
    if row['opener'] != 'None':
        notes_tex += '\\textbf{Support:} %s\\smallskip\n\n' % clean_text(row['opener'])
    # TODO: Be more careful parsing show notes
    if row['show_notes'] != 'None':
        notes_tex += '\\textbf{Notes:} %s\\smallskip\n\n' % clean_text(row['show_notes'])

    return '\\SetList{%s}{%s}{%s}' % (title, setlist_tex, notes_tex)


def compile_setlists(credential):
    # group_concat_max_len default value of 1024 too small
    cnx = credential.connect()
    cursor = cnx.cursor()
    cursor.execute('SET GLOBAL group_concat_max_len=65535')
    cursor.close()
    cnx.commit()
    cnx.close()
    df = sql_util.query('sql/setlists.sql', credential)
    df['tex'] = df.apply(lambda x: setlists_tex(x), axis=1)
    with open('tex/setlists.tex', 'w') as f:
        f.write('\n'.join(df['tex']))


def song_played_tex(row):
    full_name = clean_text(row['name'])
    name = short_text(full_name, 36)
    code = row['code']
    full_artist = clean_text(row['original_artist'])
    artist = short_text(full_artist, 36)
    first_played = row['first_played'].strftime('%m-%d-%y')
    last_played = row['last_played'].strftime('%m-%d-%y')
    return (name, code, artist, first_played, last_played)


def compile_songs_played(credential):
    df = sql_util.query('sql/songs_played.sql', credential)
    df = df.sort_values('name')
    df['code'] = df['song_id'].apply(lambda x: ID_TO_CODE[x])
    df['tex'] = df.apply(lambda x: song_played_tex(x), axis=1)
    with open('tex/songs_played.tex', 'w') as f:
        f.write('\n')
        f.write(table_tex(list(df['tex']), [0.35, 0.1, 0.35, 0.1, 0.1]))


def songs_by_year_tex(row):
    return [row['code']] + [row[i] for i in range(len(row) - 1)]


def compile_songs_by_year(credential):
    df = sql_util.query('sql/songs_by_year.sql', credential)
    years = list(range(min(df['year']), max(df['year']) + 1))
    songs = df['song_id'].unique()
    counts = df.set_index(['song_id', 'year'])['count'].to_dict()
    table = {}
    for i in songs:
        table[i] = [counts.get((i,j), 0) for j in years]
        table[i] = table[i] + [sum(table[i])]
    df = pd.DataFrame(table).T
    df = df.reset_index()
    df['code'] = df['index'].apply(lambda x: ID_TO_CODE[x])
    df = df.drop(columns='index')
    df['tex'] = df.apply(lambda x: songs_by_year_tex(x), axis=1)
    df = df.sort_values('code')
    with open('tex/songs_by_year.tex', 'w') as f:
        f.write('\n')
        w = math.floor((0.9 / (len(years) + 1)) * 1000) / 1000
        f.write(table_tex(list(df['tex']), [0.1] + ([w] * (len(years) + 1))))


def every_time_played_tex(row):
    date = date_tex(row['show_date'], row['jimmy_stewart'], row['with_lyrics'], row['hof'], superscript=False)
    if math.isnan(row['before_song_id']) or row['before_transition'] == 'None':
        before_song = '*O%s*' % SET_CODES[row['set_number']]
        before_transition = ""
    else:
        before_song = song_tex(row['before_song_id'], row['before_jimmy_stewart'],
                               row['before_with_lyrics'], row['before_hof'], superscript=False)
        before_transition = TRANSITIONS[row['before_transition']]
    if math.isnan(row['after_song_id']) or row['after_transition'] == 'None':
        after_song = '*C%s*' % SET_CODES[row['set_number']]
        after_transition = ""
    else:
        after_song = song_tex(row['after_song_id'], row['after_jimmy_stewart'],
                               row['after_with_lyrics'], row['after_hof'], superscript=False)
        after_transition = TRANSITIONS[row['after_transition']]
    return [date, before_song, before_transition, after_transition, after_song]


def compile_every_time_played(credential):

    df = sql_util.query('sql/every_time_played.sql', credential)
    df['tex'] = df.apply(lambda x: every_time_played_tex(x), axis=1)

    songs = sql_util.get_table('songs', credential)
    song_id_to_name = songs.set_index('song_id')['name'].to_dict()

    every_time_played_by_song = df.groupby('song_id')['tex'].apply(list)
    with open('tex/every_time_played.tex', 'w') as f:
        for song_id in every_time_played_by_song.keys():
            name = clean_text(song_id_to_name[song_id])
            table = table_tex(every_time_played_by_song[song_id], [0.3, 0.3, 0.07, 0.07, 0.26])
            f.write('\\begin{center}\\textbf{%s}\\end{center}\n' % name)
            f.write('\\medskip\n\n')
            f.write(table)


def hall_of_fame_tex(row):
    date = row['show_date'].strftime('%m-%d-%y')
    text = clean_text(row['name'])
    song = song_tex(row['song_id'], row['jimmy_stewart'], row['with_lyrics'],
                    row['hof'], text=text)
    return [date, song]


def compile_hall_of_fame(credential):
    df = sql_util.query('sql/hall_of_fame.sql', credential)
    df['tex'] = df.apply(lambda x: hall_of_fame_tex(x), axis=1)
    with open('tex/hall_of_fame.tex', 'w') as f:
        f.write(table_tex(list(df['tex']), [0.25, 0.27]))


def jimmy_stewart_tex(row):
    date = row['show_date'].strftime('%m-%d-%y')
    text = clean_text(row['name'])
    song = song_tex(row['song_id'], row['jimmy_stewart'], row['with_lyrics'],
                    row['hof'], text=text)
    return [date, song]


def compile_jimmy_stewart(credential):
    df = sql_util.query('sql/jimmy_stewart.sql', credential)
    df['tex'] = df.apply(lambda x: jimmy_stewart_tex(x), axis=1)
    with open('tex/jimmy_stewart.tex', 'w') as f:
        f.write(table_tex(list(df['tex']), [0.25, 0.75]))


def state_aggregation_tex(row):
    country = clean_text(row['country'])
    state = clean_text(row['state'])
    return [country, state, row['count'], int(row['jimmy_stewart']),
            int(row['with_lyrics']), int(row['hof'])]


def compile_state_aggregation(credential):
    df = sql_util.query('sql/state_aggregation.sql', credential)
    df['tex'] = df.apply(lambda x: state_aggregation_tex(x), axis=1)
    with open('tex/state_aggregation.tex', 'w') as f:
        f.write(table_tex(list(df['tex']), [0.3, 0.3, 0.1, 0.1, 0.1, 0.1]))


def venue_aggregation_tex(row):
    venue_tex = '%s, %s' % (clean_text(row['venue_name']), row['city'])
    stats = [row['count'], int(row['jimmy_stewart']), int(row['with_lyrics']), int(row['hof'])]
    stats_tex = '\\quad'.join([str(s) for s in stats])
    show_dates = row['show_dates'].split(',')
    show_dates = [datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d-%y') for date  in show_dates]
    dates_tex = '\n'.join(show_dates)
    return '\\VenueSummary{%s}{%s}{%s}' % (venue_tex, stats_tex, dates_tex)


def compile_venue_aggregation(credential):
    df = sql_util.query('sql/venue_aggregation.sql', credential)
    df = df.fillna(0)  # venues where all shows have no known setlist
    df['tex'] = df.apply(lambda x: venue_aggregation_tex(x), axis=1)
    with open('tex/venue_aggregation.tex', 'w') as f:
        f.write('\n'.join(df['tex']))


def support_tex(row):
    show_dates = row['show_dates'].split(',')
    show_dates = [datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d-%y') for date  in show_dates]
    venue_names = row['venue_names'].split(',')
    venue_names = [short_text(clean_text(name), 30) for name in venue_names]
    return list(zip(*[show_dates, venue_names]))


def compile_support(credential):
    df = sql_util.query('sql/support.sql', credential)
    df['tex'] = df.apply(lambda x: support_tex(x), axis=1)
    with open('tex/support.tex', 'w') as f:
        for _, row in df.iterrows():
            support = clean_text(row['opener'])
            table = table_tex(list(row['tex']), [0.25, 0.75])
            f.write('\\SupportSummary{%s}{%s}' % (support, table))


def main(credential: sql_util.Credentials):
    compile_song_codes(credential)
    compile_songs_played(credential)
    compile_setlists(credential)
    compile_songs_by_year(credential)
    compile_every_time_played(credential)
    compile_hall_of_fame(credential)
    compile_jimmy_stewart(credential)
    compile_state_aggregation(credential)
    compile_venue_aggregation(credential)
    compile_support(credential)


if __name__ == "__main__":
    parser = sql_util.Credentials.argparser()
    main(sql_util.Credentials.from_args(parser.parse_args()))
