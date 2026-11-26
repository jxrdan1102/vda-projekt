<script lang="ts">
    import { toasts, dismiss, confirmRequest } from '$lib/notify';

    const STYLE = {
        success: 'border-green-300 bg-green-50 text-green-800',
        error: 'border-red-300 bg-red-50 text-red-800',
        info: 'border-blue-300 bg-blue-50 text-blue-800'
    };
    const ICON = { success: '✓', error: '!', info: 'i' };

    function onKey(e: KeyboardEvent) {
        if (!$confirmRequest) return;
        if (e.key === 'Escape') $confirmRequest.resolve(false);
    }
</script>

<svelte:window onkeydown={onKey} />

<!-- Meldungen -->
<div class="fixed top-20 right-4 z-[60] flex flex-col gap-2 w-80" aria-live="polite">
    {#each $toasts as t (t.id)}
        <div class="flex items-start gap-2 rounded border px-3 py-2 text-sm shadow-md {STYLE[t.kind]}" role="status">
            <span class="font-bold" aria-hidden="true">{ICON[t.kind]}</span>
            <span class="flex-1">{t.message}</span>
            <button class="opacity-60 hover:opacity-100" aria-label="Schließen" onclick={() => dismiss(t.id)}>✕</button>
        </div>
    {/each}
</div>

<!-- Bestätigungsdialog -->
{#if $confirmRequest}
    <div class="fixed inset-0 z-[70] flex items-center justify-center bg-black/40" role="presentation"
         onclick={(e) => e.target === e.currentTarget && $confirmRequest?.resolve(false)}>
        <div class="w-full max-w-sm rounded-lg bg-white p-5 shadow-xl" role="alertdialog" aria-modal="true" aria-labelledby="confirm-text">
            <p id="confirm-text" class="mb-4 text-sm text-gray-800">{$confirmRequest.message}</p>
            <div class="flex justify-end gap-2 text-sm">
                <button class="rounded bg-gray-200 px-3 py-1 hover:bg-gray-300" onclick={() => $confirmRequest?.resolve(false)}>Abbrechen</button>
                <!-- svelte-ignore a11y_autofocus -->
                <button autofocus
                        class="rounded px-3 py-1 text-white {$confirmRequest.danger ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-800 hover:bg-gray-700'}"
                        onclick={() => $confirmRequest?.resolve(true)}>{$confirmRequest.confirmLabel}</button>
            </div>
        </div>
    </div>
{/if}
