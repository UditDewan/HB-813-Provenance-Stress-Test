"""Transformations that simulate ordinary handling of an image.

Every transform here corresponds to something a person does without any intent
to evade: saving, resizing, cropping, rotating, screenshotting, or ticking the
"remove properties" box Windows Explorer offers. Nothing in this module is
tuned to defeat a specific detector, and nothing takes a detector's output as
input. It is a stress test, not an attack.

Each transform is bytes -> bytes and carries a plain-language label describing
the human behavior it stands in for.

ponytail: one module, not one module per family. Split when a family needs more
than a screenful of its own.
"""

from __future__ import annotations

import io

import piexif
from PIL import Image

_JPEG_KW = dict(format="JPEG", quality=95)


def _open(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def _flatten(im: Image.Image) -> Image.Image:
    """RGB, compositing any transparency onto white.

    Pillow's convert("RGB") drops the alpha channel, which composites against
    black. Every editor, browser and screen puts a transparent pixel on a white
    page, so black would be measuring a file no ordinary user could produce.
    Palette images carry transparency in .info rather than a mode, hence both
    checks.
    """
    if im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info:
        im = im.convert("RGBA")
        canvas = Image.new("RGB", im.size, "white")
        canvas.paste(im, (0, 0), im)
        return canvas
    return im.convert("RGB")


def _encode(im: Image.Image, **kw) -> bytes:
    buf = io.BytesIO()
    _flatten(im).save(buf, **kw)
    return buf.getvalue()


# Geometry edits re-encode as JPEG q95 rather than preserving the original
# bitstream. That is not a shortcut, it is physics: you cannot move a JPEG's
# pixels without decoding and re-encoding them. q95 keeps the recompression
# mild so the geometry change is what the numbers are measuring.


def recompress(quality: int):
    def t(data: bytes) -> bytes:
        return _encode(_open(data), format="JPEG", quality=quality)

    t.label = f"Re-saved as JPEG at quality {quality}"
    return t


def resize(pct: int):
    def t(data: bytes) -> bytes:
        im = _open(data)
        size = (max(1, im.width * pct // 100), max(1, im.height * pct // 100))
        return _encode(im.resize(size, Image.LANCZOS), **_JPEG_KW)

    t.label = f"Resized to {pct}% of original dimensions"
    return t


def crop(pct: int):
    def t(data: bytes) -> bytes:
        im = _open(data)
        dx, dy = im.width * pct // 100, im.height * pct // 100
        return _encode(im.crop((dx, dy, im.width - dx, im.height - dy)), **_JPEG_KW)

    t.label = f"Cropped {pct}% off each border"
    return t


def rotate(degrees: int):
    op = {90: Image.ROTATE_90, 180: Image.ROTATE_180, 270: Image.ROTATE_270}[degrees]

    def t(data: bytes) -> bytes:
        return _encode(_open(data).transpose(op), **_JPEG_KW)

    t.label = f"Rotated {degrees} degrees"
    return t


def convert_png_jpeg_png(data: bytes) -> bytes:
    """PNG -> JPEG -> PNG, the shape of moving an image between two apps."""
    as_png = _encode(_open(data), format="PNG")
    as_jpeg = _encode(_open(as_png), format="JPEG", quality=90)
    return _encode(_open(as_jpeg), format="PNG")


convert_png_jpeg_png.label = "Converted PNG to JPEG and back to PNG"


def screenshot(data: bytes) -> bytes:
    """Decode to pixels, composite onto an opaque canvas, re-encode as PNG.

    A screenshot is exactly this: the file's decoded pixels, and nothing else,
    handed to a fresh encoder. No container survives it, so no metadata,
    manifest, or signature can. This is the single most common path by which an
    ordinary person moves an image, and the reason it deserves its own row.

    ponytail: no real screen capture. Same-size output, no scaling to a device
    resolution -- resize() already covers scaling, and mixing them would make
    this row measure two things.
    """
    return _encode(_open(data), format="PNG")


screenshot.label = "Screenshotted (pixels recaptured, container discarded)"


def metadata_scrub(data: bytes) -> bytes:
    """Remove the EXIF block without touching the pixels.

    This is the Windows Explorer "Remove Properties and Personal Information"
    checkbox, and the equivalent in most sharing tools. It is a privacy feature
    people are told to use. It is worth measuring separately because it removes
    metadata *without* re-encoding, which isolates 'the block was deleted' from
    'the whole file was rebuilt'.
    """
    # piexif only understands JPEG and WEBP containers. For anything else there
    # is no way to delete the metadata block without re-encoding, so the file
    # comes back untouched and the identical sha256 in runs.csv says so.
    if _open(data).format not in ("JPEG", "WEBP"):
        return data
    out = io.BytesIO()
    piexif.remove(data, out)
    return out.getvalue()


metadata_scrub.label = "EXIF block removed in place (no re-encode)"


def editor_resave(data: bytes) -> bytes:
    """Open in an editor and save. Pixels re-encoded, metadata not carried over.

    Pillow drops EXIF unless explicitly told to keep it, which is what most
    editors do by default.
    """
    return _encode(_open(data), format="JPEG", quality=92)


editor_resave.label = "Opened in an editor and saved (default settings)"


TRANSFORMS = {
    **{f"recompress_q{q}": recompress(q) for q in (95, 75, 50)},
    **{f"resize_{p}pct": resize(p) for p in (75, 50, 25)},
    **{f"crop_{p}pct": crop(p) for p in (5, 10, 25)},
    **{f"rotate_{d}": rotate(d) for d in (90, 180)},
    "convert_png_jpeg_png": convert_png_jpeg_png,
    "screenshot": screenshot,
    "metadata_scrub": metadata_scrub,
    "editor_resave": editor_resave,
}

# Two-step chains worth calling out on their own. The first is the realistic
# worst case: someone screenshots a post, then a messaging app recompresses it.
CHAINS = [
    ("screenshot", "recompress_q75"),
    ("resize_50pct", "recompress_q75"),
    ("crop_10pct", "recompress_q50"),
    ("metadata_scrub", "recompress_q75"),
]


def apply_chain(data: bytes, names) -> bytes:
    for name in names:
        data = TRANSFORMS[name](data)
    return data


def label(names) -> str:
    return " then ".join(TRANSFORMS[n].label for n in names)
