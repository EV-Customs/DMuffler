import os
from static.images.image_manifest import CAR_IMAGE_MAP

def test_all_images_exist():
    image_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    missing = []
    for key, filename in CAR_IMAGE_MAP.items():
        path = os.path.join(image_dir, filename)
        if not os.path.isfile(path):
            missing.append(filename)
    assert not missing, f"Missing image files: {missing}"

def test_image_naming():
    for filename in CAR_IMAGE_MAP.values():
        assert filename == filename.lower(), f"Filename not lowercase: {filename}"
        assert filename.replace('_', '').replace('.', '').isalnum(), f"Filename has invalid chars: {filename}"
        assert filename.endswith('.png'), f"Filename not png: {filename}"
