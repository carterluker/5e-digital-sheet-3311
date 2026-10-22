import { createContext, useContext, useEffect, useState } from 'react'

import { authFetch } from './api.ts'
import { clearSession, getSession, setSession } from './session.ts'

type SessionStatus = 'loading' | 'authenticated' | 'anonymous'

interface SessionContextValue {
    token: string | null
    status: SessionStatus
    username: string | null
    login: (username: string, password: string) => Promise<void>
    createUser: (username: string, password: string) => Promise<void>
    logout: () => Promise<void>
}

const SessionContext = createContext<SessionContextValue | null>(null)

const GENERIC_ERROR = 'Something went wrong. Please try again.'

const ERROR_MESSAGES: Record<number, string> = {
    401: 'Incorrect username or password.',
    409: 'That username is already taken.',
    422: 'Check username (3+ chars) and password (8+ chars).',
    503: 'The server is unavailable. Please try again later.',
}

async function post(url: string, body: object): Promise<{ session_token?: string }> {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })
    if (!response.ok) {
        throw new Error(ERROR_MESSAGES[response.status] ?? GENERIC_ERROR)
    }
    return response.json()
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>(null)
    const [status, setStatus] = useState<SessionStatus>('loading')
    const [username, setUsername] = useState<string | null>(null)

    // Ask the backend who the token belongs to. A rejected token is dropped; other failures
    // (e.g. the database being down) keep the cookie so the user isn't logged out by an outage.
    async function loadUser(sessionToken: string) {
        try {
            const response = await authFetch(sessionToken, '/api/user/me/')
            if (response.ok) {
                const data = await response.json()
                setToken(sessionToken)
                setUsername(data.username)
                setStatus('authenticated')
                return
            }
            if (response.status === 401) {
                clearSession()
            }
        } catch {
            // Network failure: fall through to anonymous, keeping the cookie.
        }
        setToken(null)
        setUsername(null)
        setStatus('anonymous')
    }

    // Read the cookie after mount so server/client markup never differs.
    useEffect(() => {
        const existing = getSession()
        if (existing) {
            loadUser(existing)
        } else {
            setStatus('anonymous')
        }
    }, [])

    async function startSession(newToken: string | undefined) {
        if (!newToken) {
            throw new Error(GENERIC_ERROR)
        }
        setSession(newToken)
        await loadUser(newToken)
    }

    async function login(username: string, password: string) {
        const data = await post('/api/user/login/', { username, password })
        await startSession(data.session_token)
    }

    async function createUser(username: string, password: string) {
        const data = await post('/api/user/create/', { username, password, login_after: true })
        await startSession(data.session_token)
    }

    async function logout() {
        const current = token ?? getSession()
        clearSession()
        setToken(null)
        setUsername(null)
        setStatus('anonymous')
        if (current) {
            // Best effort: the session is already gone locally either way.
            try {
                await authFetch(current, '/api/user/logout/', { method: 'POST' })
            } catch {
                // Ignore; the server expires the session on its own.
            }
        }
    }

    return (
        <SessionContext.Provider value={{ token, status, username, login, createUser, logout }}>
            {children}
        </SessionContext.Provider>
    )
}

export function useSession(): SessionContextValue {
    const context = useContext(SessionContext)
    if (!context) {
        throw new Error('useSession must be used within a SessionProvider')
    }
    return context
}
