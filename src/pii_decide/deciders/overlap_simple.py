"""
Decide between overlapping PII instances, by just comparing their spans
"""

from typing import Iterable, Union, Dict, List

from pii_data.types import PiiEntity
from pii_data.types.doc import DocumentChunk
from pii_data.types.piicollection.collection import TYPE_DET_DICT
from pii_data.helper.peeker import IterationPeeker

from .. import defs
from ..helper.misc import get_action, set_action



def resolve_overlaps(pii: List[PiiEntity]) -> Iterable[PiiEntity]:
    """
    Take a list of overlapping PII and decide which to keep
    and which to ignore
      :return: an iterable over the PII instances, each one updated with
        a decision action
    """
    # Build a list of PII features
    order_desc = [[n, i.pos, len(i), defs.ACT_KEEP] for n, i in enumerate(pii)]

    # Sort by length, then by position
    sorted_desc = sorted(order_desc, key=lambda e: (-e[2], e[1]))

    # Mark any instance that overlaps with a previous one in the sorted list
    for n, elem in enumerate(sorted_desc[1:], start=1):
        for p in sorted_desc[:n]:
            if elem[1] <= p[1] + p[2] and p[3] == defs.ACT_KEEP:
                elem[3] = defs.ACT_DISCARD
                break

    # Iterate over the results, setting the proper action
    for elem in order_desc:
        p = pii[elem[0]]
        data = {"reason": "overlap"} if elem[3] == defs.ACT_DISCARD else {}
        set_action(p, elem[3], **data)
        yield p


# ------------------------------------------------------------------------


class SimpleOverlapDecider:

    def __init__(self, config: Union[Dict, str] = None):
        self.config = config


    def __repr__(self) -> str:
        return '<SimpleOverlapDecider>'


    def __call__(self, pii_list: Iterable[PiiEntity], detectors: TYPE_DET_DICT,
                 chunk: DocumentChunk = None) -> Iterable[PiiEntity]:
        """
        Take a list of PII instances corresponding to a document chunk,
        and return it with updated decisions
        """
        pii_list = IterationPeeker(pii_list)
        for pii_curr in pii_list:

            # If this one is already ignored, skip further processing
            curr_action = get_action(pii_curr)
            if curr_action == defs.ACT_DISCARD:
                yield pii_curr
                continue

            # Check the next one
            end_pos = pii_curr.pos + len(pii_curr)
            pii_next = pii_list.peek()

            # no problem? (no next, next is already ignored, or no overlap)
            if (not pii_next or pii_next.pos > end_pos
                    or get_action(pii_next) == defs.ACT_DISCARD):
                set_action(pii_curr, defs.ACT_KEEP)
                yield pii_curr
                continue

            # Create a list with all the overlapping PII instances
            pii = [pii_curr]
            while True:
                pii_next = pii_list.peek()
                if not pii_next or pii_next.pos > end_pos:
                    break
                pii.append(pii_next)
                end_pos = max(end_pos, pii_next.pos + len(pii_next))
                next(pii_list)

            # Resolve overlaps
            yield from resolve_overlaps(pii)
