"""
Test the PiiDecider class
"""

from pathlib import Path
import os
import json
import tempfile

from typing import Dict

from pii_data.types.piicollection import PiiCollectionLoader

import pii_decide.api.decider as mod


def datafile(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name

def load_datafile(name: str) -> Dict:
    with open(datafile(name)) as f:
        return json.load(f)


def test10_constructor():
    """
    Test constructing an object
    """
    mod.PiiDecider()


def test30_decide_doc_overlap():
    """
    Test decision, overlap, full document
    """
    piic_in = PiiCollectionLoader()
    piic_in.load(datafile("pii_overlap_in.json"))

    dec = mod.PiiDecider()

    piic_out = dec(piic_in)

    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            piic_out.dump(f, format="json")
            f.close()

            with open(f.name, encoding="utf-8") as f2:
                got = json.load(f2)
    finally:
        os.unlink(f.name)

    with open(datafile("pii_overlap_out.json"), encoding="utf-8") as f:
        exp = json.load(f)

    assert got == exp


def test30_decide_chunk_overlap():
    """
    Test decision, overlap, chunk processing
    """
    piic_in = PiiCollectionLoader()
    piic_in.load(datafile("pii_overlap_chunk_in.json"))

    dec = mod.PiiDecider()
    piic_out = dec.decide_chunk(piic_in)


    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            piic_out.dump(f, format="json")
            f.close()
            with open(f.name, encoding="utf-8") as f2:
                got = json.load(f2)
    finally:
        os.unlink(f.name)

    with open(datafile("pii_overlap_chunk_out.json"), encoding="utf-8") as f:
        exp = json.load(f)

    assert got == exp
