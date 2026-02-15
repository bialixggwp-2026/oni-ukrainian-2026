"""Create PO files based on source-config.json using chunks from chunks_db.json"""

import json, os
from typing import List, Tuple


def main():
    BASE_DIR = "source"
    CFG = "source-config.json"
    CHUNKS = "chunks_db.json"

    chunks: dict = json.load(open(CHUNKS, "r", encoding="utf-8"))
    cfg: dict = json.load(open(CFG, "r", encoding="utf-8"))

    all = len(chunks)
    nf, used = create_po_from_cfg(cfg, BASE_DIR, chunks)

    print(f"Created {nf} PO files using {used} of {all} chunks.")


def create_po_from_cfg(kfg: dict, root_dir: str, chunks_src: dict) -> Tuple[int, int]:
    os.makedirs(root_dir, exist_ok=True)
    m = 0
    nf = 0
    for k,v in kfg.items():
        p = os.path.join(root_dir, k)
        if isinstance(v, dict):
            x, y = create_po_from_cfg(v, p, chunks_src)
            nf += x
            m += y
        elif isinstance(v, list):
            n = write_po_file_from_chunks(p, v, chunks_src)
            m += n
            nf += 1
        else:
            print(f"Wrong format of config file: {k} -> {v}")
            break
    return nf, m


def write_po_file_from_chunks(fname: str, ids: List[str], chunks_src: dict) -> int:
    n = 0
    print(f"writing {fname}")
    with open(fname, "w", encoding="utf=8") as f:
        for i in ids:
            if not i:   # allow empty string as visual separator
                continue
            ch = chunks_src.get(i)
            if not ch:
                print(f"ERROR: chunks_db has no chunk with ID {i}")
                return n
            n += 1
            for s in ch:
                f.write(s)
                if not s.endswith("\n"):
                    f.write("\n")
            f.write("\n")
    return n


if __name__ == "__main__":
    main()
