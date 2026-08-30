"""Three-valued provenance detection.

    present_valid    a C2PA manifest is present and validates
    present_invalid  a manifest is present but does not validate
    absent           no manifest at all

The middle case is the one policy people miss. A signature that was *stripped*
and a signature that was *broken* look the same to a user and are different
problems for an enforcement agency: the first has no evidence to act on, the
second has evidence that something happened but not what.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import c2pa
from PIL import Image

PRESENT_VALID = "present_valid"
PRESENT_INVALID = "present_invalid"
ABSENT = "absent"

# c2pa-rs ValidationState. "Trusted" additionally means the signing cert chains
# to a configured trust list; we do not configure one, so a good signature from
# an unknown issuer reports "Valid". Both count as a surviving signature -- the
# question this study asks is whether the signal survives handling, not whether
# the signer is on anyone's allowlist.
_VALID_STATES = {"Valid", "Trusted"}

# Verification is offline and deterministic. Some assets carry no manifest at
# all, only a URL pointing at one held on a vendor's server. Fetching those
# would make every run depend on a third party's uptime and would quietly
# credit an image for provenance it does not itself carry -- so we do not, and
# describe() flags the reference separately instead.
# ponytail: load_settings is deprecated in favour of Settings + Context, which
# would mean threading a Context through every Reader. It still works and is one
# line; move to Context if a future release removes it.
c2pa.load_settings(json.dumps({"verify": {"remote_manifest_fetch": False}}), "json")

# ponytail: the C2PA library reports "manifest lives at a URL" as a generic
# error with this prefix, not a typed exception. If a future release types it,
# match on the class instead.
_REMOTE_PREFIX = "Remote:"


def _read(path) -> tuple[dict, bool, str]:
    """(validation report, provenance is only a remote reference, refusal reason).

    A refusal reason means the reader found something and would not validate it:
    an unknown hash algorithm, a manifest from a pre-release spec. That is a
    manifest a verifier cannot check, which is `present_invalid` -- the file
    carries a claim and nobody can confirm it. Exactly the situation an
    enforcement agency would have to make a decision about.
    """
    try:
        return json.loads(c2pa.Reader(str(path)).json()), False, ""
    except c2pa.c2pa._C2paManifestNotFound:
        return {}, False, ""
    except (c2pa.c2pa._C2paIo, c2pa.c2pa._C2paNotSupported):
        raise  # a missing file or an unreadable container is a bug, not a result
    except c2pa.C2paError as exc:
        if str(exc).startswith(_REMOTE_PREFIX):
            return {}, True, ""
        return {}, False, str(exc)


def _state(report: dict, refused: str) -> str:
    if refused:
        return PRESENT_INVALID
    if not report:
        return ABSENT
    return PRESENT_VALID if report.get("validation_state") in _VALID_STATES else PRESENT_INVALID


def c2pa_state(path: str | Path) -> str:
    """Return one of PRESENT_VALID / PRESENT_INVALID / ABSENT."""
    report, _, refused = _read(path)
    return _state(report, refused)


def c2pa_detail(path: str | Path) -> dict:
    """Full validation report, or {} when no embedded manifest. For eyeballing."""
    return _read(path)[0]


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def describe(path: str | Path) -> dict:
    """Everything one row of runs.csv needs to know about a file."""
    path = Path(path)
    raw = path.read_bytes()
    with Image.open(path) as im:
        width, height = im.size
        exif_present = bool(im.getexif())
    report, remote_ref, refused = _read(path)
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "width": width,
        "height": height,
        "c2pa_state": _state(report, refused),
        # Not a fourth outcome: an asset whose only provenance is a URL to a
        # vendor's server carries nothing self-verifying, so it reads as absent.
        # The flag is here because "the mark is a link" is its own policy problem.
        "remote_manifest_ref": remote_ref,
        "exif_present": exif_present,
        # XMP is where several "AI-generated" claims actually live (Adobe's
        # digitalSourceType among them), and it travels separately from C2PA.
        "xmp_present": b"http://ns.adobe.com/xap/1.0/" in raw,
    }
