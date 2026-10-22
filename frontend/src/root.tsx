import { Links, Meta, Outlet, Scripts, ScrollRestoration } from "react-router"

import Header from './common/components/Header.tsx'
import { SessionProvider } from './login/SessionContext.tsx'

import './index.css'
import './common/forms.css'

export function Layout({ children }: { children: React.ReactNode }) {
	return(
		<html lang="en">
			<head>
				<meta charSet="UTF-8" />
				<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
				<meta name="viewport" content="width=device-width, initial-scale=1.0" />
				<title>5e Digital Character Sheet</title>
				<Meta />
				<Links />
			</head>
			<body>
				{children}
				<ScrollRestoration />
				<Scripts />
			</body>
		</html>
	)
}

export default function Root() {
	return(
		<SessionProvider>
			<div>
				<Header></Header>

				<Outlet />
			</div>
		</SessionProvider>
	)
}
