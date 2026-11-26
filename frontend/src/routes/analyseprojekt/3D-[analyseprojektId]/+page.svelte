<script lang="ts">
    import { onSaveShortcut } from '$lib/shortcuts';
    // ─────────────────────────────────────────────
    // Imports
    // ─────────────────────────────────────────────
    import { goto, preloadData, pushState } from '$app/navigation';
    import { page } from '$app/stores';
    import Modal from '$lib/components/Modal.svelte';

    import AnalyseprojektHeader from '$lib/components/analyseprojekt/AnalyseprojektHeader.svelte';
    import ReportButton from '$lib/components/analyseprojekt/ReportButton.svelte';
    import KonstantenGrid       from '$lib/components/analyseprojekt/KonstantenGrid.svelte';
    import KomponentenTabelle   from '$lib/components/analyseprojekt/KomponentenTabelle.svelte';
    import { DREID_COLUMNS }    from '$lib/components/analyseprojekt/types';

    // Inline-Pages für Modals (unverändert)
    import NewModelPage from './component-[anakompId]/+page.svelte';
    import NewConstPage from './constant-[anakonstId]/+page.svelte';
    import KmgInfoPage  from './kmg/+page.svelte';

    import { confirmLeave, fingerprint, hasPendingInlineEdits } from '$lib/stores/unsaved';
    import { browser } from '$app/environment';
    // ─────────────────────────────────────────────
    // Daten
    // ─────────────────────────────────────────────
    export let data;
    let analyseprojekt = data.analyseprojekt;
    $: analyseprojektId = $page.params.analyseprojektId;

    let name              = analyseprojekt.name              ?? '';
    let aenderungszustand = analyseprojekt.aenderungszustand ?? '';
    let identnr           = analyseprojekt?.identnr?.toString() ?? '';
    let partno            = analyseprojekt?.partno ?? '';
    let remark            = analyseprojekt.remark            ?? '';
    let tolfaktor         = analyseprojekt?.tolfaktor ? 1 : 0;

    // ─────────────────────────────────────────────
    // Modal-Zustände
    // ─────────────────────────────────────────────
    $: showConstModal  = !!$page.state?.selectedConstant;
    $: modellDialogOpen = !!$page.state?.updateComp;
    $: showKmg         = !!$page.state?.kmgInfo;

    function closeModal() {
        goto(`/analyseprojekt/3D-${analyseprojektId}`);
    }

    // ─────────────────────────────────────────────
    // KMG-Modal öffnen
    // ─────────────────────────────────────────────
    async function openKmg() {
        const href = `/analyseprojekt/3D-${analyseprojektId}/kmg`;
        const result = await preloadData(href);
        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { kmgInfo: result.data });
        } else {
            goto(href);
        }
    }
        // ─────────────────────────────────────────────
    // Report
    // ─────────────────────────────────────────────
    export let form: {
    success?: boolean;
    message?: string;
    error?: string;
} | null = null;

let toast: { message: string; type: 'success' | 'error' } | null = null;
let toastTimeout: ReturnType<typeof setTimeout>;

function showToast(message: string, type: 'success' | 'error' = 'success') {
    toast = { message, type };
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast = null, 3000);
}

$: if (form?.success) showToast(form.message ?? 'Gespeichert');
$: if (form?.error) showToast(form.error, 'error');

let isSaving = false;
let showUnsavedDialog = false;
let pendingNavigation: (() => void) | null = null;

// Stand beim Öffnen – damit wird beim Verlassen verglichen
const kopfFelder = () => [name, aenderungszustand, identnr, partno, remark, tolfaktor];
const ausgangsstand = fingerprint(kopfFelder());

confirmLeave(
    () =>
        !isSaving &&
        $page.data.user?.role !== 'readonly' &&
        (fingerprint(kopfFelder()) !== ausgangsstand ||
            // Komponenten/Konstanten werden einzeln gespeichert; offen ist nur, was getippt, aber nicht gespeichert wurde
            hasPendingInlineEdits(analyseprojekt.anakomp) ||
            hasPendingInlineEdits(analyseprojekt.anakonst)),
    (weiter) => {
        showUnsavedDialog = true;
        pendingNavigation = weiter;
    }
);

