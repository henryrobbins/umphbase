import string
import pandas as pd
from typing import List, Dict, Union, Optional


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
ENGLISH_RANK = {words[i]: i for i in range(len(words))}


def is_valid_code(code: str, max_length: int, tight: bool = True) -> bool:
    """Return true iif this is a valid song code.

    Args:
        code (str): Potential song code.
        max_length (int): Maximum number of characters in a valid song code.
        tight (bool): Restrict range of valid lengths. Defaults to True.

    Returns:
        bool: True if this song code is valid; false otherwise.
    """
    lb = max_length - 1 if tight else 1
    ub = max_length
    return (all([c in VALID_CHARS for c in code]) &
            (len(code) in range(lb, ub + 1)))


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
    return [new if x == old else x for x in lst]


def clean_title(title: str) -> str:
    """Return the song title after it is cleaned."""
    # lower case and remove invalid chars
    title = title.lower()
    title = title.replace(' & ', ' n ')
    title = title.replace("/", ' ')
    title = title.replace("-", ' ')
    title = ''.join([i for i in title if i in VALID_CHARS + [' ']])

    # abbreviations
    abbreviations = {'chapter': 'ch',
                     'cross': 'x',
                     'avenue': 'ave',
                     'example': 'ex',
                     'birthday': 'bday',
                     'doctor': 'dr',
                     'halloween': 'halow'}
    for k, v in abbreviations.items():
        title = title.replace(k, v)

    title = title.split()

    # word replacement abbreviations
    abbreviations = {'and': 'n'}
    for k, v in abbreviations.items():
        title = replace(k, str(v), title)

    # map string numbers
    for k, v in TENS.items():
        title = replace(k, str(v), title)
    for k, v in UNITS.items():
        title = replace(k, str(v), title)

    title = '<' + ' '.join(title) + '>'
    title = title.split()

    # roman numerals -> digits
    title = replace('i>', '1', title)
    title = replace('ii>', '2', title)
    title = replace('iii>', '3', title)

    title = ' '.join(title)
    title = title.strip('<>')

    return title


def get_acronym(words: List[str], max_length, prune=False) -> str:
    """Return acronym of for the first [max_length] words."""
    if prune:
        tmp = "".join([w[0] for w in words if word_rank(w) > 10])
    else:
        tmp = "".join([w[0] for w in words])
    return tmp[:max_length]


def remove_vowels(word: str) -> str:
    """Remove vowels (except for the first letter) from the given word."""
    if len(word) == 0:
        return ''
    else:
        return word[0] + "".join([c for c in word[1:] if c not in VOWELS])


def remove_letters(word: str) -> str:
    """Remove any letters from the given word."""
    return ''.join([c for c in word if c in NUMBERS])


def remove_numbers(word: str) -> str:
    """Remove any numbers from the given word."""
    return ''.join([c for c in word if c not in NUMBERS])


def generate_code(title: str,
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

    def short_name_code() -> Optional[str]:
        """Return a code for a song with a short name."""
        code = name.replace(' ', '')
        if is_valid_code(code, max_length, tight=False):
            return code
        code = remove_vowels(code)
        if ((len(name) < max_length + 3) & (is_valid_code(code, max_length))):
            return code
        return None

    def all_number_code() -> Optional[str]:
        """Return all number code for a song if it contains enough numbers."""
        code = remove_letters(name)
        if is_valid_code(code, max_length):
            return code
        return None

    def part_number_code() -> Optional[str]:
        """Return a code which contains some numbers."""
        nums = remove_letters(name)
        if (len(nums) in [1, 2]):
            no_numbers = remove_numbers(name)
            if (len(no_numbers) > 0):
                sub_code = generate_code(no_numbers,
                                         max_length - len(nums),
                                         word_title_freq,
                                         blacklist)
                if isinstance(sub_code, str):
                    return sub_code + nums
        return None

    def acronym_code(prune: bool) -> Optional[str]:
        """Return an acronym code; common words excluded if prune is true."""
        if (((prune) & (len(words) > max_length)) |
            ((not prune) & (len(words) in range(max_length-1, max_length+1)))):
            code = get_acronym(words, max_length, prune=prune)
            if is_valid_code(code, max_length, tight=False):
                return code
        return None

    def unique_title_word_code(word: str, vowels: bool) -> Optional[str]:
        """Return a code that is a unique title word."""
        if (word_title_freq(word) == 1):
            code = word if vowels else remove_vowels(word)
            if is_valid_code(code, max_length):
                return code
        return None

    def unique_english_word_code(word: str, vowels: bool) -> Optional[str]:
        """Return a code that is a unique title word."""
        if (word_rank(word) > 2000):
            code = word if vowels else remove_vowels(word)
            if is_valid_code(code, max_length):
                return code
        return None

    def letters_code(word: str, first: bool) -> Optional[str]:
        """Return a code that is comprised of letters in a word."""
        code = word[:max_length] if first else word[-max_length:]
        if is_valid_code(code, max_length, tight=False):
            return code
        return None

    attempts = (
        [short_name_code()] +
        [all_number_code()] +
        [part_number_code()] +
        [acronym_code(prune=True)] +
        [unique_title_word_code(w, False) for w in words_by_name_freq] +
        [unique_english_word_code(w, False) for w in words_by_freq] +
        [unique_title_word_code(w, True) for w in words_by_name_freq] +
        [unique_english_word_code(w, True) for w in words_by_freq] +
        [acronym_code(prune=False)] +
        [letters_code(w, True) for w in words_by_length] +
        [letters_code(w, False) for w in words_by_length])

    attempts = [code for code in attempts if code is not None]
    for code in attempts:
        if code not in blacklist:
            return code

    return attempts


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
                    new_code = generate_code(blocking_title,
                                             max_length,
                                             word_title_freq,
                                             blacklist)
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
