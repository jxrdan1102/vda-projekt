import { error } from '@sveltejs/kit';
import type {PageServerLoad} from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { analyseprojektId } = params;

    const response = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/calc/r`, {
        method: 'GET',
        credentials: 'include'  // Wichtig für Cookie-Weitergabe etc.
    });

    if (!response.ok) {
        error(response.status === 404 ? 404 : 500, 'Die Messunsicherheit konnte nicht berechnet werden');
    }

    const responseBody = await response.json();
    return {
        title: 'Messunsicherheit:',
        messunsicherheit: responseBody
    };
};
