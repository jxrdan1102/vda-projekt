<script lang="ts">
    // ─────────────────────────────────────────────
    // Imports
    // ─────────────────────────────────────────────
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    import AnalyseprojektHeader from '$lib/components/analyseprojekt/AnalyseprojektHeader.svelte';
    import KonstantenGrid      from '$lib/components/analyseprojekt/KonstantenGrid.svelte';
    import KomponentenTabelle  from '$lib/components/analyseprojekt/KomponentenTabelle.svelte';
    import { STANDARD_COLUMNS } from '$lib/components/analyseprojekt/types';


    import { hasUnsavedChanges } from '$lib/stores/unsaved';
    import { beforeNavigate } from '$app/navigation';
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
    let remark            = analyseprojekt.remark            ?? '';
    let tolfaktor         = analyseprojekt?.tolfaktor ? 1 : 0;

    // ─────────────────────────────────────────────
    // Konstanten-Filter: constnum 2/3/4 nur bei tolfaktor=true
    // ─────────────────────────────────────────────
    $: konstFilterFn = (k: any) =>
        (k.constnum != 2 && k.constnum != 3 && k.constnum != 4) || tolfaktor;

    // ─────────────────────────────────────────────
    // Report
    // ─────────────────────────────────────────────
let showReportMenu = false;

async function openReport(extended: boolean = false) {
    const start = '2024-01-01';
    const end   = '2024-12-31';
    const response = await fetch(
        `/backend/anamu/${analyseprojektId}/report?start_date=${start}&end_date=${end}&extended=${extended}`,
        { method: 'GET', credentials: 'include', headers: { 'Content-Type': 'application/json' } }
    );
    const blob = await response.blob();
    window.open(window.URL.createObjectURL(blob));
    showReportMenu = false;
}
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

let originalData = {
    name: data.analyseprojekt?.name ?? '',
    aenderungszustand: data.analyseprojekt?.aenderungszustand ?? '',
    identnr: data.analyseprojekt?.identnr?.toString() ?? '',
    remark: data.analyseprojekt?.remark ?? '',
    tolfaktor: data.analyseprojekt?.tolfaktor ? 1 : 0,
};
let originalAnakomp = JSON.stringify(data.analyseprojekt?.anakomp ?? []);
let originalAnakonst = JSON.stringify(data.analyseprojekt?.anakonst ?? []);

hasUnsavedChanges.set(false);

$: hasUnsavedChanges.set(
    name !== originalData.name ||
    aenderungszustand !== originalData.aenderungszustand ||
    (identnr?.toString() ?? '') !== originalData.identnr ||
    (remark ?? '') !== originalData.remark ||
    (tolfaktor ? 1 : 0) !== originalData.tolfaktor ||
    JSON.stringify(data.analyseprojekt?.anakomp ?? []) !== originalAnakomp ||
    JSON.stringify(data.analyseprojekt?.anakonst ?? []) !== originalAnakonst
);

$: if (form?.success) {
    originalData = {
        name,
        aenderungszustand,
        identnr: identnr?.toString() ?? '',
        remark: remark ?? '',
        tolfaktor,
    };
    originalAnakomp = JSON.stringify(data.analyseprojekt?.anakomp ?? []);
    originalAnakonst = JSON.stringify(data.analyseprojekt?.anakonst ?? []);
    hasUnsavedChanges.set(false);
}

beforeNavigate(({ cancel, to }) => {
    if (isSaving) return;
    if ($hasUnsavedChanges) {
        cancel();
        showUnsavedDialog = true;
        pendingNavigation = () => {
            hasUnsavedChanges.set(false);
            if (to?.url) goto(to.url.href);  // ← goto statt window.location.href
        };
    }
});

async function handleSubmit(actionValue: string) {
    isSaving = true;
    hasUnsavedChanges.set(false);
    const formEl = document.querySelector('form') as HTMLFormElement;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'action';
    input.value = actionValue;
    formEl.appendChild(input);
    formEl.submit();
}


$: {
    const checks = {
        name: name !== originalData.name,
        aenderungszustand: aenderungszustand !== originalData.aenderungszustand,
        identnr: (identnr?.toString() ?? '') !== originalData.identnr,
        remark: (remark ?? '') !== originalData.remark,
        tolfaktor: tolfaktor !== originalData.tolfaktor,
        anakomp: JSON.stringify(data.analyseprojekt?.anakomp ?? []) !== originalAnakomp,
        anakonst: JSON.stringify(data.analyseprojekt?.anakonst ?? []) !== originalAnakonst,
    };
    console.log('unsaved checks:', checks);
}
</script>
<svelte:window on:click={(e) => {
    if (showReportMenu && !(e.target as HTMLElement).closest('.report-dropdown')) {
        showReportMenu = false;
    }
}}/>
<section class="space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">

    <form method="POST" action="?/speichern">
        <AnalyseprojektHeader
            {analyseprojekt}
            bind:name
            bind:aenderungszustand
            bind:identnr
            bind:remark
            bind:tolfaktor
        >
            <!-- Seitenspezifische Buttons -->
            <svelte:fragment slot="buttons">
                <button
                    type="button"
                    on:click={() => goto(`/analyseprojekt/${analyseprojektId}/MU`)}
                    class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right"
                >
                    Berechnen
                </button>
                <button
                    type="button" on:click={() => handleSubmit('speichern')}
                    class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right"
                >
                    Speichern
                </button>
                <div class="report-dropdown relative inline-block float-right mr-2">
    <div class="flex">
        <button
            type="button"
            on:click={() => openReport(false)}
            class="bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700"
        >
            Report öffnen
        </button>
        <button
            type="button"
            on:click={() => showReportMenu = !showReportMenu}
            class="bg-gray-600 text-white text-sm px-2 py-1 rounded-r border-l border-gray-500 hover:bg-gray-700"
        >
            ▾
        </button>
        {#if showReportMenu}
            <div class="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded shadow-lg z-50 w-44">
                <button
                    type="button"
                    on:click={() => openReport(true)}
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                    Erweiterter Report
                </button>
            </div>
        {/if}
    </div>
</div>
            </svelte:fragment>

            <!-- fk_modell als hidden field (nur Standard-Variante) -->
            <svelte:fragment slot="hidden-fields">
                <input
                    hidden
                    type="number"
                    name="fk_modell"
                    bind:value={data.analyseprojekt.modell.id}
                />
            </svelte:fragment>
        </AnalyseprojektHeader>
    </form>

    <!-- Konstanten -->
    <KonstantenGrid
        bind:konstanten={analyseprojekt.anakonst}
        filterFn={konstFilterFn}
    />

    <!-- Komponenten-Tabelle (inline edit, alle 5 Felder) -->
    <KomponentenTabelle
        bind:komponenten={analyseprojekt.anakomp}
        columns={STANDARD_COLUMNS}
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
