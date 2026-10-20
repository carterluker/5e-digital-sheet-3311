import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router"

import { ApiError, api, getToken, setToken, type Backup, type Character, type Item, type Sheet } from "../common/api"

type Action = { type: string; [key: string]: unknown }

const SLOT_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9]
const COINS = ["cp", "sp", "ep", "gp", "pp"]
const label = (s: string) => s.replace(/_/g, " ")
const signed = (n: number) => (n >= 0 ? `+${n}` : `${n}`)

function Num({ value, onChange, min }: { value: number; onChange: (n: number) => void; min?: number }) {
    return <input type="number" value={value} min={min}
        onChange={(e) => onChange(Number.isNaN(e.target.valueAsNumber) ? 0 : e.target.valueAsNumber)} />
}

function Txt({ value, onChange, placeholder }: { value: string; onChange: (s: string) => void; placeholder?: string }) {
    return <input type="text" value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />
}

function CharacterSheetPage() {
    const { id } = useParams()
    const navigate = useNavigate()

    const [char, setChar] = useState<Character | null>(null)
    const [draft, setDraft] = useState<Sheet | null>(null)
    const [status, setStatus] = useState("")
    const [error, setError] = useState("")
    const [conflict, setConflict] = useState(false)
    const [log, setLog] = useState<string[]>([])
    const [backups, setBackups] = useState<Backup[]>([])

    // Mutable mirrors so async handlers never see stale state.
    const draftRef = useRef<Sheet | null>(null)
    const versionRef = useRef(0)
    const dirtyRef = useRef(false)
    const conflictRef = useRef(false)
    const queue = useRef<Promise<void>>(Promise.resolve())
    const timer = useRef<number | undefined>(undefined)

    // Small form state
    const [dmg, setDmg] = useState(1)
    const [hitDice, setHitDice] = useState(1)
    const [cond, setCond] = useState("")
    const [res, setRes] = useState({ name: "", maximum: 1, recharge: "long" })
    const [item, setItem] = useState<Item>({
        name: "", quantity: 1, weight: 0, kind: "gear", armor_type: null, base_ac: null, ac_bonus: 0, equipped: false, description: "",
    })

    function fail(err: unknown) {
        if (err instanceof ApiError && err.status === 401) {
            setToken(null)
            navigate("/login")
        } else if (err instanceof ApiError && err.status === 409) {
            conflictRef.current = true
            setConflict(true)
            setStatus("Conflict")
        } else setError((err as Error).message)
    }

    // Replace local state with an authoritative server copy.
    function adopt(c: Character) {
        versionRef.current = c.version
        draftRef.current = c.data
        dirtyRef.current = false
        conflictRef.current = false
        setConflict(false)
        setChar(c)
        setDraft(c.data)
    }

    async function loadBackups() {
        setBackups(await api<Backup[]>("GET", `/characters/${id}/backups`))
    }

    async function load() {
        setError("")
        try {
            adopt(await api<Character>("GET", `/characters/${id}`))
            setStatus("Loaded")
            await loadBackups()
        } catch (err) {
            fail(err)
        }
    }

    useEffect(() => {
        if (!getToken()) return void navigate("/login")
        load()
        return () => window.clearTimeout(timer.current)
    }, [id])

    // ---- autosave
    function doSave(): Promise<void> {
        return (queue.current = queue.current.then(async () => {
            if (!dirtyRef.current || conflictRef.current || !draftRef.current) return
            const sent = draftRef.current
            setStatus("Saving…")
            try {
                const saved = await api<Character>("PUT", `/characters/${id}`, { version: versionRef.current, data: sent })
                versionRef.current = saved.version
                setChar(saved) // refreshes derived stats and issues; the draft is left alone
                if (draftRef.current === sent) {
                    dirtyRef.current = false
                    setStatus("Saved")
                }
            } catch (err) {
                fail(err)
            }
        }))
    }

    function edit(fn: (s: Sheet) => void) {
        if (!draftRef.current) return
        const next = structuredClone(draftRef.current)
        fn(next)
        draftRef.current = next
        dirtyRef.current = true
        setDraft(next)
        setStatus("Unsaved changes…")
        window.clearTimeout(timer.current)
        timer.current = window.setTimeout(doSave, 800)
    }

    async function flush() {
        window.clearTimeout(timer.current)
        await doSave()
    }

    // ---- server-side bookkeeping actions
    async function run(action: Action) {
        setError("")
        await flush()
        if (conflictRef.current) return
        try {
            const r = await api<{ messages: string[]; character: Character }>("POST", `/characters/${id}/actions`, {
                action, version: versionRef.current,
            })
            adopt(r.character)
            setLog((l) => [...r.messages, ...l].slice(0, 20))
            setStatus("Saved")
        } catch (err) {
            fail(err)
        }
    }

    async function backupOp(fn: () => Promise<Character | void>) {
        setError("")
        await flush()
        if (conflictRef.current) return
        try {
            const c = await fn()
            if (c) adopt(c)
            await loadBackups()
        } catch (err) {
            fail(err)
        }
    }

    if (!draft || !char) return <main>{error ? <p className="error">{error}</p> : <p>Loading…</p>}</main>

    const d = char.derived
    const hp = draft.hp

    return (
        <main>
            <p>
                <strong>{status}</strong>
                {conflict && <> — the server has a newer version. <button onClick={load}>Reload</button></>}
            </p>
            {error && <p className="error">{error}</p>}

            <fieldset>
                <legend>Rule checks</legend>
                {char.issues.length === 0 ? <p>No issues.</p> : (
                    <ul>
                        {char.issues.map((i, n) => <li key={n} className={i.severity}>{i.severity}: {i.message} ({i.path})</li>)}
                    </ul>
                )}
            </fieldset>

            <fieldset>
                <legend>Basics</legend>
                <label>Name <Txt value={draft.name} onChange={(v) => edit((s) => { s.name = v })} /></label>{" "}
                <label>Race <Txt value={draft.race} onChange={(v) => edit((s) => { s.race = v })} /></label>{" "}
                <label>Class <Txt value={draft.character_class} onChange={(v) => edit((s) => { s.character_class = v })} /></label>{" "}
                <label>Subclass <Txt value={draft.subclass} onChange={(v) => edit((s) => { s.subclass = v })} /></label>
                <br />
                <label>Background <Txt value={draft.background} onChange={(v) => edit((s) => { s.background = v })} /></label>{" "}
                <label>Alignment <Txt value={draft.alignment} onChange={(v) => edit((s) => { s.alignment = v })} /></label>{" "}
                <label>Level <Num min={1} value={draft.level} onChange={(v) => edit((s) => { s.level = v })} /></label>{" "}
                <label>XP <Num min={0} value={draft.experience} onChange={(v) => edit((s) => { s.experience = v })} /></label>{" "}
                <label><input type="checkbox" checked={draft.inspiration}
                    onChange={(e) => edit((s) => { s.inspiration = e.target.checked })} /> Inspiration</label>
            </fieldset>

            <fieldset>
                <legend>Combat</legend>
                <p>
                    AC {d.armor_class} · Initiative {signed(d.initiative)} · Proficiency {signed(d.proficiency_bonus)} ·
                    Passive Perception {d.passive_perception}
                    {d.spell_save_dc !== null && <> · Spell DC {d.spell_save_dc} · Spell attack {signed(d.spell_attack_bonus!)}</>}
                </p>
                <label>HP <Num min={0} value={hp.current} onChange={(v) => edit((s) => { s.hp.current = v })} /></label>
                {" / "}
                <label>Max <Num min={0} value={hp.max} onChange={(v) => edit((s) => { s.hp.max = v })} /></label>{" "}
                <label>Temp <Num min={0} value={hp.temp} onChange={(v) => edit((s) => { s.hp.temp = v })} /></label>
                <p>
                    <Num min={0} value={dmg} onChange={setDmg} />{" "}
                    <button onClick={() => run({ type: "damage", amount: dmg })}>Damage</button>{" "}
                    <button onClick={() => run({ type: "heal", amount: dmg })}>Heal</button>{" "}
                    <button onClick={() => run({ type: "temp_hp", amount: dmg })}>Set temp HP</button>
                </p>
                {hp.current === 0 && (
                    <p>
                        Death saves: {draft.death_saves.successes} successes, {draft.death_saves.failures} failures{" "}
                        <button onClick={() => run({ type: "death_save" })}>Roll death save</button>
                    </p>
                )}
                <p>
                    Hit dice: {d.hit_dice_remaining}/{d.hit_dice_total}{d.hit_die ? ` (d${d.hit_die})` : ""}{" "}
                    <Num min={1} value={hitDice} onChange={setHitDice} />{" "}
                    <button onClick={() => run({ type: "spend_hit_dice", count: hitDice })}>Spend hit dice</button>
                </p>
                <p>
                    <button onClick={() => run({ type: "short_rest" })}>Short rest</button>{" "}
                    <button onClick={() => run({ type: "long_rest" })}>Long rest</button>
                </p>
                {log.length > 0 && <ul>{log.map((m, n) => <li key={n}>{m}</li>)}</ul>}
            </fieldset>

            <fieldset>
                <legend>Abilities, saves and skills</legend>
                <table>
                    <thead><tr><th>Ability</th><th>Score</th><th>Mod</th><th>Save prof.</th><th>Save</th></tr></thead>
                    <tbody>
                        {Object.keys(draft.abilities).map((a) => (
                            <tr key={a}>
                                <td>{a}</td>
                                <td><Num min={1} value={draft.abilities[a]} onChange={(v) => edit((s) => { s.abilities[a] = v })} /></td>
                                <td>{signed(d.ability_modifiers[a])}</td>
                                <td><input type="checkbox" checked={draft.save_proficiencies.includes(a)}
                                    onChange={(e) => edit((s) => {
                                        s.save_proficiencies = s.save_proficiencies.filter((x) => x !== a)
                                        if (e.target.checked) s.save_proficiencies.push(a)
                                    })} /></td>
                                <td>{signed(d.saving_throws[a])}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <br />
                <table>
                    <thead><tr><th>Skill</th><th>Prof.</th><th>Expertise</th><th>Bonus</th></tr></thead>
                    <tbody>
                        {Object.keys(d.skills).map((k) => (
                            <tr key={k}>
                                <td>{label(k)}</td>
                                <td><input type="checkbox" checked={draft.skill_proficiencies.includes(k)}
                                    onChange={(e) => edit((s) => {
                                        s.skill_proficiencies = s.skill_proficiencies.filter((x) => x !== k)
                                        if (e.target.checked) s.skill_proficiencies.push(k)
                                    })} /></td>
                                <td><input type="checkbox" checked={draft.skill_expertise.includes(k)}
                                    onChange={(e) => edit((s) => {
                                        s.skill_expertise = s.skill_expertise.filter((x) => x !== k)
                                        if (e.target.checked) s.skill_expertise.push(k)
                                    })} /></td>
                                <td>{signed(d.skills[k])}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </fieldset>

            <fieldset>
                <legend>Inventory</legend>
                <p>Weight {d.total_weight} / {d.carrying_capacity} lb{d.encumbered && <strong className="error"> — encumbered</strong>}</p>
                {draft.inventory.length > 0 && (
                    <table>
                        <thead><tr><th>Item</th><th>Kind</th><th>Qty</th><th>Weight</th><th>AC</th><th>Equipped</th><th></th></tr></thead>
                        <tbody>
                            {draft.inventory.map((it, n) => (
                                <tr key={n}>
                                    <td>{it.name}</td>
                                    <td>{it.kind}{it.armor_type ? ` (${it.armor_type})` : ""}</td>
                                    <td>{it.quantity}</td>
                                    <td>{it.weight}</td>
                                    <td>{it.base_ac ?? ""}{it.ac_bonus ? ` ${signed(it.ac_bonus)}` : ""}</td>
                                    <td>{["armor", "shield", "weapon"].includes(it.kind) && (
                                        <input type="checkbox" checked={it.equipped}
                                            onChange={(e) => run({ type: "equip", name: it.name, equipped: e.target.checked })} />
                                    )}</td>
                                    <td>
                                        <button onClick={() => run({ type: "remove_item", name: it.name, quantity: 1 })}>-1</button>{" "}
                                        <button onClick={() => run({ type: "remove_item", name: it.name, quantity: it.quantity })}>Remove</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
                <p>
                    <Txt placeholder="Item name" value={item.name} onChange={(v) => setItem({ ...item, name: v })} />{" "}
                    <select value={item.kind} onChange={(e) => setItem({ ...item, kind: e.target.value as Item["kind"], armor_type: e.target.value === "armor" ? "light" : null })}>
                        <option>gear</option><option>weapon</option><option>armor</option><option>shield</option>
                    </select>{" "}
                    {item.kind === "armor" && (<>
                        <select value={item.armor_type ?? "light"} onChange={(e) => setItem({ ...item, armor_type: e.target.value as Item["armor_type"] })}>
                            <option>light</option><option>medium</option><option>heavy</option>
                        </select>{" "}
                        <label>Base AC <Num value={item.base_ac ?? 10} onChange={(v) => setItem({ ...item, base_ac: v })} /></label>{" "}
                    </>)}
                    {(item.kind === "shield" || item.kind === "armor") &&
                        <label>AC bonus <Num value={item.ac_bonus} onChange={(v) => setItem({ ...item, ac_bonus: v })} /></label>}{" "}
                    <label>Qty <Num min={1} value={item.quantity} onChange={(v) => setItem({ ...item, quantity: v })} /></label>{" "}
                    <label>Weight <Num min={0} value={item.weight} onChange={(v) => setItem({ ...item, weight: v })} /></label>{" "}
                    <button disabled={!item.name.trim()} onClick={() => {
                        const it = { ...item, base_ac: item.kind === "armor" ? (item.base_ac ?? 10) : null }
                        run({ type: "add_item", item: it })
                        setItem({ ...item, name: "" })
                    }}>Add item</button>
                </p>
                <p>
                    Currency:{" "}
                    {COINS.map((c) => (
                        <label key={c}>{c} <Num min={0} value={draft.currency[c]} onChange={(v) => edit((s) => { s.currency[c] = v })} /> </label>
                    ))}
                </p>
            </fieldset>

            <fieldset>
                <legend>Resources and spell slots</legend>
                {draft.resources.length > 0 && (
                    <table>
                        <thead><tr><th>Resource</th><th>Remaining</th><th>Recharge</th><th></th></tr></thead>
                        <tbody>
                            {draft.resources.map((r, n) => (
                                <tr key={n}>
                                    <td>{r.name}</td>
                                    <td>{r.maximum - r.used} / {r.maximum}</td>
                                    <td>{r.recharge}</td>
                                    <td>
                                        <button onClick={() => run({ type: "use_resource", name: r.name })}>Use</button>{" "}
                                        <button onClick={() => edit((s) => { s.resources.splice(n, 1) })}>Delete</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
                <p>
                    <Txt placeholder="Resource name" value={res.name} onChange={(v) => setRes({ ...res, name: v })} />{" "}
                    <label>Max <Num min={0} value={res.maximum} onChange={(v) => setRes({ ...res, maximum: v })} /></label>{" "}
                    <select value={res.recharge} onChange={(e) => setRes({ ...res, recharge: e.target.value })}>
                        <option>short</option><option>long</option><option>none</option>
                    </select>{" "}
                    <button disabled={!res.name.trim()} onClick={() => {
                        edit((s) => { s.resources.push({ name: res.name.trim(), maximum: res.maximum, used: 0, recharge: res.recharge as "short" | "long" | "none" }) })
                        setRes({ ...res, name: "" })
                    }}>Add resource</button>
                </p>
                <table>
                    <thead><tr><th>Slot level</th><th>Max</th><th>Used</th><th></th></tr></thead>
                    <tbody>
                        {SLOT_LEVELS.map((lvl) => {
                            const slot = draft.spell_slots[lvl]
                            return (
                                <tr key={lvl}>
                                    <td>{lvl}</td>
                                    <td><Num min={0} value={slot?.maximum ?? 0}
                                        onChange={(v) => edit((s) => { s.spell_slots[lvl] = { maximum: v, used: Math.min(s.spell_slots[lvl]?.used ?? 0, v) } })} /></td>
                                    <td>{slot?.used ?? 0}</td>
                                    <td><button disabled={!slot || slot.used >= slot.maximum}
                                        onClick={() => run({ type: "use_spell_slot", level: lvl })}>Cast</button></td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </fieldset>

            <fieldset>
                <legend>Conditions</legend>
                <p>
                    {draft.conditions.length === 0 && "None "}
                    {draft.conditions.map((c) => (
                        <span key={c}>{label(c)} <button onClick={() => run({ type: "condition", name: c, active: false })}>x</button>{" "}</span>
                    ))}
                </p>
                <Txt placeholder="e.g. poisoned" value={cond} onChange={setCond} />{" "}
                <button disabled={!cond.trim()} onClick={() => { run({ type: "condition", name: cond, active: true }); setCond("") }}>Add</button>
            </fieldset>

            <fieldset>
                <legend>Notes</legend>
                <textarea rows={6} style={{ width: "100%" }} value={draft.notes} onChange={(e) => edit((s) => { s.notes = e.target.value })} />
            </fieldset>

            <fieldset>
                <legend>Backups</legend>
                <p>
                    <button onClick={() => backupOp(async () => { await api("POST", `/characters/${id}/backups`) })}>Back up now</button>{" "}
                    (an automatic backup is also taken while you edit)
                </p>
                {backups.length > 0 && (
                    <table>
                        <thead><tr><th>When</th><th>Name</th><th>Version</th><th>Reason</th><th></th></tr></thead>
                        <tbody>
                            {backups.map((b) => (
                                <tr key={b.id}>
                                    <td>{new Date(b.created_at).toLocaleString()}</td>
                                    <td>{b.name}</td><td>{b.version}</td><td>{b.reason}</td>
                                    <td><button onClick={() => {
                                        if (confirm("Replace the current sheet with this backup? The current state is backed up first.")) {
                                            backupOp(() => api<Character>("POST", `/characters/${id}/backups/${b.id}/restore`))
                                        }
                                    }}>Restore</button></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </fieldset>
        </main>
    )
}

export default CharacterSheetPage
