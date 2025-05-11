import os
import pytest
import GlobalConstants as GC

EXPECTED_IMAGES = [
    'ford_model_t.png',
    'ford_mustang_gt350.png',
    'jaguar_e_type_series_1.png',
    'la_ferrari.png',
    'mclaren_f1.png',
    'porsche_911.png',
    'orange_ferrari.png',
    'purple_bmw.png',
]

EXPECTED_IMAGE_CONSTS = [
    GC.FORD_MODEL_T_IMG,
    GC.FORD_MUSTANG_GT350_IMG,
    GC.JAGUAR_E_TYPE_SERIES_1_IMG,
    GC.LA_FERRARI_IMG,
    GC.MCLAREN_F1_IMG,
    GC.PORSCHE_911_IMG,
    GC.ORANGE_FERRARI_IMG,
    GC.PURPLE_BMW_IMG,
]

EXPECTED_SOUND_CONSTS = [
    GC.FORD_MODEL_T_SOUND,
    GC.FORD_MUSTANG_GT350_SOUND,
    GC.JAGUAR_E_TYPE_SERIES_1_SOUND,
    GC.LA_FERRARI_SOUND,
    GC.MCLAREN_F1_SOUND,
    GC.PORSCHE_911_SOUND,
    GC.ORANGE_FERRARI_SOUND,
    GC.PURPLE_BMW_SOUND,
]

def test_all_images_exist():
    image_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    missing = []
    for fname in EXPECTED_IMAGES:
        path = os.path.join(image_dir, fname)
        if not os.path.isfile(path):
            missing.append(fname)
    assert not missing, f"Missing image files: {missing}"

def test_image_constants_defined():
    for const in EXPECTED_IMAGE_CONSTS:
        assert const is not None and isinstance(const, str) and const.endswith('.png')

def test_sound_constants_defined():
    for const in EXPECTED_SOUND_CONSTS:
        assert const is not None and isinstance(const, str) and const.endswith('.wav')

def test_image_count():
    image_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    pngs = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    assert len(pngs) == 8, f"Expected 8 images, found {len(pngs)}: {pngs}"
