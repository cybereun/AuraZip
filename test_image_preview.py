import io

from PIL import Image

from archive_view import read_preview_image


def make_oriented_jpeg(orientation: int) -> bytes:
    image = Image.new("RGB", (3, 2), "white")
    exif = Image.Exif()
    exif[274] = orientation  # EXIF Orientation
    data = io.BytesIO()
    image.save(data, format="JPEG", exif=exif)
    return data.getvalue()


def test_preview_orientation_corrects_camera_portrait_metadata():
    for orientation in (6, 8):
        image = read_preview_image(make_oriented_jpeg(orientation))
        assert (image.width(), image.height()) == (2, 3)


def test_preview_orientation_preserves_unrotated_landscape_bytes():
    image = read_preview_image(make_oriented_jpeg(1))
    assert (image.width(), image.height()) == (3, 2)
