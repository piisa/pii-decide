
from operator import attrgetter

from pii_data.types import PiiEntity, PiiCollection
from pii_data.types.doc import SrcDocument, DocumentChunk
from pii_data.helper.exception import UnimplementedException
from pii_data.types.piicollection import PiiChunkIterator
from pii_data.types.piicollection.collection import TYPE_DET_DICT
from pii_data.helper.config import load_config

from typing import Dict, List, Iterable

from ..deciders import SimpleOverlapDecider
from .. import defs



class PiiDecider:

    def __init__(self, config: Dict = None, debug: bool = False):
        """
         :param config: object configuration to apply
         :param debug: print out debug messages
        """
        self._debug = debug
        all_config = load_config(config, [defs.FMT_CONFIG_DECIDER,
                                          defs.FMT_CONFIG_SCORER])
        config = all_config.get(defs.FMT_CONFIG_DECIDER) or {}

        # For the time being, the decision is made using a SimpleOverlapDecider
        self._dec = SimpleOverlapDecider(config)


    def process_chunk(self, entlist: Iterable[PiiEntity],
                      detectors: TYPE_DET_DICT,
                      chunk: DocumentChunk = None) -> Iterable[PiiEntity]:
        """
        Perform decision on a list of PII Instances (corresponding to a
        single document chunk)
          :return: an iterable of the PiiEntity objects, with decision result
            added
        """
        # Ensure the PII Instances in the chunk are sorted by position
        sorted_pii = sorted(entlist, key=attrgetter("pos"))
        # Process the list via the SimpleOverlapDecider
        return self._dec(sorted_pii, detectors, chunk)


    def decide_chunk(self, piic: PiiCollection,
                     chunk: DocumentChunk = None) -> PiiCollection:
        """
        Perform decision on a collection of PII Instances (which must
        correspond to a single document chunk)
          :return: a PiiCollection in which each PII instance contains
            the decision result
        """
        detectors = piic.get_detectors(asdict=True)
        out = PiiCollection.clone(piic)
        for pii in self.process_chunk(piic, detectors, chunk):
            out.add(pii)
        return out


    def decide_doc(self, piic: PiiCollection,
                   doc: SrcDocument = None) -> PiiCollection:
        """
        Perform decision on a PII collection corresponding to a full document
        """
        if doc:
            raise UnimplementedException("unimplemented doc processing in decision")
        detectors = piic.get_detectors(asdict=True)
        out = PiiCollection.clone(piic)
        for pii_chunk in PiiChunkIterator(piic):
            for pii in self.process_chunk(pii_chunk, detectors):
                out.add(pii)
        out.stage("decision")
        return out


    def __call__(self, piic: PiiCollection,
                 doc: SrcDocument = None) -> PiiCollection:
        return self.decide_doc(piic, doc)
