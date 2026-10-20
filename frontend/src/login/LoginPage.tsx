function LoginPage() {
    return (
        <main>
            <div className="login">
                <h2>Log in</h2>
                <form>
                    <div>
                        <label htmlFor="username">Username</label>
                        <input id="username" name="username" type="text" autoComplete="username" required />
                    </div>
                    
                    <div>
                        <label htmlFor="password">Password</label>
                        <input id="password" name="password" type="password" autoComplete="current-password" required />
                    </div>
                    
                    <button type="submit">Log in</button>
                </form>
            </div>
        </main>
    )
}

export default LoginPage