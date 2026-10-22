import { Navigate } from "react-router"


// Exists purely to redirct root to the login page.
function HomeRedirect() {
    return(
        <Navigate to="/login" replace />
    )
}

export default HomeRedirect
