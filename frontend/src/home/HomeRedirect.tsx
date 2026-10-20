import { Navigate } from "react-router"

import { getToken } from "../common/api"

function HomeRedirect() {
    // Rendered client-side only (SPA mode), so localStorage is available.
    return(
        <Navigate to={getToken() ? "/characters" : "/login"} replace />
    )
}

export default HomeRedirect
