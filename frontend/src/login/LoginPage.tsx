import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'

import FormError from './components/FormError.tsx'
import FormField from './components/FormField.tsx'
import SubmitButton from './components/SubmitButton.tsx'
import { useSession } from './SessionContext.tsx'

import './login.css'

function LoginPage() {
    const { token, login, createUser } = useSession()
    const navigate = useNavigate()

    const [creating, setCreating] = useState(false)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [pending, setPending] = useState(false)

    // Check if already logged in (existing session cookie or just authenticated).
    useEffect(() => {
        if (token) {
            navigate('/characters', { replace: true })
        }
    }, [token, navigate])

    async function handleSubmit(e: React.SubmitEvent<HTMLFormElement>) {
        e.preventDefault()
        setError(null)
        setPending(true)
        try {
            await (creating ? createUser : login)(username, password)
        } catch (err) {
            // Maybe add more verbose errors?
            setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
        } finally {
            setPending(false)
        }
    }

    return (
        <main>
            <div className="login">
                <h2>{creating ? 'Create account' : 'Log in'}</h2>
                <form onSubmit={handleSubmit}>
                    <FormField
                        id="username"
                        label="Username"
                        autoComplete="username"
                        value={username}
                        onChange={setUsername}
                    />
                    <FormField
                        id="password"
                        label="Password"
                        type="password"
                        autoComplete={creating ? 'new-password' : 'current-password'}
                        value={password}
                        onChange={setPassword}
                    />
                    <FormError message={error} />
                    <SubmitButton pending={pending}>{creating ? 'Create account' : 'Log in'}</SubmitButton>
                    <button
                        type="button"
                        className="link"
                        onClick={() => { setCreating(!creating); setError(null) }}
                    >
                        {creating ? 'Have an account? Log in' : 'Need an account? Create one'}
                    </button>
                </form>
            </div>
        </main>
    )
}

export default LoginPage
