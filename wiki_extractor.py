#!/usr/bin/env python3

import sqlite3
import re

if __name__ == '__main__':
    import argparse
    import tqdm
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('wiki_abstract_dump', help='Japanese Wikipedia XML abstract dump')
    parser.add_argument('sqlite_result_file', default='wiki_readings.sqlite3', nargs='?', help='SQLite database file to store results in')
    args = parser.parse_args()

    db = sqlite3.connect(args.sqlite_result_file)
    db.execute('DROP TABLE IF EXISTS wiki_readings')
    db.execute('CREATE TABLE wiki_readings (kanji, reading)')
    db.execute('CREATE INDEX IF NOT EXISTS kanji_reading_index ON wiki_readings(kanji)')

    pat = re.compile('<abstract>([^（]+)（([^）]+)）') # Caution, this pattern contains both japanese parentheses, which are ignored by re, and ASCII parentheses.

    size = os.path.getsize(args.wiki_abstract_dump)
    tq = tqdm.tqdm(total=size)
    with open(args.wiki_abstract_dump) as f:
        last, this = 0, 0
        while True:
            # Use this workaround instead of just iterating for tell() to work.
            line = f.readline()
            if not line:
                break

            last, this = this, f.tell()
            tq.update(this - last)

            if not line.startswith('<abstract>'):
                continue
            
            m = pat.match(line)
            if not m:
                continue
            
            kanji, readings = m.groups()
            tq.write(f'{kanji} {readings}')
            for reading in readings.split('、'):
                db.execute('INSERT INTO wiki_readings VALUES (?, ?)', (kanji, reading))

    db.commit()

