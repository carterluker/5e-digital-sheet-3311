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
            <h1>5.5e Digital Character Sheet</h1>
            <nav>
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
