import { Link, useNavigate } from "react-router"

import { api, getToken, setToken } from "../api"

function Header() {
    const navigate = useNavigate()

    async function logout() {
        await api("POST", "/auth/logout").catch(() => {})
        setToken(null)
        navigate("/login")
    }

    return(
        <header>
            <h1>Carter's Digital Character Sheet</h1>
            <nav>
                <Link to="/characters">Characters</Link>{" "}
                {getToken() && <button onClick={logout}>Log out</button>}
            </nav>
            <hr></hr>
        </header>
    )
}

export default Header
