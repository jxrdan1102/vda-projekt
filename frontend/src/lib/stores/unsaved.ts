import { beforeNavigate, goto } from '$app/navigation';

/* ── Rückfrage "Ungespeicherte Änderungen" beim Verlassen einer Seite ── */

/**
 * Wert vergleichbar machen, damit gleiche Inhalte auch gleich aussehen:
 * null / undefined / '' → '' · true/false → '1'/'0' · 1 und "1" und "1,0" → '1'
 */
export function norm(v: unknown): string {
    if (v === null || v === undefined) return '';
    if (typeof v === 'boolean') return v ? '1' : '0';
    const s = String(v).trim();
    const n = Number(s.replace(',', '.'));
    return s !== '' && !Number.isNaN(n) ? String(n) : s;
}

/** Fingerabdruck mehrerer Formularwerte (zum Vergleich "vorher ↔ jetzt") */
export function fingerprint(values: unknown[]): string {
    return values.map(norm).join('\u0001');
}

/**
 * true, wenn in einer Liste (Komponenten / Konstanten) ein Wert eingetippt,
 * aber noch nicht gespeichert wurde. Die Tabellen halten Eingaben in
 * Feldern "xxxTemp" und übernehmen sie erst beim Speichern nach "xxx".
 */
export function hasPendingInlineEdits(rows: Record<string, unknown>[] | null | undefined): boolean {
    return (rows ?? []).some((row) =>
        Object.keys(row).some((k) => k.endsWith('Temp') && norm(row[k]) !== norm(row[k.slice(0, -4)]))
    );
}

/**
 * Beim Verlassen nachfragen, wenn `isDirty()` true liefert.
 * - Link / Menü / Zurück-Knopf in der App: eigener Dialog über `ask(weiter)`
 * - Tab schließen oder neu laden: Rückfrage des Browsers
 * Geprüft wird erst im Moment des Verlassens – so zählt immer der aktuelle Stand.
 */
export function confirmLeave(isDirty: () => boolean, ask: (weiter: () => void) => void) {
    let bypass = false;
    beforeNavigate(({ cancel, to, type }) => {
        if (bypass || !isDirty()) return;
        cancel();
        if (type === 'leave') return; // Browser zeigt seine eigene Rückfrage
        ask(() => {
            bypass = true;
            if (to?.url) goto(to.url.href);
        });
    });
}
