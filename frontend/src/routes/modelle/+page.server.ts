import type {PageServerLoad} from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
    const response = await fetch('http://localhost:9999/modells/r', {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    console.log(responseBody);
    return {
        title: 'Modelle',
        modelle: responseBody
    }
}