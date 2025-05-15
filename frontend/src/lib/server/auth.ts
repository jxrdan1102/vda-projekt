import type {RequestEvent} from '@sveltejs/kit';
import {jwtDecode} from 'jwt-decode';

export async function fetchUserIsAdmin(): Promise<boolean> {
    const response = await fetch('http://localhost:9999/auth/admin', {
        credentials: 'include',
    });

    if (!response.ok) return false;

    return await response.json(); // true oder false
}

type DecodedToken = {
    sub: string;
    id: number;
    exp?: number;
    iat?: number;
};

export const authenticateUser = (event: RequestEvent) => {
    const { cookies } = event;
    const token = cookies.get('access_token');
    if (!token) {
        return null;
    }

    try {
        const decoded = jwtDecode<DecodedToken>(token);
        if (decoded.exp) {
            const currentTime = Math.floor(Date.now() / 1000); // Aktuelle Zeit in Sekunden
            if (decoded.exp < currentTime) {
                console.error('Token abgelaufen');
                return null;  // Token ist abgelaufen
            }
        }
        return {
            sub: decoded.sub,
            id: decoded.id
        };
    } catch (error) {
        console.error('Ungültiges Token:', error);
        return null;
    }
};
