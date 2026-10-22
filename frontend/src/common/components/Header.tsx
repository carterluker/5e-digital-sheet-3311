import { useNavigate } from 'react-router'

import { useSession } from '../../login/SessionContext.tsx'

function Header() {
    const { status, username, logout } = useSession()
    const navigate = useNavigate()

    async function handleLogout() {
        await logout()
        navigate('/login')
    }

    return(
        <header>
            <h1>Carter's Digital Character Sheet</h1>
            <nav>
                <ul>
                    <li><a href="">Home</a></li>
                    <li><a href="">About</a></li>
                </ul>
            </nav>
            {status === 'authenticated' && (
                <p>
                    Signed in as {username} <button type="button" onClick={handleLogout}>Log out</button>
                </p>
            )}
            <hr></hr>
        </header>
    )
}

export default Header
