import uuid
def make_id() -> str:
    return uuid.uuid4().hex
