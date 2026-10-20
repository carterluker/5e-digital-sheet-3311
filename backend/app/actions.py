"""Scripted bookkeeping: server-side game actions that mutate a Sheet.

Each action is a small pydantic model discriminated by `type`. `apply` mutates
the sheet in place and returns human-readable log messages.
"""
import random
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from .rules import class_info, modifier
from .sheet import Item, Sheet

rng = random.Random()  # replaced in tests for deterministic rolls


class ActionError(ValueError):
    """The action is not legal for the current sheet state."""


class _Action(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Damage(_Action):
    type: Literal["damage"]
    amount: int = Field(ge=0, le=9999)


class Heal(_Action):
    type: Literal["heal"]
    amount: int = Field(ge=0, le=9999)


class TempHp(_Action):
    type: Literal["temp_hp"]
    amount: int = Field(ge=0, le=9999)


class DeathSave(_Action):
    type: Literal["death_save"]
    roll: int | None = Field(None, ge=1, le=20)  # server rolls if omitted


class AddItem(_Action):
    type: Literal["add_item"]
    item: Item


class RemoveItem(_Action):
    type: Literal["remove_item"]
    name: str
    quantity: int = Field(1, ge=1)


class Equip(_Action):
    type: Literal["equip"]
    name: str
    equipped: bool = True


class Currency(_Action):
    type: Literal["currency"]
    delta: dict[Literal["cp", "sp", "ep", "gp", "pp"], int]


class SetCondition(_Action):
    type: Literal["condition"]
    name: str = Field(min_length=1, max_length=50)
    active: bool = True


class UseResource(_Action):
    type: Literal["use_resource"]
    name: str
    amount: int = Field(1, ge=1)


class UseSpellSlot(_Action):
    type: Literal["use_spell_slot"]
    level: int = Field(ge=1, le=9)


class SpendHitDice(_Action):
    type: Literal["spend_hit_dice"]
    count: int = Field(1, ge=1, le=20)
    rolls: list[int] | None = None  # server rolls if omitted


class ShortRest(_Action):
    type: Literal["short_rest"]


class LongRest(_Action):
    type: Literal["long_rest"]


Action = Annotated[
    Damage | Heal | TempHp | DeathSave | AddItem | RemoveItem | Equip | Currency | SetCondition
    | UseResource | UseSpellSlot | SpendHitDice | ShortRest | LongRest,
    Field(discriminator="type"),
]


def _find_item(sheet: Sheet, name: str) -> Item:
    for item in sheet.inventory:
        if item.name.lower() == name.strip().lower():
            return item
    raise ActionError(f"No item named '{name}'")


def _find_resource(sheet: Sheet, name: str):
    for r in sheet.resources:
        if r.name.lower() == name.strip().lower():
            return r
    raise ActionError(f"No resource named '{name}'")


def _drop_unconscious(sheet: Sheet) -> None:
    if "unconscious" in sheet.conditions:
        sheet.conditions.remove("unconscious")


def apply(sheet: Sheet, a: Action) -> list[str]:
    hp = sheet.hp
    msgs: list[str] = []

    if isinstance(a, Damage):
        remaining = a.amount
        absorbed = min(hp.temp, remaining)
        hp.temp -= absorbed
        remaining -= absorbed
        if absorbed:
            msgs.append(f"{absorbed} damage absorbed by temp HP")
        if remaining and hp.current == 0:
            # Damage while dying: one failed death save (three on a massive hit).
            sheet.death_saves.failures = 3 if remaining >= hp.max else min(sheet.death_saves.failures + 1, 3)
            msgs.append(f"Damage at 0 HP: {sheet.death_saves.failures} death save failure(s)")
        elif remaining:
            overflow = remaining - hp.current
            hp.current = max(hp.current - remaining, 0)
            msgs.append(f"Took {remaining} damage ({hp.current}/{hp.max} HP)")
            if hp.current == 0:
                if overflow >= hp.max:
                    sheet.death_saves.failures = 3
                    msgs.append("Massive damage: instant death")
                else:
                    msgs.append("Dropped to 0 HP: unconscious")
                if "unconscious" not in sheet.conditions:
                    sheet.conditions.append("unconscious")
                    sheet.death_saves.successes = 0

    elif isinstance(a, Heal):
        if sheet.death_saves.failures >= 3:
            raise ActionError("Character is dead; healing has no effect (restore from a backup or reset death saves)")
        was_down = hp.current == 0
        hp.current = min(hp.current + a.amount, hp.max)
        if was_down and hp.current > 0:
            sheet.death_saves.successes = sheet.death_saves.failures = 0
            _drop_unconscious(sheet)
        msgs.append(f"Healed to {hp.current}/{hp.max} HP")

    elif isinstance(a, TempHp):
        hp.temp = max(hp.temp, a.amount)  # temp HP do not stack
        msgs.append(f"Temp HP: {hp.temp}")

    elif isinstance(a, DeathSave):
        if hp.current != 0:
            raise ActionError("Death saves are only rolled at 0 HP")
        if sheet.death_saves.failures >= 3:
            raise ActionError("Character is already dead")
        roll = a.roll or rng.randint(1, 20)
        ds = sheet.death_saves
        if roll == 20:
            hp.current = 1
            ds.successes = ds.failures = 0
            _drop_unconscious(sheet)
            msgs.append("Natural 20: regains 1 HP")
        else:
            if roll == 1:
                ds.failures = min(ds.failures + 2, 3)
            elif roll < 10:
                ds.failures += 1
            else:
                ds.successes += 1
            msgs.append(f"Rolled {roll}: {ds.successes} success(es), {ds.failures} failure(s)")
            if ds.successes >= 3:
                ds.successes = ds.failures = 0
                _drop_unconscious(sheet)
                msgs.append("Stabilised")
            elif ds.failures >= 3:
                msgs.append("Character has died")

    elif isinstance(a, AddItem):
        new = a.item
        existing = next((i for i in sheet.inventory if i.model_dump(exclude={"quantity", "equipped"}) == new.model_dump(exclude={"quantity", "equipped"}) and not i.equipped), None)
        if existing and not new.equipped:
            existing.quantity += new.quantity
            msgs.append(f"{existing.name} x{existing.quantity}")
        else:
            sheet.inventory.append(new)
            msgs.append(f"Added {new.name} x{new.quantity}")

    elif isinstance(a, RemoveItem):
        item = _find_item(sheet, a.name)
        if a.quantity > item.quantity:
            raise ActionError(f"Only {item.quantity} x {item.name} in inventory")
        item.quantity -= a.quantity
        if item.quantity == 0:
            sheet.inventory.remove(item)
        msgs.append(f"Removed {a.quantity} x {item.name}")

    elif isinstance(a, Equip):
        item = _find_item(sheet, a.name)
        if a.equipped:
            if item.kind not in ("armor", "shield", "weapon"):
                raise ActionError(f"{item.name} cannot be equipped")
            if item.kind in ("armor", "shield"):
                for other in sheet.inventory:
                    if other is not item and other.kind == item.kind and other.equipped:
                        other.equipped = False
                        msgs.append(f"Unequipped {other.name}")
        item.equipped = a.equipped
        msgs.append(f"{'Equipped' if a.equipped else 'Unequipped'} {item.name}")

    elif isinstance(a, Currency):
        for coin, delta in a.delta.items():
            new = getattr(sheet.currency, coin) + delta
            if new < 0:
                raise ActionError(f"Not enough {coin} (have {getattr(sheet.currency, coin)}, need {-delta})")
            setattr(sheet.currency, coin, new)
        msgs.append("Currency updated")

    elif isinstance(a, SetCondition):
        name = a.name.strip().lower().replace(" ", "_")
        if a.active and name not in sheet.conditions:
            sheet.conditions.append(name)
        elif not a.active and name in sheet.conditions:
            sheet.conditions.remove(name)
        msgs.append(f"{name}: {'on' if a.active else 'off'}")

    elif isinstance(a, UseResource):
        r = _find_resource(sheet, a.name)
        if r.used + a.amount > r.maximum:
            raise ActionError(f"{r.name}: only {r.maximum - r.used} remaining")
        r.used += a.amount
        msgs.append(f"{r.name}: {r.maximum - r.used}/{r.maximum} remaining")

    elif isinstance(a, UseSpellSlot):
        slot = sheet.spell_slots.get(a.level)
        if slot is None or slot.used >= slot.maximum:
            raise ActionError(f"No level {a.level} spell slots remaining")
        slot.used += 1
        msgs.append(f"Level {a.level} slots: {slot.maximum - slot.used}/{slot.maximum} remaining")

    elif isinstance(a, SpendHitDice):
        info = class_info(sheet)
        if info is None:
            raise ActionError("Set a valid SRD class to spend hit dice")
        available = sheet.level - sheet.hit_dice_used
        if a.count > available:
            raise ActionError(f"Only {available} hit dice remaining")
        if a.rolls is not None and (len(a.rolls) != a.count or any(not 1 <= r <= info.hit_die for r in a.rolls)):
            raise ActionError(f"Provide {a.count} rolls between 1 and {info.hit_die}")
        rolls = a.rolls or [rng.randint(1, info.hit_die) for _ in range(a.count)]
        con = modifier(sheet.abilities.constitution)
        healed = sum(max(r + con, 0) for r in rolls)
        sheet.hit_dice_used += a.count
        before = hp.current
        hp.current = min(hp.current + healed, hp.max) if hp.current > 0 else hp.current
        msgs.append(f"Spent {a.count} d{info.hit_die} (rolled {rolls}): healed {hp.current - before} HP")

    elif isinstance(a, ShortRest):
        for r in sheet.resources:
            if r.recharge == "short":
                r.used = 0
        msgs.append("Short rest: short-rest resources restored")

    elif isinstance(a, LongRest):
        if hp.current == 0 and sheet.death_saves.failures >= 3:
            raise ActionError("Character is dead")
        hp.current, hp.temp = hp.max, 0
        sheet.death_saves.successes = sheet.death_saves.failures = 0
        _drop_unconscious(sheet)
        recovered = max(sheet.level // 2, 1)
        sheet.hit_dice_used = max(sheet.hit_dice_used - recovered, 0)
        for r in sheet.resources:
            if r.recharge in ("short", "long"):
                r.used = 0
        for slot in sheet.spell_slots.values():
            slot.used = 0
        msgs.append(f"Long rest: HP, slots and resources restored; regained {recovered} hit dice")

    return msgs
