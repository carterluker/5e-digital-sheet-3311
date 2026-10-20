import { useState } from "react"
import { useNavigate } from "react-router"

import { api, setToken } from "../common/api"

function LoginPage() {
    const navigate = useNavigate()
    const [mode, setMode] = useState<"login" | "register">("login")
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")

    async function submit(e: React.FormEvent) {
        e.preventDefault()
        setError("")
        try {
            const creds = { username, password }
            if (mode === "register") await api("POST", "/auth/register", creds)
            const { access_token } = await api("POST", "/auth/login", creds)
            setToken(access_token)
            navigate("/characters")
        } catch (err) {
            setError((err as Error).message)
        }
    }

    return (
        <main>
            <div className="login">
                <h2>{mode === "login" ? "Log in" : "Register"}</h2>
                <form onSubmit={submit}>
                    <div>
                        <label htmlFor="username">Username</label>{" "}
                        <input id="username" name="username" type="text" autoComplete="username" required
                            value={username} onChange={(e) => setUsername(e.target.value)} />
                    </div>

                    <div>
                        <label htmlFor="password">Password</label>{" "}
                        <input id="password" name="password" type="password" minLength={8} required
                            autoComplete={mode === "login" ? "current-password" : "new-password"}
                            value={password} onChange={(e) => setPassword(e.target.value)} />
                    </div>

                    <button type="submit">{mode === "login" ? "Log in" : "Register"}</button>{" "}
                    <button type="button" onClick={() => setMode(mode === "login" ? "register" : "login")}>
                        {mode === "login" ? "Need an account?" : "Have an account?"}
                    </button>
                    {error && <p className="error">{error}</p>}
                </form>
            </div>
        </main>
    )
}

export default LoginPage
