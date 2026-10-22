const COOKIE_NAME = 'session_token'
const DEFAULT_LIFETIME_DAYS = 7

export function getSession(): string | null {
    const prefix = `${COOKIE_NAME}=`
    const entry = document.cookie.split('; ').find((c) => c.startsWith(prefix))
    return entry ? decodeURIComponent(entry.slice(prefix.length)) : null
}

export function setSession(token: string, days = DEFAULT_LIFETIME_DAYS) {
    const secure = window.location.protocol === 'https:' ? '; Secure' : ''
    document.cookie =
        `${COOKIE_NAME}=${encodeURIComponent(token)}; path=/; SameSite=Lax; max-age=${days * 24 * 60 * 60}${secure}`
}

export function clearSession() {
    document.cookie = `${COOKIE_NAME}=; path=/; SameSite=Lax; max-age=0`
}
