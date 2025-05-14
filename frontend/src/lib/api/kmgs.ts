
export const fetchKmgs = async (): Promise<any[]> => {
    const response = await fetch('http://localhost:9999/kmgs');
    if (!response.ok) {
        throw new Error('Fehler beim Laden der KMGs');
    }
    const data = await response.json();
    return data; // oder data.kmgs, wenn die API ein 'kmgs' Array zurückgibt
};