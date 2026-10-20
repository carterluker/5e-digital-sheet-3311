import { Navigate } from "react-router"

function HomeRedirect() {
    return(
        <Navigate to="/login" replace />
    )
}

export default HomeRedirect
