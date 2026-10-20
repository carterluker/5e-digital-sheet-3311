from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import actions, security
from app.config import settings
from app.db import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False)

    def override():
        with Session() as s:
            yield s

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def auth_headers(client, username="alice", password="password123"):
    client.post("/api/auth/register", json={"username": username, "password": password})
    token = client.post("/api/auth/login", json={"username": username, "password": password}).cookies["session"]
    return {"Cookie": f"session={token}"}


@pytest.fixture()
def h(client):
    return auth_headers(client)


FIGHTER = {
    "name": "Brienne",
    "race": "Human",
    "character_class": "Fighter",
    "level": 5,
    "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 12, "charisma": 8},
    "save_proficiencies": ["strength", "constitution"],
    "skill_proficiencies": ["athletics", "perception"],
    "hp": {"max": 44, "current": 44, "temp": 0},
}


def make(client, h, data=None):
    r = client.post("/api/characters", json={"data": data or FIGHTER}, headers=h)
    assert r.status_code == 201, r.text
    return r.json()


def act(client, h, cid, **action):
    return client.post(f"/api/characters/{cid}/actions", json={"action": action}, headers=h)


# ---------------------------------------------------------------- auth

def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "db": True}


def test_auth_flow(client):
    assert client.post("/api/auth/register", json={"username": "Bob", "password": "hunter2hunter2"}).status_code == 201
    assert client.post("/api/auth/register", json={"username": "bob", "password": "hunter2hunter2"}).status_code == 409
    assert client.post("/api/auth/register", json={"username": "x", "password": "short"}).status_code == 422
    assert client.post("/api/auth/login", json={"username": "bob", "password": "wrong-password"}).status_code == 401
    assert client.post("/api/auth/login", json={"username": "nobody", "password": "wrong-password"}).status_code == 401
    r = client.post("/api/auth/login", json={"username": "BOB", "password": "hunter2hunter2"})
    assert r.json()["username"] == "bob"
    flags = r.headers["set-cookie"].lower()
    assert "httponly" in flags and "samesite=lax" in flags and "path=/api" in flags
    hdr = {"Cookie": f"session={r.cookies['session']}"}
    assert client.get("/api/auth/me", headers=hdr).json()["username"] == "bob"
    assert client.post("/api/auth/logout", headers=hdr).status_code == 204
    assert client.get("/api/auth/me", headers=hdr).status_code == 401


def test_requires_auth(client):
    assert client.get("/api/characters").status_code == 401
    assert client.get("/api/characters", headers={"Cookie": "session=nope"}).status_code == 401


def test_expired_token(client, h, monkeypatch):
    assert client.get("/api/auth/me", headers=h).status_code == 200
    later = security.utcnow() + timedelta(hours=settings.session_ttl_hours + 1)
    monkeypatch.setattr(security, "utcnow", lambda: later)
    assert client.get("/api/auth/me", headers=h).status_code == 401


# ---------------------------------------------------------- characters

def test_crud_and_isolation_between_users(client, h):
    c = make(client, h)
    assert c["version"] == 1 and c["name"] == "Brienne"
    assert [x["name"] for x in client.get("/api/characters", headers=h).json()] == ["Brienne"]

    bob = auth_headers(client, "bob", "password456")
    assert client.get("/api/characters", headers=bob).json() == []
    assert client.get(f"/api/characters/{c['id']}", headers=bob).status_code == 404
    assert client.delete(f"/api/characters/{c['id']}", headers=bob).status_code == 404
    assert client.get(f"/api/characters/{c['id']}/backups", headers=bob).status_code == 404
    assert act(client, bob, c["id"], type="long_rest").status_code == 404

    assert client.delete(f"/api/characters/{c['id']}", headers=h).status_code == 204
    assert client.get(f"/api/characters/{c['id']}", headers=h).status_code == 404


def test_structural_validation_rejects_bad_sheet(client, h):
    bad = {**FIGHTER, "level": 25}
    assert client.post("/api/characters", json={"data": bad}, headers=h).status_code == 422
    assert client.post("/api/characters", json={"data": {**FIGHTER, "nonsense": 1}}, headers=h).status_code == 422


