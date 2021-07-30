import string
import pandas as pd
from typing import List, Dict, Union


NUMBERS = list('0123456789')
CHARS = list(string.ascii_lowercase)
VALID_CHARS = CHARS + NUMBERS
VOWELS = list('aeiou')

# https://stackoverflow.com/a/38760564
units = ["zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
units.reverse()
UNITS = {units[i]: 19-i for i in range(len(units))}
tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety"]
TENS = {tens[i]: i for i in range(2, len(tens))}


# used to measure how unique a words is
with open('data/common_english_words.txt') as f:
    words = [w.rstrip() for w in f.readlines()]
ENGLISH_RANK = {words[i] : i for i in range(len(words))}


def is_valid_code(code: str, lb: int, ub: int, blacklist: List[str]) -> bool:
    return (all([c in VALID_CHARS for c in code]) &
            (len(code) in range(lb, ub + 1)) &
            (code not in blacklist))


def word_rank(word: str) -> int:
    """Return the rank of the word with lower rank being more frequent."""
    if word in ENGLISH_RANK:
        rank = ENGLISH_RANK[word]
    else:
        rank = len(ENGLISH_RANK)
    # plural form of low rank words should be low rank
    if ((len(word) > 1) & (word[-1] == 's')):
        return min(rank, word_rank(word[:-1]))
    return rank


def replace(old: str, new: str, lst: List[str]) -> List[str]:
    """Replace instances of old with new in the given list."""
    return [new if x==old else x for x in lst]


def clean_title(title: str) -> str:
    """Return the song title after it is cleaned."""
    # lower case and remove invalid chars
    title = title.lower()
    title = title.replace(' & ', ' n ')
    title = title.replace("/", ' ')
    title = title.replace("-", ' ')
    title = ''.join([i for i in title if i in VALID_CHARS + [' ']])

    # abbreviations
    abbreviations = {'chapter' : 'ch',
                     'cross' : 'x',
                     'avenue' : 'ave',
                     'example': 'ex',
                     'birthday': 'bday',
                     'doctor': 'dr',
                     'halloween': 'halow'}
    for k, v in abbreviations.items():
        title = title.replace(k,v)

    title = title.split()

    # word replacement abbreviations
    abbreviations = {'and' : 'n'}
    for k, v in abbreviations.items():
        title = replace(k, str(v), title)

    # map string numbers
    for k, v in TENS.items():
        title = replace(k, str(v), title)
    for k, v in UNITS.items():
        title = replace(k, str(v), title)
    title = replace('fortysix', '46', title)

    title = '<' + ' '.join(title) + '>'
    title = title.split()

    # roman numerals -> digits
    title = replace('i>', '1', title)
    title = replace('ii>', '2', title)
    title = replace('iii>', '3', title)

    title = ' '.join(title)
    title = title.strip('<>')

    return title


def generate_code(
    title: str,
    max_length: int,
    word_title_freq,
    blacklist: List[str]) -> Union[str, List[str]]:
    """
    Generate a code for the given song title. If none of generated codes are
    validated, return the ordered list of attempted codes.
    """
    name = clean_title(title)
    words = name.split()
    words_by_freq = sorted(words, key=lambda x: word_rank(x), reverse=True)
    words_by_name_freq = sorted(words, key=lambda x: word_title_freq(x))
    words_by_length = sorted(words, key=lambda x: len(x), reverse=True)

    tried = []  # attempted codes

    # x characters or less (without spaces)
    word = name.replace(' ', '')
    tried.append(word)
    if is_valid_code(word, 1, max_length, blacklist):
        return word
    else:
        code = word[0] + "".join([c for c in word[1:] if c not in VOWELS])
        tried.append(code)
        if ((len(word) < max_length + 3) & (is_valid_code(code, max_length - 1, max_length, blacklist))):
            return code

    # exactly x numbers
    code = ''.join([i for i in name if i in NUMBERS])
    tried.append(code)
    if is_valid_code(code, max_length - 1, max_length, blacklist):
        return code

    # 1 or 2 numbers
    code = ''.join([i for i in name if i in NUMBERS])
    size = len(code)
    if (size in [1,2]):
        no_numbers = ''.join([i for i in name if i not in NUMBERS])
        return generate_code(no_numbers, max_length - size, word_title_freq, blacklist) + code

    # First x letter acronym for songs with more than x words
    if (len(words) > max_length):
        code = "".join([w[0] for w in words if word_rank(w) > 10][:max_length])
        tried.append(code)
        if is_valid_code(code, 1, max_length, blacklist):
            return code

    # Contains word unique in all song names (x chars)
    for word in words_by_name_freq:
        tried.append(word)
        if ((word_title_freq(word) == 1) & (is_valid_code(word, max_length - 1, max_length, blacklist))):
            return word

    # Contains very unique word (x chars)
    for word in words_by_freq:
        if word in blacklist:
            tried.append(word)
            continue
        if (word_rank(word) > 2000) & (is_valid_code(word, max_length - 1, max_length, blacklist)):
            return word

    # Contains word unique in all song names (x chars no vowels)
    for word in words_by_name_freq:
        code = word[0] + "".join([c for c in word[1:] if c not in VOWELS])
        if code in blacklist:
            tried.append(word)
            continue
        if ((word_title_freq(word) == 1) & (is_valid_code(code, max_length - 1, max_length, blacklist))):
            return code

    # Contains very unique word (x chars no vowels)
    for word in words_by_freq:
        code = word[0] + "".join([c for c in word[1:] if c not in VOWELS])
        if code in blacklist:
            tried.append(word)
            continue
        if ((word_rank(word) > 100) & (is_valid_code(code, max_length - 1, max_length, blacklist))):
            return code

    # Acronym for songs with x words
    if (len(words) in range(max_length - 1, max_length + 1)):
        code = "".join([w[0] for w in words][:max_length])
        tried.append(code)
        if is_valid_code(code, 1, max_length, blacklist):
            return code

    # First x letters of longest word
    for word in words_by_length:
        code = word.replace(" ","")[:max_length]
        tried.append(code)
        if code in blacklist:
            continue
        else:
            return code

    # Last x letters of longest word
    for word in words_by_length:
        code = word.replace(" ","")[-max_length:]
        tried.append(code)
        if code in blacklist:
            continue
        else:
            return code

    return tried


def generate(songs: pd.DataFrame, max_length: int) -> Dict[str, str]:
    """Return a dictionary of song titles to codes under a specified length.

    Args:
        titles (List[str]): List of titles to generate codes for.
        max_length (int): Maximum number of characters in a valid code.

    Returns:
        Dict[str, str]: Dictionary from every song title to a unique code.
    """
    # keep track of the frequency of words in song names
    cleaned_titles = [x for s in songs['name'] for x in clean_title(s).split()]
    title_frequency = pd.Series(cleaned_titles).value_counts().to_dict()


    def word_title_freq(word: str) -> int:
        if word in title_frequency:
            rank = title_frequency[word]
        else:
            rank = len(title_frequency)
        # account for plural form
        if ((len(word) > 1) & (word[-1] == 's')):
            return min(rank, word_title_freq(word[:-1]))
        return rank


    song_to_code = {}
    code_to_song = {}
    blacklist = []
    for index, row in songs.iterrows():
        title = row['name']
        is_original = bool(int(row['original']))
        code_or_tried = generate_code(title, max_length, word_title_freq, blacklist)
        if isinstance(code_or_tried, list):
            tried = code_or_tried
            reassign_success = False
            for code in tried:
                if code in blacklist:
                    # re-assign the song currently assigned to this code
                    blocking_title = code_to_song[code]
                    new_code = generate_code(blocking_title, max_length, word_title_freq, blacklist)
                    if isinstance(new_code, list):
                        continue
                    song_to_code[blocking_title] = new_code
                    code_to_song[new_code] = blocking_title

                    # this code is now free to be assigned to the current code
                    song_to_code[title] = code
                    code_to_song[code] = title
                    reassign_success = True
                    break
            if not reassign_success:
                raise ValueError("Unable to generate unique codes.")
        else:
            code = code_or_tried
            code = str.upper(code) if is_original else code
            blacklist.append(code)
            song_to_code[title] = code
            code_to_song[code] = title

    return song_to_code
