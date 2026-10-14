import hashlib

from .v3_06 import FIRMWARE as V3_06

VERSIONS = (V3_06,)


def identify(cdd: bytes):
    """Return the Firmware whose stock .CDD this is, or None."""
    digest = hashlib.sha256(cdd).hexdigest()
    return next((fw for fw in VERSIONS if fw.sha256 == digest), None)