def test_derived_stats(client, h):
    d = make(client, h)["derived"]
    assert d["proficiency_bonus"] == 3
    assert d["ability_modifiers"]["strength"] == 3
    assert d["saving_throws"]["strength"] == 6 and d["saving_throws"]["dexterity"] == 2
    assert d["skills"]["athletics"] == 6 and d["skills"]["stealth"] == 2
    assert d["passive_perception"] == 10 + 1 + 3
    assert d["armor_class"] == 12 and d["hit_die"] == 10 and d["spell_save_dc"] is None


def test_armor_class_from_equipment(client, h):
    data = {
        **FIGHTER,
        "inventory": [
            {"name": "Chain Shirt", "kind": "armor", "armor_type": "medium", "base_ac": 13, "equipped": True},
            {"name": "Shield", "kind": "shield", "ac_bonus": 2, "equipped": True},
        ],
    }
    assert make(client, h, data)["derived"]["armor_class"] == 13 + 2 + 2  # dex capped at +2


def test_rule_issues_reported_not_blocking(client, h):
    data = {
        **FIGHTER,
        "hp": {"max": 44, "current": 50},
        "skill_expertise": ["stealth"],
        "inventory": [
            {"name": "Plate", "kind": "armor", "armor_type": "heavy", "base_ac": 18, "equipped": True},
            {"name": "Mail", "kind": "armor", "armor_type": "heavy", "base_ac": 16, "equipped": True},
        ],
        "spell_slots": {"1": {"maximum": 2, "used": 3}},
    }
    c = make(client, h, data)  # saved despite errors
    errors = {i["path"] for i in c["issues"] if i["severity"] == "error"}
    assert {"hp.current", "skill_expertise[0]", "inventory", "spell_slots.1"} <= errors


def test_class_and_slot_rules(client, h):
    wiz = {"name": "Merlin", "character_class": "Wizard", "level": 1, "race": "Gnome", "spell_slots": {"1": {"maximum": 3}}}
    issues = make(client, h, wiz)["issues"]
    assert any(i["path"] == "spell_slots.1" and i["severity"] == "error" for i in issues)
    d = make(client, h, {**wiz, "spell_slots": {}, "abilities": {"intelligence": 16}})["derived"]
    assert d["spell_save_dc"] == 8 + 2 + 3 and d["spell_attack_bonus"] == 5
    r = client.post("/api/characters/validate", json={"character_class": "Jedi"}, headers=h)
    assert r.json()["issues"][0]["severity"] == "warning"


# -------------------------------------------------- autosave + backups

def save(client, h, c, **changes):
    body = {"version": c["version"], "data": {**c["data"], **changes}}
    return client.put(f"/api/characters/{c['id']}", json=body, headers=h)


def test_autosave_versioning_and_conflict(client, h):
    c = make(client, h)
    r = save(client, h, c, notes="hello")
    assert r.status_code == 200 and r.json()["version"] == 2 and r.json()["data"]["notes"] == "hello"
    stale = save(client, h, c, notes="from a stale tab")
    assert stale.status_code == 409
    assert client.get(f"/api/characters/{c['id']}", headers=h).json()["data"]["notes"] == "hello"


def test_layout_saved_and_preserved(client, h):
    c = make(client, h)
    layout = [{"id": "hp", "order": 0, "width": 4, "height": 2}, {"id": "skills", "order": 1}]
    r = client.put(f"/api/characters/{c['id']}", json={"version": 1, "data": c["data"], "layout": layout}, headers=h).json()
    assert [p["id"] for p in r["layout"]] == ["hp", "skills"]
    r = save(client, h, r, notes="x")  # no layout key -> unchanged
    assert len(r.json()["layout"]) == 2
    dup = [{"id": "hp", "order": 0}, {"id": "hp", "order": 1}]
    assert client.put(f"/api/characters/{c['id']}", json={"version": 3, "data": c["data"], "layout": dup}, headers=h).status_code == 422


def test_autosave_backups_are_throttled_and_pruned(client, h, monkeypatch):
    c = make(client, h)
    cid = c["id"]
    for i in range(3):  # inside the interval: only the first save makes a backup
        c = save(client, h, c, notes=f"n{i}").json()
    backups = client.get(f"/api/characters/{cid}/backups", headers=h).json()
    assert len(backups) == 1 and backups[0]["reason"] == "autosave" and backups[0]["version"] == 1

    monkeypatch.setattr(settings, "backup_interval_seconds", 0)
    monkeypatch.setattr(settings, "max_backups_per_character", 3)
    for i in range(6):
        c = save(client, h, c, notes=f"m{i}").json()
    backups = client.get(f"/api/characters/{cid}/backups", headers=h).json()
    assert len(backups) == 3


