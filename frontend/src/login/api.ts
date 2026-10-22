export function authFetch(token: string, url: string, init: RequestInit = {}): Promise<Response> {
    const headers = new Headers(init.headers)
    headers.set('Authorization', `Bearer ${token}`)
    return fetch(url, { ...init, headers })
}
