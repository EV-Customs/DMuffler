import GlobalConstants as GC

def test_car_asset_fields():
    asset = GC.CarAsset("test", "image.png", "sound.mp3")
    assert asset.name == "test"
    assert asset.image == "image.png"
    assert asset.sound == "sound.mp3"

def test_car_assets_list():
    assert isinstance(GC.CAR_ASSETS, list)
    assert all(isinstance(a, GC.CarAsset) for a in GC.CAR_ASSETS)
