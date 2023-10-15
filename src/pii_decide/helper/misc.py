
from pii_data.types import PiiEntity

from .. import defs


def get_action(pii: PiiEntity) -> str:
    """
    Get the current action defined in the decision stage of a PiiEntity process
    field
    """
    prc = pii.fields.get("process")
    return prc["action"] if prc and prc["stage"] == defs.STAGE else None


def set_action(pii: PiiEntity, action: str, **data):
    """
    Set the decision stage with the passed action on a PiiEntity process field
    """
    pii.add_process_stage(defs.STAGE, action=action, **data)
