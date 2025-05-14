"""
test_image_manifest.py

Tests for asset manifest integrity and existence in DMuffler.
Checks image and sound constant correctness, and validates actual asset files exist.
"""
import os
import logging
import pytest
import GlobalConstants as GC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_image_manifest")

EXPECTED_IMAGES = [
    "bmw_m4.png",
    "ferrari_laferrari.png",
    "ford_model_t.png",
    "ford_mustang.png",
    "jaguar_e_type.png",
    "mclaren_artura.png",
    "porsche_911.png",
    "STAR_WARS_PODRACER.png",
    "SUBARU_WRX_STI.png",
    "TESLA_ROADSTER.png",
]

EXPECTED_IMAGE_CONSTS = [
    GC.bmw_m4_img,
    GC.ferrari_laferrari_img,
    GC.ford_model_t_img,
    GC.ford_mustang_img,
    GC.jaguar_e_type_img,
    GC.mclaren_artura_img,
    GC.porsche_911_img,
    GC.star_wars_podracer_img,
    GC.subaru_wrx_sti_img,
    GC.tesla_roadster_img,
]

EXPECTED_SOUND_CONSTS = [
    GC.bmw_m4_sound,
    GC.ferrari_laferrari_sound,
    GC.ford_model_t_sound,
    GC.ford_mustang_sound,
    GC.jaguar_e_type_sound,
    GC.mclaren_artura_sound,
    GC.porsche_911_sound,
    GC.star_wars_podracer_sound,
    GC.subaru_wrx_sti_sound,
    GC.tesla_roadster_sound,
]

@pytest.mark.parametrize("img_const, expected_fname", zip(EXPECTED_IMAGE_CONSTS, EXPECTED_IMAGES))
def test_image_constants(img_const, expected_fname):
    assert img_const.endswith(expected_fname), f"Constant does not match expected filename: {img_const} vs {expected_fname}"

@pytest.mark.parametrize("sound_const, expected_car", zip(EXPECTED_SOUND_CONSTS, [
    "bmw_m4", "ferrari_laferrari", "ford_model_t", "ford_mustang", "jaguar_e_type", "mclaren_artura", "porsche_911", "star_wars_podracer", "subaru_wrx_sti", "tesla_roadster"
]))
def test_sound_constants(sound_const, expected_car):
    assert sound_const.endswith(".mp3"), f"Sound constant for {expected_car} does not end with .mp3: {sound_const}"

def test_all_images_exist():
    image_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    missing = []
    for fname in EXPECTED_IMAGES:
        path = os.path.join(image_dir, fname)
        if not os.path.isfile(path):
            logger.error(f"Missing image file: {fname}")
            missing.append(fname)
    assert not missing, f"Missing image files: {missing}"

def test_image_constants_defined():
    for const in EXPECTED_IMAGE_CONSTS:
        assert const is not None and isinstance(const, str) and const.endswith('.png')

def test_sound_constants_defined():
    for const in EXPECTED_SOUND_CONSTS:
        assert const is not None and isinstance(const, str) and const.endswith('.mp3')

def test_image_count():
    image_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    pngs = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    assert len(pngs) == 10, f"Expected 10 images, found {len(pngs)}: {pngs}"
