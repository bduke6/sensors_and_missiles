from entities import Ship, Missile


def test_uid_generation():
    ship = Ship(lat=13.5, lon=144.8, alt=0, velocity=[0, 0, 0], orientation=[1, 0, 0])
    missile = Missile(lat=13.5, lon=144.8, alt=0, velocity=[0, 0, 0], orientation=[1, 0, 0], entity_id="missile_1",fuel=100)
    assert ship.entity_id is not None
    assert missile.entity_id is not None
    assert isinstance(ship.entity_id, str)
    assert isinstance(missile.entity_id, str)

def test_missile_launch():
    ship = Ship(lat=13.5, lon=144.8, alt=0, velocity=[0, 0, 0], orientation=[1, 0, 0])
    missile = Missile(lat=13.5, lon=144.8, alt=0, velocity=[0, 0, 0], orientation=[1, 0, 0], entity_id="missile_1", fuel=100)
    missile.launch(ship)
    assert missile.fuel == 99  # Assuming fuel decreases on launch
