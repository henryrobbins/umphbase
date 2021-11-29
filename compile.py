import math
import pandas as pd
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
               '>' : '\\textgreater',
               '->' : '\\textrightarrow'}


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


def table_tex(table: List[List[str]], widths: List[str]):
    rows = [''.join('\\cell{%s}{%s}' % (widths[i], row[i]) for i in range(len(row))) for row in table]
    return '\\newline\n'.join(rows)


def song_tex(song_id: int, jimmy_stewart: bool, with_lyrics: bool, hof: bool, text: str=None, superscript: bool=True) -> str:
    if text is None:
        text = ID_TO_CODE[song_id]
    special = [jimmy_stewart, with_lyrics, hof]
    if any(special):
        if superscript:
            ss = ''.join([SPECIAL_KEYS[i] for i in range(3) if special[i]])
            return '\\textbf{%s\\textsuperscript{%s}}' % (text, ss)
        else:
            return '\\textbf{%s}' % text
    else:
        return text


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
        f.write('\\begin{multicols*}{3}\n')
        f.write('\\setlength{\columnseprule}{0.4pt}\n')
        f.write('\\noindent\n')
        f.write(table_tex(list(df['tex']), ['4cm', '0.5cm']))
        f.write('\\end{multicols*}\n')


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
        f.write('\\noindent\n')
        f.write(table_tex(list(df['tex']), ['7cm', '2cm', '7cm', '2cm', '2cm']))


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
    for song_id in every_time_played_by_song.keys():
        name = clean_text(song_id_to_name[song_id])
        table = table_tex(every_time_played_by_song[song_id], ['1.3cm', '1.3cm', '0.3cm', '0.4cm', '1.2cm'])
        with open('tex/every_time_played/%d.tex' % song_id, 'w') as f:
            f.write('\\begin{center}\\textbf{%s}\\end{center}\n' % name)
            f.write('\\noindent\n')
            f.write(table)

    with open('tex/every_time_played.tex', 'w') as f:
        f.write('\\begin{multicols*}{4}')
        f.write('\\setlength{\columnseprule}{0.4pt}')
        f.write('\\begin{scriptsize}')
        for song_id in every_time_played_by_song.keys():
            f.write('\\input{every_time_played/%s}\n' % song_id)
        f.write('\\end{scriptsize}')
        f.write('\\end{multicols*}')


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
        f.write('\\begin{multicols*}{3}')
        f.write('\\setlength{\columnseprule}{0.4pt}')
        f.write('\\noindent\n')
        f.write(table_tex(list(df['tex']), ['1.5cm', '4.5cm']))
        f.write('\\end{multicols*}')


def main(credential: sql_util.Credentials):
    compile_song_codes(credential)
    compile_songs_played(credential)
    compile_every_time_played(credential)
    compile_hall_of_fame(credential)


if __name__ == "__main__":
    parser = sql_util.Credentials.argparser()
    main(sql_util.Credentials.from_args(parser.parse_args()))
