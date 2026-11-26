import { error } from '@sveltejs/kit';
import type {LayoutServerLoad} from './$types';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { analyseprojektId } = params;
    const response = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/r`, {
        method: 'GET',
        credentials: 'include',
    });
    if (!response.ok) error(response.status === 404 ? 404 : response.status, 'Analyseprojekt nicht gefunden');
    const analyseprojekt = await response.json();
    return { analyseprojekt };
};