def test_manual_backup_and_restore(client, h):
    c = make(client, h)
    cid = c["id"]
    b = client.post(f"/api/characters/{cid}/backups", headers=h).json()
    assert b["reason"] == "manual"
    c = save(client, h, c, name="Oops, renamed").json()
    assert client.get(f"/api/characters/{cid}/backups/{b['id']}", headers=h).json()["name"] == "Brienne"

    restored = client.post(f"/api/characters/{cid}/backups/{b['id']}/restore", headers=h).json()
    assert restored["name"] == "Brienne" and restored["data"]["name"] == "Brienne"
    assert restored["version"] == c["version"] + 1
    reasons = [x["reason"] for x in client.get(f"/api/characters/{cid}/backups", headers=h).json()]
    assert "pre-restore" in reasons  # the overwritten state is recoverable too
    assert client.get("/api/characters", headers=h).json()[0]["name"] == "Brienne"


def test_backups_not_accessible_across_characters(client, h):
    a, b = make(client, h), make(client, h)
    bk = client.post(f"/api/characters/{a['id']}/backups", headers=h).json()
    assert client.get(f"/api/characters/{b['id']}/backups/{bk['id']}", headers=h).status_code == 404


# ------------------------------------------------------------ actions

def test_damage_heal_and_temp_hp(client, h):
    cid = make(client, h)["id"]
    act(client, h, cid, type="temp_hp", amount=5)
    r = act(client, h, cid, type="damage", amount=8).json()["character"]["data"]["hp"]
    assert r == {"max": 44, "current": 41, "temp": 0}
    r = act(client, h, cid, type="heal", amount=100).json()["character"]["data"]["hp"]
    assert r["current"] == 44


def test_dying_and_death_saves(client, h):
    cid = make(client, h)["id"]
    d = act(client, h, cid, type="damage", amount=44).json()["character"]["data"]
    assert d["hp"]["current"] == 0 and "unconscious" in d["conditions"]
    assert act(client, h, cid, type="damage", amount=3).json()["character"]["data"]["death_saves"]["failures"] == 1
    assert act(client, h, cid, type="death_save", roll=15).json()["character"]["data"]["death_saves"]["successes"] == 1
    d = act(client, h, cid, type="death_save", roll=20).json()["character"]["data"]
    assert d["hp"]["current"] == 1 and "unconscious" not in d["conditions"] and d["death_saves"] == {"successes": 0, "failures": 0}
    assert act(client, h, cid, type="death_save", roll=10).status_code == 422  # not at 0 HP


def test_massive_damage_kills_and_healing_refused(client, h):
    cid = make(client, h)["id"]
    r = act(client, h, cid, type="damage", amount=88).json()
    assert r["character"]["data"]["death_saves"]["failures"] == 3
    assert act(client, h, cid, type="heal", amount=5).status_code == 422


def test_inventory_actions(client, h):
    cid = make(client, h)["id"]
    potion = {"name": "Potion of Healing", "quantity": 2, "weight": 0.5}
    act(client, h, cid, type="add_item", item=potion)
    inv = act(client, h, cid, type="add_item", item=potion).json()["character"]["data"]["inventory"]
    assert len(inv) == 1 and inv[0]["quantity"] == 4  # stacks
    assert act(client, h, cid, type="remove_item", name="potion of healing", quantity=9).status_code == 422
    c = act(client, h, cid, type="remove_item", name="potion of healing", quantity=4).json()["character"]
    assert c["data"]["inventory"] == []
    assert act(client, h, cid, type="remove_item", name="ghost").status_code == 422


def test_equip_swaps_armor_and_updates_ac(client, h):
    cid = make(client, h)["id"]
    act(client, h, cid, type="add_item", item={"name": "Leather", "kind": "armor", "armor_type": "light", "base_ac": 11})
    act(client, h, cid, type="add_item", item={"name": "Plate", "kind": "armor", "armor_type": "heavy", "base_ac": 18})
    ac = lambda r: r.json()["character"]["derived"]["armor_class"]  # noqa: E731
    assert ac(act(client, h, cid, type="equip", name="Leather")) == 13
    r = act(client, h, cid, type="equip", name="Plate")
    assert ac(r) == 18
    assert [i["equipped"] for i in r.json()["character"]["data"]["inventory"]] == [False, True]
    assert ac(act(client, h, cid, type="equip", name="Plate", equipped=False)) == 12


