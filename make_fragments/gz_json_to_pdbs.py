#!/usr/bin/env python
"""

mainly for debugging/curiosity, very simple script :D

"""

import gzip
import json
import pathlib
import os


def main():
    with gzip.open("casp_12-13.json.gz", 'rt') as fh:
        json_data = json.loads(fh.read())
    for db_name, db_data in json_data.items():
        for target_name, target_data in db_data.items():
            target_loc = os.path.join(db_name, target_name)
            pathlib.Path(target_loc).mkdir(exist_ok=True, parents=True)
            target_pdb = os.path.join(target_loc, f"{target_name}.pdb")
            with open(target_pdb, 'w') as fh:
                fh.write(target_data["pdb_text"])


if __name__ == "__main__":
    main()
