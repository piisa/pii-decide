"""
Test the SimpleOverlapDecider class
"""

from pathlib import Path
from itertools import zip_longest
import json

from typing import Dict

from pii_data.types.piicollection import PiiCollectionLoader
from pii_data.types import PiiEnum
from pii_data.types.piicollection import PiiChunkIterator



import pii_decide.deciders.overlap_simple as mod


def datafile(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name

def load_datafile(name: str) -> Dict:
    with open(datafile(name)) as f:
        return json.load(f)


def test10_constructor():
    """
    Test constructing an object
    """
    m = mod.SimpleOverlapDecider()
    assert str(m) == "<SimpleOverlapDecider>"


def test20_decide_no_overlap():
    """
    Test decision, no overlap
    """
    piic = PiiCollectionLoader()
    piic.load(datafile("pii_no_overlap.json"))
    detectors = piic.get_detectors(asdict=True)

    dec = mod.SimpleOverlapDecider(None)

    exp_list = [
        [
            (PiiEnum.PERSON,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection', 'score': 0.85}]}),
            (PiiEnum.PHONE_NUMBER,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]}),
            (PiiEnum.IP_ADDRESS,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]})
        ],
        [
            (PiiEnum.PERSON,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection', 'score': 0.85}]}),
            (PiiEnum.OTHER,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection', 'score': 0.85}]}),
            (PiiEnum.EMAIL_ADDRESS,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]})
        ],
        [
            (PiiEnum.CREDIT_CARD,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]}),
            (PiiEnum.BLOCKCHAIN_ADDRESS,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]})
        ]
    ]
    for exp, pii_chunk in zip_longest(exp_list, PiiChunkIterator(piic)):
        got = list(dec(pii_chunk, None, detectors))
        got_pii = [(e.info.pii, e.fields["process"]) for e in got]
        assert exp == got_pii


def test21_decide_overlap():
    """
    Test decision, overlap
    """
    piic = PiiCollectionLoader()
    piic.load(datafile("pii_overlap_in.json"))
    detectors = piic.get_detectors(asdict=True)

    dec = mod.SimpleOverlapDecider(None)

    exp_list = [
        # First chunk: we keep the 2nd PII, which is longer that the 1st
        [
            (PiiEnum.PERSON,
             {'stage': 'decision', 'action': 'discard', 'reason': 'overlap',
              'history': [{'stage': 'detection', 'score': 0.85}]}),
            (PiiEnum.PHONE_NUMBER,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]}),
            (PiiEnum.IP_ADDRESS,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]})
        ],
        # Second chunk: we keep the 1st PII (same length, comes before) and
        # discard the 2nd. Then we can keep the 3rd
        [
            (PiiEnum.PERSON,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection', 'score': 0.85}]}),
            (PiiEnum.OTHER,
             {'stage': 'decision', 'action': 'discard', 'reason': 'overlap',
              'history': [{'stage': 'detection', 'score': 0.85}]}),
            (PiiEnum.EMAIL_ADDRESS,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]})
        ],
        # Third chunk: we keep the 1st (longest) and discard the 2nd & 3rd
        # (overlap with the 1st)
        [
            (PiiEnum.BLOCKCHAIN_ADDRESS,
             {'stage': 'decision', 'action': 'keep',
              'history': [{'stage': 'detection'}]}),
            (PiiEnum.CREDIT_CARD,
             {'stage': 'decision', 'action': 'discard', 'reason': 'overlap',
              'history': [{'stage': 'detection'}]}),
            (PiiEnum.PERSON,
             {'stage': 'decision', 'action': 'discard', 'reason': 'overlap',
              'history': [{'stage': 'detection'}]})
        ]
    ]
    for exp_chk, pii_chunk in zip_longest(exp_list, PiiChunkIterator(piic)):
        got = list(dec(pii_chunk, None, detectors))
        got_chk = [(e.info.pii, e.fields["process"]) for e in got]
        assert exp_chk == got_chk
