import { Navigate, Outlet } from 'react-router'

import { useSession } from './SessionContext.tsx'

/** Layout route: only renders its child routes for a signed-in user. */
function RequireSession() {
    const { status } = useSession()

    if (status === 'loading') {
        return <p>Loading...</p>
    }
    if (status === 'anonymous') {
        return <Navigate to="/login" replace />
    }
    return <Outlet />
}

export default RequireSession
