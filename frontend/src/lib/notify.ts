import { writable } from 'svelte/store';

/* ── Meldungen oben rechts (statt alert) ── */

export type Toast = { id: number; kind: 'success' | 'error' | 'info'; message: string };

export const toasts = writable<Toast[]>([]);
let nextId = 1;

function show(kind: Toast['kind'], message: string, ms = 4000) {
    const id = nextId++;
    toasts.update((all) => [...all, { id, kind, message }]);
    setTimeout(() => dismiss(id), ms);
}

export function dismiss(id: number) {
    toasts.update((all) => all.filter((t) => t.id !== id));
}

export const toast = {
    success: (message: string) => show('success', message),
    error: (message: string) => show('error', message, 7000),
    info: (message: string) => show('info', message)
};

/* ── Bestätigungsdialog (statt confirm) ── */

export type ConfirmRequest = {
    message: string;
    confirmLabel: string;
    danger: boolean;
    resolve: (ok: boolean) => void;
};

export const confirmRequest = writable<ConfirmRequest | null>(null);

/** Zeigt den Dialog und liefert true, wenn bestätigt wurde. */
export function askConfirm(
    message: string,
    { confirmLabel = 'Löschen', danger = true }: { confirmLabel?: string; danger?: boolean } = {}
): Promise<boolean> {
    return new Promise((resolve) => {
        confirmRequest.set({
            message,
            confirmLabel,
            danger,
            resolve: (ok) => {
                confirmRequest.set(null);
                resolve(ok);
            }
        });
    });
}

/**
 * Für Formulare: onsubmit={confirmForm('… wirklich löschen?')}
 * Hält das Absenden an, fragt nach und schickt das Formular bei "Ja" ab.
 */
export function confirmForm(message: string, options?: { confirmLabel?: string; danger?: boolean }) {
    return async (e: SubmitEvent) => {
        const form = e.currentTarget as HTMLFormElement;
        if (form.dataset.confirmed === '1') {
            delete form.dataset.confirmed;
            return;
        }
        e.preventDefault();
        if (await askConfirm(message, options)) {
            form.dataset.confirmed = '1';
            form.requestSubmit();
        }
    };
}
