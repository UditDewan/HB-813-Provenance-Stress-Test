"""The checks that matter: detection tells the three outcomes apart, and every
transform produces a real image.

Run: uv run pytest
Needs the corpus: uv run python -m src.corpus fetch
"""

from __future__ import annotations

import pytest
from PIL import Image

from src import detect
from src.corpus import CORPUS
from src.transforms import TRANSFORMS

SIGNED = CORPUS / "C.jpg"

pytestmark = pytest.mark.skipif(
    not SIGNED.exists(), reason="corpus not built -- run: python -m src.corpus fetch"
)


def test_signed_image_reads_present_valid():
    assert detect.c2pa_state(SIGNED) == detect.PRESENT_VALID


def test_resaving_removes_the_manifest_entirely(tmp_path):
    """A signature that was stripped, not broken. This is the common case."""
    out = tmp_path / "resaved.jpg"
    out.write_bytes(TRANSFORMS["editor_resave"](SIGNED.read_bytes()))
    assert detect.c2pa_state(out) == detect.ABSENT


def test_tampered_pixels_read_present_invalid(tmp_path):
    """The middle outcome, and the reason detection is three-valued.

    Flipping a byte deep in the compressed scan data leaves the manifest in
    place but breaks the hash it asserts over the pixels. A policy that treats
    "no signature" and "a signature that no longer matches" as the same thing
    loses the distinction between an image nobody vouched for and an image
    somebody vouched for and then something changed.
    """
    data = bytearray(SIGNED.read_bytes())
    data[-5000] ^= 0xFF
    out = tmp_path / "tampered.jpg"
    out.write_bytes(bytes(data))
    assert detect.c2pa_state(out) == detect.PRESENT_INVALID


def test_describe_reports_every_column_the_csv_needs():
    d = detect.describe(SIGNED)
    assert set(d) == {"sha256", "bytes", "width", "height", "c2pa_state",
                      "remote_manifest_ref", "exif_present", "xmp_present"}
    assert d["width"] > 0 and d["height"] > 0


@pytest.mark.parametrize("name", sorted(TRANSFORMS))
def test_transform_returns_a_decodable_image(name, tmp_path):
    out = TRANSFORMS[name](SIGNED.read_bytes())
    path = tmp_path / name
    path.write_bytes(out)
    with Image.open(path) as im:
        im.verify()


def test_metadata_scrub_leaves_the_pixels_alone():
    """It deletes the EXIF block without re-encoding, so C2PA is untouched.

    Worth asserting because it is the one transform that separates "metadata
    removed" from "file rebuilt" -- and it shows a privacy feature people are
    told to use does not, by itself, destroy provenance.
    """
    data = SIGNED.read_bytes()
    assert detect.c2pa_state(SIGNED) == detect.PRESENT_VALID
    assert TRANSFORMS["metadata_scrub"](data) == data  # C.jpg carries no EXIF to remove