def test_encumbrance(client, h):
    cid = make(client, h)["id"]
    r = act(client, h, cid, type="add_item", item={"name": "Gold bars", "quantity": 100, "weight": 3}).json()["character"]["derived"]
    assert r["total_weight"] == 300 and r["carrying_capacity"] == 240 and r["encumbered"] is True


def test_currency(client, h):
    cid = make(client, h)["id"]
    act(client, h, cid, type="currency", delta={"gp": 50, "sp": 3})
    c = act(client, h, cid, type="currency", delta={"gp": -20}).json()["character"]["data"]["currency"]
    assert c["gp"] == 30 and c["sp"] == 3
    assert act(client, h, cid, type="currency", delta={"gp": -31}).status_code == 422
    assert client.get(f"/api/characters/{cid}", headers=h).json()["data"]["currency"]["gp"] == 30


def test_conditions(client, h):
    cid = make(client, h)["id"]
    act(client, h, cid, type="condition", name="Poisoned")
    c = act(client, h, cid, type="condition", name="poisoned").json()["character"]["data"]
    assert c["conditions"] == ["poisoned"]
    assert act(client, h, cid, type="condition", name="poisoned", active=False).json()["character"]["data"]["conditions"] == []


def test_resources_slots_hit_dice_and_rests(client, h):
    data = {
        **FIGHTER,
        "resources": [
            {"name": "Second Wind", "maximum": 1, "recharge": "short"},
            {"name": "Action Surge", "maximum": 1, "recharge": "long"},
        ],
        "spell_slots": {"1": {"maximum": 2}},
    }
    cid = make(client, h, data)["id"]
    act(client, h, cid, type="use_resource", name="Second Wind")
    assert act(client, h, cid, type="use_resource", name="second wind").status_code == 422
    act(client, h, cid, type="use_resource", name="Action Surge")
    act(client, h, cid, type="use_spell_slot", level=1)
    assert act(client, h, cid, type="use_spell_slot", level=2).status_code == 422

    act(client, h, cid, type="damage", amount=20)
    r = act(client, h, cid, type="spend_hit_dice", count=2, rolls=[6, 4]).json()["character"]["data"]
    assert r["hp"]["current"] == 24 + (6 + 2) + (4 + 2) and r["hit_dice_used"] == 2
    assert act(client, h, cid, type="spend_hit_dice", count=1, rolls=[11]).status_code == 422  # d10 hit die
    assert act(client, h, cid, type="spend_hit_dice", count=4).status_code == 422  # only 3 left

    r = act(client, h, cid, type="short_rest").json()["character"]["data"]
    assert [x["used"] for x in r["resources"]] == [0, 1]

    r = act(client, h, cid, type="long_rest").json()["character"]["data"]
    assert [x["used"] for x in r["resources"]] == [0, 0]
    assert r["hp"]["current"] == 44 and r["spell_slots"]["1"]["used"] == 0
    assert r["hit_dice_used"] == 0  # regained half of 5 = 2 (min), clamped at 0


def test_server_rolls_when_not_provided(client, h, monkeypatch):
    monkeypatch.setattr(actions.rng, "randint", lambda a, b: b)
    cid = make(client, h)["id"]
    act(client, h, cid, type="damage", amount=44)
    d = act(client, h, cid, type="death_save").json()["character"]["data"]
    assert d["hp"]["current"] == 1  # "rolled" a 20


def test_action_version_check_and_persistence(client, h):
    c = make(client, h)
    r = client.post(f"/api/characters/{c['id']}/actions", json={"action": {"type": "heal", "amount": 1}, "version": 99}, headers=h)
    assert r.status_code == 409
    r = act(client, h, c["id"], type="temp_hp", amount=7).json()
    assert r["character"]["version"] == 2
    assert client.get(f"/api/characters/{c['id']}", headers=h).json()["data"]["hp"]["temp"] == 7


def test_unknown_action_rejected(client, h):
    cid = make(client, h)["id"]
    assert act(client, h, cid, type="teleport").status_code == 422
