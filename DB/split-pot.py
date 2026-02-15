"""Split POT file into chunks.

Every chunk has the following structure:

#. <<<comment as string internal ID>>>
msgctxt "context as string internal ID (same as above)"
msgid "English phrase"
msgstr ""

msgstr is always empty field inside POT file.

Chunks are separated by blank line.
"""

import os, sys
from typing import List
import json


FNAME = "strings_template.pot"


def main():
    db = {}
    chunks_db = {}
    with open(FNAME, "r", encoding="utf-8") as f:
        chunk = []
        for s in f:
            ss = s.rstrip()
            if not ss:
                if False:
                    print(chunk)
                    break
                else:
                    r = process_chunk(chunk, db, chunks_db)
                    if r is None:
                        print("Check script or POT file")
                        return 1
                    # if r is True:
                    #    break
                    chunk = []
            else:
                chunk.append(s.rstrip("\r\n"))
    if chunk:
        process_chunk(chunk)
    print(f"DB is collected: {len(db)} IDs found")
    empty = count_empty_english(db)
    print(f"Empty strings: {empty}")
    print("writing plain json")
    write_db_json(db, "strings_db.json")
    print("writing chunks json")
    write_db_json(chunks_db, "chunks_db.json")
    # convert to tree ids
    tdb = convert_to_tree_db(db)
    print("writing tree json")
    write_db_json(tdb, "strings_tree.json")
    print("writing tree on disk")
    write_db_on_disk(tdb, root_dir="TDB")
    print("done.")


def process_chunk(chunk: List[str], db: dict, chunks_db: dict):
    if not chunk:
        return False
    a: str = chunk[0]
    if a == 'msgid ""':
        print("skip first meta info chunk")
        return False
    # print(chunk)
    if len(chunk) != 4:
        print("Wrong chunk:")
        print(chunk)
        return None
    sp = {}
    for i in chunk:
        x = i.split(maxsplit=1)
        if len(x) != 2:
            print(f"Wrong line in chunk: {i}")
            print(chunk)
            return None
        key, value = x
        if len(value) >= 2:
            if value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
        sp[key] = value
    # print(sp)
    id1 = sp.get("#.")
    id2 = sp.get("msgctxt")
    if id1 is None or id2 is None:
        print("Chunk misses some ID string")
        print(chunk)
        return None
    if id1 != id2:
        print(f"Chunk has 2 different IDs: {id1} != {id2}")
        print(chunk)
        return None
    en = sp.get("msgid")
    if en is None:
        print("Chunk has no English text")
        print(chunk)
    # if en == "":
    #    print("Chunk has empty English text!")
    #    print(chunk)
    #    return False
    if id1 in db:
        print(f"Database is already containing ID {id1}: {db[id1]}")
        print(f"New text: {en}")
        return None
    tr = sp.get("msgstr")
    if tr:
        print(f"Chunk has got not empty msgstr: {tr}")
        print(chunk)
        return None
    db[id1] = en
    chunks_db[id1] = chunk
    return True


def count_empty_english(db: dict) -> int:
    n = 0
    for v in db.values():
        if not v:
            n += 1
    return n


def write_db_json(db: dict, fname: str):
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(db, f, sort_keys=True, indent=2)


def convert_to_tree_db(db: dict):
    tdb = {}
    for key, value in db.items():
        pk = key.split(".")
        di = tdb
        for i in pk[:-1]:
            di = di.setdefault(i, {})
        j = pk[-1]
        di[j] = value
    return tdb


def write_db_on_disk(tdb: dict, root_dir: str = "."):
    for key, value in tdb.items():
        if isinstance(value, dict):
            d = os.path.join(root_dir, key)
            os.makedirs(d, exist_ok=True)
            write_db_on_disk(value, d)
        else:
            fn = os.path.join(root_dir, key)
            with open(fn, "w", encoding="utf-8") as f:
                f.write(value)


if __name__ == "__main__":
    main()
