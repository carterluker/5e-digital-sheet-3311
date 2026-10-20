function Login() {
    return(
        <div className="login">
            <h2>Log in</h2>
            <form>
                <label htmlFor="username">Username</label>
                <input id="username" name="username" type="text" autoComplete="username" required />

                <label htmlFor="password">Password</label>
                <input id="password" name="password" type="password" autoComplete="current-password" required />

                <button type="submit">Log in</button>
            </form>
        </div>
    )
}

export default Login