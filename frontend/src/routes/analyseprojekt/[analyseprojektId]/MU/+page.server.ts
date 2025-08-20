import type {PageServerLoad} from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { analyseprojektId } = params;

    const response = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/calc/r`, {
        method: 'GET',
        credentials: 'include'  // Wichtig für Cookie-Weitergabe etc.
    });

    if (!response.ok) {
        throw new Error('Fehler beim Abrufen der Messunsicherheit');
    }

    const responseBody = await response.json();
    console.log(responseBody);
    return {
        title: 'Messunsicherheit:',
        messunsicherheit: responseBody
    };
};
