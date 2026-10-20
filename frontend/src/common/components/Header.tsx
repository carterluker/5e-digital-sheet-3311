import { Link, useLocation, useNavigate } from "react-router"

import { api } from "../api"

function Header() {
    const navigate = useNavigate()
    const onLogin = useLocation().pathname === "/login"

    async function logout() {
        await api("POST", "/auth/logout").catch(() => {})
        navigate("/login")
    }

    return(
        <header>
            <h1>5.5e Digital Character Sheet</h1>
            <nav>
                <Link to="/characters">Characters</Link>{" "}
                {!onLogin && <button onClick={logout}>Log out</button>}
            </nav>
            <hr></hr>
        </header>
    )
}

export default Header
