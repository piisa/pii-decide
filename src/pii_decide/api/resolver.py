

from typing import Dict, Iterable

from pii_data.types import DocumentChunk, PiiEntity, PiiCollection

from ..defs import FMT_CONFIG

class Resolver:

    def __init__(self, config: TYPE_CONFIG_LIST, debug: bool = False):
        self.policy = policy

        dp = Path(__file__).parents[2] / "resources" / "decision.json"
        cfgdata = load_single_config(dp, FMT_CONFIG, config)
        self.dec = load_deciders(cfgdata.get("deciders"))



    def __call__(self, pii_list: Iterable[PiiEntity], chunk: DocumentChunk,
                 piic: PiiCollection) -> Iterable[PiiEntity]:
        for pii in pii_list:
            yield pii
