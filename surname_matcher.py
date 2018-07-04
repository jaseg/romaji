#!/usr/bin/env python3

HIRAGANA =   'ぁあぃいぅうぇえぉおかがきぎく'\
           'ぐけげこごさざしじすずせぜそぞた'\
           'だちぢっつづてでとどなにぬねのは'\
           'ばぱひびぴふぶぷへべぺほぼぽまみ'\
           'むめもゃやゅゆょよらりるれろゎわ'\
           'ゐゑをんゔゕゖ゛゜ゝゞゟ'

if __name__ == '__main__':
    import argparse
    import sqlite3
    import re

    parser = argparse.ArgumentParser()
    parser.add_argument('name_file', help='Input file of Japanese names, format [kanji]\t[frequency]')
    parser.add_argument('wiki_reading_db', nargs='?', default='wiki_readings.sqlite3', help='SQLite3 database containing Japanese words and their readings generated from a wikipedia.jp abstract dump by wiki_extractor.py')
    args = parser.parse_args()

    reading_db = sqlite3.connect(args.wiki_reading_db)
    cur = reading_db.cursor()

    with open(args.name_file) as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue

            name, _, extra = line.strip().partition('\t')
            results = cur.execute('SELECT reading FROM wiki_readings WHERE kanji=? LIMIT 1', (name,)).fetchall()
            #foo = ','.join(reading for reading, in results)
            
            reading = None
            if results:
                (reading,), = results
            else:
                results = cur.execute('SELECT reading, COUNT(*) AS count FROM wiki_readings WHERE kanji LIKE ? GROUP BY reading ORDER BY count DESC', (f'{name} %',)).fetchall()
                if results:
                    results = [reading for reading, count in results if all(c in HIRAGANA or c == ' ' for c in reading)]
                    if results:
                        reading, *_rest = results
                    
            if reading:
                reading = re.split('[／・/ ]', reading)[0]

            print(f'{name}\t{reading}\t{extra}')

