import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router"

import { ApiError, api, getToken, setToken, type Character, type Summary } from "../common/api"

function CharacterListPage() {
    const navigate = useNavigate()
    const [chars, setChars] = useState<Summary[] | null>(null)
    const [name, setName] = useState("")
    const [error, setError] = useState("")

    function fail(err: unknown) {
        if (err instanceof ApiError && err.status === 401) {
            setToken(null)
            navigate("/login")
        } else setError((err as Error).message)
    }

    useEffect(() => {
        if (!getToken()) return void navigate("/login")
        api<Summary[]>("GET", "/characters").then(setChars).catch(fail)
    }, [])

    async function create(e: React.FormEvent) {
        e.preventDefault()
        try {
            const c = await api<Character>("POST", "/characters", { data: { name } })
            navigate(`/characters/${c.id}`)
        } catch (err) {
            fail(err)
        }
    }

    async function remove(c: Summary) {
        if (!confirm(`Delete ${c.name}? This cannot be undone.`)) return
        try {
            await api("DELETE", `/characters/${c.id}`)
            setChars((chars ?? []).filter((x) => x.id !== c.id))
        } catch (err) {
            fail(err)
        }
    }

    return (
        <main>
            <h2>Your characters</h2>
            {error && <p className="error">{error}</p>}
            {chars === null ? <p>Loading…</p> : chars.length === 0 ? <p>No characters yet.</p> : (
                <table>
                    <thead><tr><th>Name</th><th>Race</th><th>Class</th><th>Level</th><th>Updated</th><th></th></tr></thead>
                    <tbody>
                        {chars.map((c) => (
                            <tr key={c.id}>
                                <td><Link to={`/characters/${c.id}`}>{c.name}</Link></td>
                                <td>{c.race}</td><td>{c.character_class}</td><td>{c.level}</td>
                                <td>{new Date(c.updated_at).toLocaleString()}</td>
                                <td><button onClick={() => remove(c)}>Delete</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            <h3>New character</h3>
            <form onSubmit={create}>
                <input placeholder="Name" required value={name} onChange={(e) => setName(e.target.value)} />{" "}
                <button type="submit">Create</button>
            </form>
        </main>
    )
}

export default CharacterListPage