async function handleSubmit(actionValue: string) {
    isSaving = true;
    const formEl = document.querySelector('form') as HTMLFormElement;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'action';
    input.value = actionValue;
    formEl.appendChild(input);
    formEl.submit();
}
</script>
<!-- Strg+S = Speichern -->
<svelte:window on:keydown={(e) => onSaveShortcut(e, () => {
    if ($page.data.user?.role !== 'readonly' && !isSaving) handleSubmit('speichern');
})} />
<section class="space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" action="?/speichern">
        <AnalyseprojektHeader
            {analyseprojekt}
            bind:name
            bind:aenderungszustand
            bind:identnr
            bind:partno
            bind:remark
            bind:tolfaktor
        >
            <!-- Seitenspezifische Buttons -->
            <svelte:fragment slot="buttons">
                <button
                    type="button"
                    on:click={() => goto(`/analyseprojekt/3D-${analyseprojektId}/MU`)}
                    class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right"
                >
                    Berechnen
                </button>
                <button
 data-write                    type="button" title="Speichern (Strg+S)" on:click={() => handleSubmit('speichern')}
                    class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right"
                >
                    Speichern
                </button>
                <button
                    type="button"
                    on:click={openKmg}
                    name="kmg"
                    class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right"
                >
                {analyseprojekt?.kmg?.kmg_ident ?? 'KMG'}
                </button>
                <ReportButton {analyseprojektId} class="float-right mr-2" />
            </svelte:fragment>
            <!-- 3D braucht kein hidden fk_modell → kein slot="hidden-fields" nötig -->
        </AnalyseprojektHeader>
    </form>

    <!-- Konstanten (kein Filter in 3D) -->
    <KonstantenGrid bind:konstanten={analyseprojekt.anakonst} />

    <!-- Komponenten-Tabelle (dblclick edit, 3D-Spalten) -->
    <KomponentenTabelle
        bind:komponenten={analyseprojekt.anakomp}
        columns={DREID_COLUMNS}
        editMode="inline"
        showSaveAll={true}
    />
    {#if toast}
    <div class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded shadow-lg text-sm text-white transition-all"
        style="background-color: {toast.type === 'success' ? '#1f3b5e' : '#dc2626'}">
        {toast.message}
    </div>
{/if}

{#if showUnsavedDialog}
    <div class="fixed inset-0 flex items-center justify-center z-50" style="background: rgba(0,0,0,0.45);">
        <div class="bg-white rounded-lg shadow-xl w-[400px] overflow-hidden">
            <div class="px-5 py-4" style="background-color: #1f3b5e;">
                <h2 class="text-white font-semibold text-base">Ungespeicherte Änderungen</h2>
            </div>
            <div class="px-5 py-4 space-y-2">
                <p class="text-sm text-gray-700">Es gibt ungespeicherte Änderungen. Möchtest du die Seite wirklich verlassen?</p>
                <p class="text-xs text-gray-500">Alle nicht gespeicherten Änderungen gehen verloren.</p>
            </div>
            <div class="px-5 py-3 flex justify-end gap-2 border-t border-gray-200" style="background-color: #f0f0f0;">
                <button on:click={() => { showUnsavedDialog = false; pendingNavigation = null; }}
                    class="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-200 transition">
                    Abbrechen
                </button>
                <button on:click={() => { showUnsavedDialog = false; pendingNavigation?.(); pendingNavigation = null; }}
                    class="px-4 py-1.5 text-sm text-white rounded transition"
                    style="background-color: #1f3b5e;">
                    Trotzdem verlassen
                </button>
            </div>
        </div>
    </div>
{/if}
</section>

<!-- Modals (unverändert) -->
<Modal open={modellDialogOpen} on:close={closeModal}>
    <NewModelPage data={$page.state.updateComp} />
</Modal>

<Modal open={showConstModal} on:close={closeModal}>
    <NewConstPage data={$page.state.selectedConstant} />
</Modal>

<Modal open={showKmg} on:close={closeModal}>
    <KmgInfoPage data={$page.state.kmgInfo} fk_kmg={analyseprojekt.fk_kmg} />
</Modal>
