// Thin wrapper around the backend REST API. The token lives in localStorage.

export type Abilities = Record<string, number>
export type Item = {
    name: string; quantity: number; weight: number
    kind: "gear" | "weapon" | "armor" | "shield"
    armor_type: "light" | "medium" | "heavy" | null
    base_ac: number | null; ac_bonus: number; equipped: boolean; description: string
}
export type Resource = { name: string; maximum: number; used: number; recharge: "short" | "long" | "none" }
export type Sheet = {
    name: string; race: string; character_class: string; subclass: string; background: string; alignment: string
    level: number; experience: number; inspiration: boolean
    abilities: Abilities
    save_proficiencies: string[]; skill_proficiencies: string[]; skill_expertise: string[]
    hp: { max: number; current: number; temp: number }
    hit_dice_used: number
    death_saves: { successes: number; failures: number }
    inventory: Item[]
    currency: Record<string, number>
    resources: Resource[]
    spell_slots: Record<string, { maximum: number; used: number }>
    conditions: string[]
    notes: string
}
export type Derived = {
    proficiency_bonus: number; ability_modifiers: Record<string, number>
    saving_throws: Record<string, number>; skills: Record<string, number>
    initiative: number; armor_class: number; passive_perception: number
    hit_die: number | null; hit_dice_total: number; hit_dice_remaining: number
    spell_save_dc: number | null; spell_attack_bonus: number | null
    total_weight: number; carrying_capacity: number; encumbered: boolean
}
export type Issue = { severity: "error" | "warning"; path: string; message: string }
export type Character = {
    id: number; name: string; version: number; data: Sheet; layout: unknown[]
    derived: Derived; issues: Issue[]
}
export type Summary = { id: number; name: string; race: string; character_class: string; level: number; updated_at: string }
export type Backup = { id: number; version: number; reason: string; name: string; created_at: string }

export class ApiError extends Error {
    status: number
    constructor(status: number, message: string) {
        super(message)
        this.status = status
    }
}

const TOKEN_KEY = "token"
export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t: string | null) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY))

function errorText(body: any, fallback: string): string {
    const d = body?.detail
    if (typeof d === "string") return d
    if (Array.isArray(d)) return d.map((e) => `${(e.loc ?? []).slice(1).join(".")}: ${e.msg}`).join("; ")
    return fallback
}

export async function api<T = any>(method: string, path: string, body?: unknown): Promise<T> {
    const token = getToken()
    const res = await fetch(`/api${path}`, {
        method,
        headers: {
            ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: body !== undefined ? JSON.stringify(body) : undefined,
    })
    if (res.status === 204) return undefined as T
    const json = await res.json().catch(() => null)
    if (!res.ok) throw new ApiError(res.status, errorText(json, res.statusText))
    return json as T
}
