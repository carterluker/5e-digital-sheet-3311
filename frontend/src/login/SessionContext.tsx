import { createContext, useContext, useEffect, useState } from 'react'

import { clearSession, getSession, setSession } from './session.ts'

interface SessionContextValue {
    token: string | null
    login: (username: string, password: string) => Promise<void>
    createUser: (username: string, password: string) => Promise<void>
    logout: () => void
}

const SessionContext = createContext<SessionContextValue | null>(null)

const ERROR_MESSAGES: Record<number, string> = {
    401: 'Incorrect username or password.',
    409: 'That username is already taken.',
    503: 'The server is unavailable. Please try again later.',
}

async function post(url: string, body: object): Promise<{ session_token?: string }> {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })
    if (!response.ok) {
        throw new Error(ERROR_MESSAGES[response.status] ?? 'Something went wrong. Please try again.')
    }
    return response.json()
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>(null)

    // Read the cookie after mount so server/client markup never differs.
    useEffect(() => {
        setToken(getSession())
    }, [])

    function startSession(newToken: string | undefined) {
        if (!newToken) {
            throw new Error('Something went wrong. Please try again.')
        }
        setSession(newToken)
        setToken(newToken)
    }

    async function login(username: string, password: string) {
        const data = await post('/api/login/', { username, password })
        startSession(data.session_token)
    }

    async function createUser(username: string, password: string) {
        const data = await post('/api/create_user/', { username, password, login_after: true })
        startSession(data.session_token)
    }

    function logout() {
        clearSession()
        setToken(null)
    }

    return (
        <SessionContext.Provider value={{ token, login, createUser, logout }}>
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
