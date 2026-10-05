import { browser } from '$app/environment';
import { goto } from '$app/navigation';

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function refreshToken(): Promise<boolean> {
    if (isRefreshing && refreshPromise) return refreshPromise;
    
    isRefreshing = true;
    refreshPromise = fetch('http://localhost:9999/auth/refresh_token', {
        method: 'GET',
        credentials: 'include',
    }).then(res => {
        isRefreshing = false;
        refreshPromise = null;
        return res.ok;
    }).catch(() => {
        isRefreshing = false;
        refreshPromise = null;
        return false;
    });
    
    return refreshPromise;
}

export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const res = await fetch(url, { ...options, credentials: 'include' });
    
    if (res.status === 401) {
        const refreshed = await refreshToken();
        
        if (refreshed) {
            return fetch(url, { ...options, credentials: 'include' });
        } else {
            if (browser) goto('/login');
            throw new Error('Session abgelaufen');
        }
    }
    
    return res;
}