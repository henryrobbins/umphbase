import argparse
from ortools.linear_solver import pywraplp as OR
import pandas as pd
import re
from string import ascii_lowercase
from typing import Callable, Dict, Iterable, List, Optional, Set


NUMBERS = list('0123456789')
CHARS = list(ascii_lowercase)
VALID_CHARS = frozenset(CHARS + NUMBERS)
VALID_CHARS_AND_SPACE = frozenset(CHARS + NUMBERS + [' '])
vowel_but_not_first_re =  '(?!^)[aeiou]'  # Vowels not at beginning of a word

# https://stackoverflow.com/a/38760564
units = ["zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
UNITS = {unit: 19 - i for i, unit in enumerate(reversed(units))}
tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety"]
TENS = {tens[i]: i for i in range(2, len(tens))}
ordinals = ["first", "second", "third", "fourth", "fifth"]
ORDINALS = {ordinal: i + 1 for i, ordinal in enumerate(ordinals)}
multiples = ["single", "double", "triple", "quadruple", "quintuple"]
MULTIPLICATIVES = {multiple: i + 1 for i, multiple in enumerate(multiples)}

# used to measure how unique a words is
with open('data/common_english_words.txt') as f:
    ENGLISH_RANK = {word.rstrip(): i for i, word in enumerate(f)}


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
    return lb <= len(code) <= ub and all(c in VALID_CHARS for c in code)


def word_rank(word: str) -> int:
    """Return the rank of the word with lower rank being more frequent."""
    rank = ENGLISH_RANK.get(word, len(ENGLISH_RANK))
    # plural form of low rank words should be low rank
    if len(word) > 1 and word[-1] == 's':
        rank = min(rank, ENGLISH_RANK.get(word[:-1], len(ENGLISH_RANK)))
    return rank


def replace(old: str, new: str, lst: List[str]) -> List[str]:
    """Replace instances of old with new in the given list."""
    return [new if x == old else x for x in lst]


def clean_title(title: str) -> str:
    """Return the song title after it is cleaned."""
    # lower case and remove invalid chars
    title = title.lower()
    title = title.replace(' & ', ' n ')
    title = title.replace('/', ' ')
    title = title.replace('-', ' ')
    title = ''.join([i for i in title if i in VALID_CHARS_AND_SPACE])

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

    title_words = title.split()

    # word replacement abbreviations
    word_abbreviations: Dict[str, str] = {'and': 'n'}
    for k, v in word_abbreviations.items():
        title_words = replace(k, v, title_words)

    # map string numbers
    for swaps in [TENS, UNITS, ORDINALS, MULTIPLICATIVES]:
        for k, v in swaps.items():
            title_words = replace(k, str(v), title_words)

    title = ' '.join(title_words)
    title = re.sub('iii$', '3', title)
    title = re.sub('ii$', '2', title)
    title = re.sub('i$', '1', title)

    return title


def get_acronym(words: List[str], max_length, prune=False) -> str:
    """Return acronym of for the first [max_length] words."""
    if prune:
        acronym = "".join([w[0] for w in words if word_rank(w) > 10])
    else:
        acronym = "".join([w[0] for w in words])
    return acronym[:max_length]


def remove_vowels(word: str) -> str:
    """Remove vowels (except for the first letter) from the given word."""
    return re.sub(vowel_but_not_first_re, '', word)


def remove_letters(word: str) -> str:
    """Remove any letters from the given word."""
    return re.sub('\D', '', word)


def remove_numbers(word: str) -> str:
    """Remove any numbers from the given word."""
    return re.sub('\d', '', word)


def code_attempts(title: str,
                  max_length: int,
                  word_title_freq: Callable[[str], int]) -> List[str]:
    """Return a list of potential song codes ordered by preference."""
    name = clean_title(title)
    words = name.split()
    words_by_freq = sorted(words, key=word_rank, reverse=True)
    words_by_name_freq = sorted(words, key=word_title_freq)
    words_by_length = sorted(words, key=len, reverse=True)

    def short_name_code() -> Optional[str]:
        """Return a code for a song with a short name."""
        code = name.replace(' ', '')
        if is_valid_code(code, max_length, tight=False):
            return code
        code = remove_vowels(code)
        if len(name) < max_length + 3 and is_valid_code(code, max_length):
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
        if len(nums) in [1, 2]:
            no_numbers = remove_numbers(name)
            if len(no_numbers):
                sub_code = code_attempts(no_numbers,
                                         max_length - len(nums),
                                         word_title_freq)[0]
                try:
                    if name.index(nums) < len(name) / 2:
                        return nums + sub_code
                    else:
                        return sub_code + nums
                except ValueError:
                    return sub_code + nums
        return None

    def acronym_code(prune: bool) -> Optional[str]:
        """Return an acronym code; common words excluded if prune is true."""
        if ((prune and len(words) > max_length) or
            (not prune and max_length - 1 <= len(words) <= max_length)):
            code = get_acronym(words, max_length, prune=prune)
            if is_valid_code(code, max_length, tight=False):
                return code
        return None

    def unique_title_word_code(word: str, vowels: bool) -> Optional[str]:
        """Return a code that is a unique title word."""
        if word_title_freq(word) == 1:
            code = word if vowels else remove_vowels(word)
            if is_valid_code(code, max_length):
                return code
        return None

    def unique_english_word_code(word: str, vowels: bool) -> Optional[str]:
        """Return a code that is a unique title word."""
        if word_rank(word) > 2000:
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

    possible_attempts: List[Optional[str]] = [
        short_name_code(),
        all_number_code(),
        part_number_code(),
        acronym_code(prune=True),
        *(unique_title_word_code(w, True) for w in words_by_name_freq),
        *(unique_english_word_code(w, True) for w in words_by_freq),
        *(unique_title_word_code(w, False) for w in words_by_name_freq),
        *(unique_english_word_code(w, False) for w in words_by_freq),
        acronym_code(prune=False),
        *(letters_code(w, True) for w in words_by_length),
        *(letters_code(w, False) for w in words_by_length)]

    attempts: Iterable[str] = filter(None, possible_attempts)
    unique_attempts: List[str] = list(dict.fromkeys(attempts))  # remove duplicates

    return unique_attempts


def assignment(titles: Iterable[str], codes: Iterable[str], edges):
    """A model for assigning song titles to valid song codes."""
    TITLES = titles       # song titles
    CODES = codes         # potential codes
    EDGES = list(edges)   # edges between feasible title, code pairs
    c = edges             # cost of edges

    m = OR.Solver('assignment', OR.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # decision variables
    x = {}
    for i, j in EDGES:
        x[i, j] = m.IntVar(0, m.infinity(), ('(%s, %s)' % (i, j)))

    # objective function
    m.Minimize(sum(c[i, j] * x[i, j] for i, j in EDGES))

    # each title must be assigned exactly one code
    for k in TITLES:
        m.Add(sum(x[i, j] for i, j in EDGES if i == k) == 1)

    # a code can be used at most one time
    for k in CODES:
        m.Add(sum(x[i, j] for i, j in EDGES if j == k) <= 1)

    if m.Solve() == 2:
        raise ValueError("Unable to generate unique codes.")

    return {title: code for (title, code), xval in x.items()
            if xval.solution_value() > 0.5}


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
        rank = title_frequency.get(word, len(title_frequency))
        # account for plural form
        if len(word) > 1 and word[-1] == 's':
            rank = max(rank, title_frequency.get(word[:-1], len(title_frequency)))
        return rank

    title_to_attempts: Dict[str, List[str]] = {}
    all_attempts: Set[str] = set()
    for _, row in songs.iterrows():
        title = row['name']
        attempts = code_attempts(title, max_length, word_title_freq)
        if int(row['original']):
            attempts = list(map(str.upper, attempts))
        title_to_attempts[title] = attempts
        all_attempts.update(attempts)

    edges = {}
    for title, attempts in title_to_attempts.items():
        for i, attempt in enumerate(attempts):
            edges[title, attempt] = 10**i

    result = assignment(songs['name'], all_attempts, edges)

    return result

def main(songs_path: str, codes_path: str, n: int):
    """Generate length n codes for songs at path and write them to codes_path.

    Args:
        songs_path (str): Path to songs (.pickle).
        codes_path (str): Path where codes should be written.
        length (int): Length of the codes to generate.
    """
    songs_df = pd.read_pickle(songs_path)
    codes_df = pd.DataFrame.from_dict(generate(songs_df, n), orient='index',
            columns=['code'])
    result_df = songs_df.merge(codes_df, left_on='name', right_index=True,
            how='left')[['song_id', 'code']]
    result_df.to_csv(codes_path, index=0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--songs_path', required=True, help="Path to songs")
    parser.add_argument('-c', '--codes_path', required=True, help="Path to write codes to")
    parser.add_argument('-l', '--length', type=int, required=True, help="Code length")
    args = parser.parse_args()
    main(args.songs_path, args.codes_path, args.length)
