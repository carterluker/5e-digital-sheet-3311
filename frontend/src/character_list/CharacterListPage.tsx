import { useEffect, useState } from 'react'

import { authFetch } from '../login/api.ts'
import { useSession } from '../login/SessionContext.tsx'

import CharacterList from './components/CharacterList.tsx'
import { type CharacterSummary } from './components/CharacterListItem.tsx'

import './character_list.css'

function CharacterListPage() {
    const { token } = useSession()

    const [characters, setCharacters] = useState<CharacterSummary[] | null>(null)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!token) {
            return
        }
        let cancelled = false

        async function load(sessionToken: string) {
            try {
                const response = await authFetch(sessionToken, '/api/characters/')
                if (!response.ok) {
                    throw new Error()
                }
                const data = await response.json()
                if (!cancelled) {
                    setCharacters(data)
                }
            } catch {
                if (!cancelled) {
                    setError('Could not load your characters. Please try again later.')
                }
            }
        }
        load(token)

        return () => { cancelled = true }
    }, [token])

    return (
        <main>
            <div className="characters">
                <h2>Your characters</h2>
                {error && <p className="form-error" role="alert">{error}</p>}
                {!error && characters === null && <p>Loading...</p>}
                {characters !== null && <CharacterList characters={characters} />}
            </div>
        </main>
    )
}

export default CharacterListPage
