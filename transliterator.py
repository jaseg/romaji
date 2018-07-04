#!/usr/bin/env python3
import sqlite3
import romkan

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('results_db', nargs='?', default='results.sqlite3', help='Database of words to transliterate produced by extractor.py')
    args = parser.parse_args()

    db = sqlite3.connect(args.results_db)

    for kanji, reading, glosses, part_of_speech in db.execute('SELECT kanji, reading, glosses, part_of_speech FROM unique_results'):
        print(kanji, reading, romkan.to_hepburn(reading))
           'ぁあぃいぅうぇえぉおかがきぎく'\
           'ぐけげこごさざしじすずせぜそぞた'\
           'だちぢっつづてでとどなにぬねのは'\
           'ばぱひびぴふぶぷへべぺほぼぽまみ'\
           'むめもゃやゅゆょよらりるれろゎわ'\
           'ゐゑをんゔゕゖ゛゜ゝゞゟ'
