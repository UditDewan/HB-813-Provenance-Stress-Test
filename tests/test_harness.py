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

SIGNED = CORPUS / "C.jpg"                 # signed, carries no EXIF
SIGNED_WITH_EXIF = CORPUS / "ocsp.jpg"    # signed, carries EXIF

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


def test_metadata_scrub_is_a_noop_when_there_is_no_exif():
    """Nothing to delete, so the bytes come back identical and C2PA is untouched."""
    data = SIGNED.read_bytes()
    assert detect.c2pa_state(SIGNED) == detect.PRESENT_VALID
    assert not detect.describe(SIGNED)["exif_present"]
    assert TRANSFORMS["metadata_scrub"](data) == data


@pytest.mark.skipif(not SIGNED_WITH_EXIF.exists(), reason="corpus not built")
def test_metadata_scrub_breaks_the_signature_when_there_is_exif(tmp_path):
    """The finding that reframes the memo, so it gets a test.

    "Remove properties and personal information" is a privacy feature people are
    told to use. On a signed image that actually carries EXIF it deletes a
    segment the manifest hashes over, so the claim stays attached and stops
    matching: present_invalid, assertion.dataHash.mismatch.

    A user who did nothing wrong ends up distributing an image that carries a
    broken provenance claim. That is the middle outcome, arrived at innocently,
    and it is why detection here is three-valued.
    """
    assert detect.describe(SIGNED_WITH_EXIF)["exif_present"]
    assert detect.c2pa_state(SIGNED_WITH_EXIF) == detect.PRESENT_VALID

    out = tmp_path / "scrubbed.jpg"
    out.write_bytes(TRANSFORMS["metadata_scrub"](SIGNED_WITH_EXIF.read_bytes()))

    assert detect.c2pa_state(out) == detect.PRESENT_INVALID
    codes = {s.get("code") for s in detect.c2pa_detail(out).get("validation_status", [])}
    assert "assertion.dataHash.mismatch" in codes


def test_transparency_composites_onto_white_not_black():
    """A transparent pixel becomes white, the colour every screen puts behind it.

    Pillow's convert("RGB") drops the alpha channel, which composites against
    black. Two corpus PNGs are palette images with transparency, so the
    un-fixed path produced a black-backed image no ordinary user could have
    made -- and the screenshot row is meant to be the most ordinary path there is.
    """
    import io

    im = Image.new("RGBA", (4, 2), (255, 0, 0, 255))
    im.putpixel((0, 0), (0, 0, 0, 0))
    buf = io.BytesIO()
    im.save(buf, format="PNG")

    out = Image.open(io.BytesIO(TRANSFORMS["screenshot"](buf.getvalue()))).convert("RGB")
    assert out.getpixel((0, 0)) == (255, 255, 255)
    assert out.getpixel((3, 1)) == (255, 0, 0)
