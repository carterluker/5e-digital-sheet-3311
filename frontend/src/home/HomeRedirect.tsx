import { Navigate } from "react-router"

function HomeRedirect() {
    // The session cookie is HttpOnly, so auth state isn't visible here; /characters redirects to /login on 401.
    return(
        <Navigate to={"/characters"} replace />
    )
}

export default HomeRedirect
