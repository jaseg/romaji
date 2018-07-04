#!/usr/bin/env python3
import sqlite3
from itertools import groupby
import tqdm
import re

hiragana =   'ぁあぃいぅうぇえぉおかがきぎく'\
           'ぐけげこごさざしじすずせぜそぞた'\
           'だちぢっつづてでとどなにぬねのは'\
           'ばぱひびぴふぶぷへべぺほぼぽまみ'\
           'むめもゃやゅゆょよらりるれろゎわ'\
           'ゐゑをんゔゕゖ゛゜ゝゞゟ'

katakana = '゠ァアィイゥウェエォオカガキギク'\
           'グケゲコゴサザシジスズセゼソゾタ'\
           'ダチヂッツヅテデトドナニヌネノハ'\
           'バパヒビピフブプヘベペホボポマミ'\
           'ムメモャヤュユョヨラリルレロヮワ'\
           'ヰヱヲンヴヵヶヷヸヹヺ・ーヽヾヿ'

def load_words(filename):
    with open(filename, encoding='euc_jisx0213') as f:
        for line in f:
            if not line.strip() or line[0] == '#':
                continue

            word, _, frequency = line.partition('\t')
            if int(frequency) < 100:
                continue

            yield word

def word_type(word):
    if all(c not in hiragana and c not in katakana for c in word):
        return 'kanji'
    if all(c in hiragana or c in katakana for c in word):
        return 'kana'
    return 'mixed'

def fetch_readings_and_pos(wordtype_dbfile, words):
    type_db = sqlite3.connect(wordtype_dbfile)
    tq = tqdm.tqdm(words)
    for word in tq:
        results = []
        for result in type_db.execute('SELECT readings, GROUP_CONCAT(glosses), GROUP_CONCAT(part_of_speech) FROM wordtypes WHERE kanji=?1 OR readings=?1 GROUP BY readings', (word,)):
            results.append(result)
        tq.write(f'{word} {result}')
        yield (word, results)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', default='wordfreq_ck', nargs='?', help='Giardi/Kelly Newspaper Word Frequency List (http://ftp.monash.edu.au/pub/nihongo/wordfreq_ck.gz)')
    parser.add_argument('wordtype_db', default='wordtype.sqlite3', nargs='?', help="Word type sqlite database extracted from JMDict XML using jaseg's JMDict python module")
    args = parser.parse_args()


    words = list(load_words(args.infile))
    kanji_words, kana_words, mixed_words = [list(g) for k, g in groupby(sorted((word_type(w), w) for w in words), key=lambda e: e[0])]
    print(f'Loaded {len(words)} words: {len(kanji_words)} kanji-only, {len(kana_words)} kana-only, {len(mixed_words)} mixed')

    words_dict = fetch_readings_and_pos(args.wordtype_db, words)
    unambiguous_words = [(word, results[0]) for word, results in words_dict if len(results) == 1]
    print(f'{len(unambiguous_words)} unambiguous results found')

    result_db = sqlite3.connect('results.sqlite3')
    with result_db as conn:
        conn.execute('DROP TABLE IF EXISTS unique_results')
        conn.execute('CREATE TABLE unique_results(kanji, reading, glosses, part_of_speech)')
        for word, (reading, glosses, part_of_speech) in unambiguous_words:
            cleanup = lambda s: re.sub(r' *,[ ,]*', ',', s)
            conn.execute('INSERT INTO unique_results VALUES (?, ?, ?, ?)', (word, reading, cleanup(glosses), cleanup(part_of_speech)))

