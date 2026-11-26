/* ── Tastenkürzel ── */

/**
 * Strg+S (bzw. ⌘+S auf dem Mac) abfangen und stattdessen `save` aufrufen.
 * Verhindert, dass der Browser "Seite speichern unter …" öffnet.
 */
export function onSaveShortcut(e: KeyboardEvent, save: () => void) {
    if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey && e.key.toLowerCase() === 's') {
        e.preventDefault();
        if (!e.repeat) save();
    }
}
