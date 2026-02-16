import os, json, pprint, sys

with open("strings_db.json", "r", encoding="utf-8") as f:
    d: dict = json.load(f)
    all = {}
    for v in d.values():
        n = all.setdefault(v, 0)
        all[v] = n + 1

uniq = len(all)
if "" in all:
    uniq = uniq - 1

print(f"Unique strings: {uniq}")
if "" in all:
    print(f"Empty strings: {all['']}")

dupes = 0
dd = {}
for k, v in all.items():
    if v < 2 or k == "":
        continue
    dupes += 1
    dd.setdefault(v, []).append(k)

print(f"Found {dupes} duplicated strings.")
print(list(sorted(dd.keys(), reverse=True)))

if sys.argv[-1] == "-v":
    pprint.pprint(dd)
