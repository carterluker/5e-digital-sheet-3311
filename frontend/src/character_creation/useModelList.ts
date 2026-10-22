import { useEffect, useState } from 'react'

import { authFetch } from '../login/api.ts'
import { useSession } from '../login/SessionContext.tsx'

interface ModelList<T> {
    url: string
    items: T[]
}

/**
 * Fetches a list of character component models (e.g. '/api/model/species/').
 * `items` is null while loading, or when `url` is null (e.g. a dependent selection hasn't been made).
 */
export function useModelList<T>(url: string | null): { items: T[] | null, error: string | null } {
    const { token } = useSession()
    const [loaded, setLoaded] = useState<ModelList<T> | null>(null)
    const [failedUrl, setFailedUrl] = useState<string | null>(null)

    useEffect(() => {
        if (!token || !url) {
            return
        }
        let cancelled = false

        async function load(sessionToken: string, listUrl: string) {
            try {
                const response = await authFetch(sessionToken, listUrl)
                if (!response.ok) {
                    throw new Error()
                }
                const items = await response.json()
                if (!cancelled) {
                    setLoaded({ url: listUrl, items })
                }
            } catch {
                if (!cancelled) {
                    setFailedUrl(listUrl)
                }
            }
        }
        load(token, url)

        return () => { cancelled = true }
    }, [token, url])

    // Ignore results that belong to a previous url.
    return {
        items: loaded !== null && loaded.url === url ? loaded.items : null,
        error: failedUrl !== null && failedUrl === url ? 'Could not load options. Please try again later.' : null,
    }
}
