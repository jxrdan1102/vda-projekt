<script lang="ts">
    import {goto,invalidate, preloadData, pushState} from "$app/navigation";
    import {page} from '$app/stores';
    import { browser } from '$app/environment';
    import Modal from "$lib/components/Modal.svelte";
    import NewCompPage from "../[modellId]/addComponent/+page.svelte";
    import CompInfoPage from '../[modellId]/component-[componentId]/+page.svelte';
    import {COMPONENTS, Components} from "$lib/Mapping.js";
    import ComponentTable from '$lib/components/modelle/ComponentTable.svelte';
    import ModellRightPanel from '$lib/components/modelle/ModellRightPanel.svelte';

    export let data;

    export let form: {
        success?: boolean;
        message?: string;
        error?: string;
        code?: string;
        count?: number;
    } | null = null;

    let showConflictDialog = false;
    let conflictCount = 0;

    let editable = !data.modell.is_builtin;
    let name: string = data.modell?.name ?? '';
    let geo_me: string | null = data.modell?.geo_me != null ? data.modell.geo_me.toString() : null;
    let geo_mo: string | null = data.modell?.geo_mo != null ? data.modell.geo_mo.toString() : null;
    let geo_bn: string | null = data.modell?.geo_bn != null ? data.modell.geo_bn.toString() : null;
    let methode: string | null = data.modell?.methode != null ? data.modell.methode.toString() : null;
    let tsk_ausenmessung: number = data.modell?.tsk_ausenmessung ?? 0;
    let tsk_innenmessung: number = data.modell?.tsk_innenmessung ?? 0;
    let tsk_tiefenmessung: number = data.modell?.tsk_tiefenmessung ?? 0;
    let tsk_hoehenmessung: number = data.modell?.tsk_hoehenmessung ?? 0;
    let tsk_stufenmessung: number = data.modell?.tsk_stufenmessung ?? 0;
    let description: string = data.modell?.description ?? '';
    let formeldesc: string = data.modell?.formeldesc ?? '';
    let formel = data.modell.formel ?? '';
    let modellId = data.modellId;

    // Reaktiv speichern bei jeder Änderung
    $: if (browser) {
        sessionStorage.setItem('pendingModellData', JSON.stringify({
            name, geo_me, geo_mo, geo_bn, methode,
            tsk_ausenmessung, tsk_innenmessung, tsk_tiefenmessung,
            tsk_hoehenmessung, tsk_stufenmessung,
            description, formel, formeldesc
        }));
    }

    $: if (form?.code === 'FK_IN_USE') {
        if (browser) {
            const saved = sessionStorage.getItem('pendingModellData');
            if (saved) {
                const p = JSON.parse(saved);
                name = p.name;
                geo_me = p.geo_me;
                geo_mo = p.geo_mo;
                geo_bn = p.geo_bn;
                methode = p.methode;
                tsk_ausenmessung = p.tsk_ausenmessung;
                tsk_innenmessung = p.tsk_innenmessung;
                tsk_tiefenmessung = p.tsk_tiefenmessung;
                tsk_hoehenmessung = p.tsk_hoehenmessung;
                tsk_stufenmessung = p.tsk_stufenmessung;
                description = p.description;
                formel = p.formel;
                formeldesc = p.formeldesc;
            }
        }
        conflictCount = form.count ?? 0;
        showConflictDialog = true;
    }

    $: if (form?.success && browser) {
        sessionStorage.removeItem('pendingModellData');
    }

    async function createCopy() {
        const copyRes = await fetch(`/backend/modells/${data.modellId}/copy`, {
            method: 'POST',
            credentials: 'include'
        });
        if (!copyRes.ok) {
            alert('Fehler beim Erstellen der Kopie');
            return;
        }
        const copyJson = await copyRes.json();
        const newId = copyJson.new_id;

        const payload: Record<string, any> = {
            name,
            aufgabe_modell: data.modell.aufgabe_modell,
            geo_me: geo_me ? parseInt(geo_me) : undefined,
            geo_mo: geo_mo ? parseInt(geo_mo) : undefined,
            geo_bn: geo_bn ? parseInt(geo_bn) : undefined,
            methode: methode ? parseInt(methode) : undefined,
            tsk_ausenmessung,
            tsk_innenmessung,
            tsk_tiefenmessung,
            tsk_hoehenmessung,
            tsk_stufenmessung,
            description,
            formel,
            formeldesc,
        };

        Object.keys(payload).forEach(k => {
            if (payload[k] === undefined || payload[k] === null) delete payload[k];
        });

        await fetch(`/backend/modells/${newId}/r`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (browser) sessionStorage.removeItem('pendingModellData');
        showConflictDialog = false;
            await invalidate(`http://localhost:9999/modells/${data.modellId}/r`);
        goto(`/modelle/${newId}`);
    }

    $: fieldClass = `w-full h-6 border border-gray-400 px-2 text-sm py-0 ${editable ? 'bg-white' : 'bg-gray-50 cursor-not-allowed opacity-60'}`;
    $: inputClass = `w-full h-6 border border-gray-400 px-2 text-sm py-2 ${editable ? 'bg-white' : 'bg-gray-50 cursor-not-allowed opacity-60'}`;
    $: modellId = $page.params.modellId;
    $: componentDialogOpen = !!$page.state?.newComponent;
    $: showComponent = !!$page.state?.componentInfo;

    $: prozesstitel = (() => {
        switch (data.modell.aufgabe_modell) {
            case 1: return 'Prüfprozess';
            case 2: return 'Kalibrierprozess';
            case 3: return '3D-Prüfprozess';
            default: return 'Fehler';
        }
    })();

    async function onNewComponentClick(e: MouseEvent & { currentTarget: SVGElement }) {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();
        const href = `/modelle/${modellId}/addComponent`;
        const result = await preloadData(href);
        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { newComponent: result.data });
        } else {
            goto(href);
        }
    }

    async function onOpenComponent(e: MouseEvent, compId: number) {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();
        const href = `/modelle/${modellId}/component-${compId}`;
        const result = await preloadData(href);
        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { componentInfo: result.data });
        } else {
            goto(href);
        }
    }

    function closeModal() { history.back(); }
    let selectedRow: number | null = null;
import { onMount } from 'svelte';

onMount(() => {
    const added = $page.url.searchParams.get('added');
    if (added) {
        showToast('Komponente wurde hinzugefügt');
        history.replaceState({}, '', window.location.pathname);
    }
    const edited = $page.url.searchParams.get('edited');
    if (edited) {
        showToast('Komponente wurde aktualisiert');
        history.replaceState({}, '', window.location.pathname);
    }
});
    async function deleteComponent(compId: number) {
    const confirmed = confirm("Möchtest du diese Komponente wirklich löschen?");
    if (!confirmed) return;
    try {
        const res = await fetch(`/backend/components/${compId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Fehler beim Löschen der Komponente');
        data.modell.components = data.modell.components.filter((c: any) => c.id !== compId);
        showToast('Komponente wurde gelöscht');
    } catch (err) {
        console.error(err);
        showToast('Löschen fehlgeschlagen', 'error');
    }
}
    let showSaveMenu = false;

let toast: { message: string; type: 'success' | 'error' } | null = null;
let toastTimeout: ReturnType<typeof setTimeout>;

function showToast(message: string, type: 'success' | 'error' = 'success') {
    toast = { message, type };
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast = null, 3000);
}
import { hasUnsavedChanges } from '$lib/stores/unsaved';
import { beforeNavigate } from '$app/navigation';

let showUnsavedDialog = false;
let pendingNavigation: (() => void) | null = null;

let originalData = {
    name: data.modell?.name ?? '',
    geo_me: data.modell?.geo_me != null ? data.modell.geo_me.toString() : null,
    geo_mo: data.modell?.geo_mo != null ? data.modell.geo_mo.toString() : null,
    geo_bn: data.modell?.geo_bn != null ? data.modell.geo_bn.toString() : null,
    methode: data.modell?.methode != null ? data.modell.methode.toString() : null,
    tsk_ausenmessung: data.modell?.tsk_ausenmessung ?? 0,
    tsk_innenmessung: data.modell?.tsk_innenmessung ?? 0,
    tsk_tiefenmessung: data.modell?.tsk_tiefenmessung ?? 0,
    tsk_hoehenmessung: data.modell?.tsk_hoehenmessung ?? 0,
    tsk_stufenmessung: data.modell?.tsk_stufenmessung ?? 0,
    description: data.modell?.description ?? '',
    formel: data.modell?.formel ?? '',
    formeldesc: data.modell?.formeldesc ?? '',
};
let originalComponents = JSON.stringify(data.modell?.components ?? []);

hasUnsavedChanges.set(false);

$: hasUnsavedChanges.set(
    name !== originalData.name ||
    geo_me !== originalData.geo_me ||
    geo_mo !== originalData.geo_mo ||
    geo_bn !== originalData.geo_bn ||
    methode !== originalData.methode ||
    tsk_ausenmessung !== originalData.tsk_ausenmessung ||
    tsk_innenmessung !== originalData.tsk_innenmessung ||
    tsk_tiefenmessung !== originalData.tsk_tiefenmessung ||
    tsk_hoehenmessung !== originalData.tsk_hoehenmessung ||
    tsk_stufenmessung !== originalData.tsk_stufenmessung ||
    description !== originalData.description ||
    formel !== originalData.formel ||
    formeldesc !== originalData.formeldesc ||
    JSON.stringify(data.modell?.components ?? []) !== originalComponents
);

$: if (form?.success) {
    originalData = {
        name,
        geo_me,
        geo_mo,
        geo_bn,
        methode,
        tsk_ausenmessung,
        tsk_innenmessung,
        tsk_tiefenmessung,
        tsk_hoehenmessung,
        tsk_stufenmessung,
        description,
        formel,
        formeldesc,
    };
    originalComponents = JSON.stringify(data.modell?.components ?? []);
    hasUnsavedChanges.set(false);
}

let isSaving = false;

async function handleSubmit(actionValue: string) {
    isSaving = true;
    hasUnsavedChanges.set(false);
    
    // Programmatisch das Form submitten
    const form = document.querySelector('form') as HTMLFormElement;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'action';
    input.value = actionValue;
    form.appendChild(input);
    form.submit();
}
beforeNavigate(({ cancel, to }) => {
    if ($hasUnsavedChanges) {
        cancel();
        showUnsavedDialog = true;
        pendingNavigation = () => {
            hasUnsavedChanges.set(false);
            if (to?.url) window.location.href = to.url.href;
        };
    }
});


</script>
<svelte:window on:click={(e) => {
    if (showSaveMenu && !(e.target as HTMLElement).closest('.relative')) {
        showSaveMenu = false;
    }
}}/>
<section class="w-8xl space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" class="max-w-8xl space-y-6" action="?">
        <input type="number" name="aufgabe_modell" hidden bind:value={data.modell.aufgabe_modell} disabled={!editable} class={inputClass} />

<h1 class="text-base font-semibold border-b pb-2">{prozesstitel}
    <div class="float-right flex">
        <button type="submit" name="action" value="save"
        disabled={data.modell.is_builtin}
            on:click={() => handleSubmit('save')} class="disabled:opacity-40 disabled:cursor-not-allowed bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700">
            Speichern
        </button>
        <div class="relative">
            <button type="button"
            disabled={data.modell.is_builtin}
                on:click={() => showSaveMenu = !showSaveMenu}
                class="disabled:opacity-40 disabled:cursor-not-allowed bg-gray-600 text-white text-sm px-2 py-1 rounded-r border-l border-gray-500 hover:bg-gray-700">
                ▾
            </button>
            {#if showSaveMenu}
                <div class="absolute right-0 mt-1 bg-white border border-gray-200 rounded shadow-lg z-50 w-44">
                    <button type="button" on:click={() => { showSaveMenu = false; handleSubmit('continue'); }}
                        class="bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700">
                        Speichern & Schließen
                    </button>
                    <button type="button" on:click={() => { showSaveMenu = false; handleSubmit('close'); }}
                        class="bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700">
                        Speichern & Weiter
                    </button>
                </div>
            {/if}
        </div>
    </div>
</h1>

        

        {#if form?.error && form?.code !== 'FK_IN_USE'}
            <div class="bg-red-100 border border-red-300 text-red-700 px-4 py-2 rounded text-sm">
                {form.error}
            </div>
        {/if}

        {#if form?.success}
            <div class="bg-green-100 border border-green-300 text-green-700 px-4 py-2 rounded text-sm">
                {form.message}
            </div>
        {/if}

        <div class="flex gap-20 border rounded p-3 bg-gray-100">
            <div class="mr-5">
                <div class="mb-3">
                    <label class="block text-gray-700 text-xs mb-1">Modell</label>
                    <input type="text" name="name" bind:value={name} disabled={!editable} class={inputClass} />
                </div>
                <div>
                    <label class="block text-gray-700 text-xs mb-1">Aufgabe</label>
                    <div class="flex flex-col gap-1 px-1">
                        <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_ausenmessung" disabled={!editable} class="h-4 w-4 text-gray-600 border-gray-400 rounded {editable ? '' : 'cursor-not-allowed opacity-60'}" bind:checked={tsk_ausenmessung}/> Außenmessung</label>
                        <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_innenmessung" disabled={!editable} class="h-4 w-4 text-gray-600 border-gray-400 rounded {editable ? '' : 'cursor-not-allowed opacity-60'}" bind:checked={tsk_innenmessung}/> Innenmessung</label>
                        <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_tiefenmessung" disabled={!editable} class="h-4 w-4 text-gray-600 border-gray-400 rounded {editable ? '' : 'cursor-not-allowed opacity-60'}" bind:checked={tsk_tiefenmessung}/> Tiefenmessung</label>
                        <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_hoehenmessung" disabled={!editable} class="h-4 w-4 text-gray-600 border-gray-400 rounded {editable ? '' : 'cursor-not-allowed opacity-60'}" bind:checked={tsk_hoehenmessung}/> Höhenmessung</label>
                        <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_stufenmessung" disabled={!editable} class="h-4 w-4 text-gray-600 border-gray-400 rounded {editable ? '' : 'cursor-not-allowed opacity-60'}" bind:checked={tsk_stufenmessung}/> Stufenmessung</label>
                    </div>
                </div>
            </div>
            <div class="">
                <div class="mx-20 mb-3">
                    <label class="block text-gray-700 text-xs mb-1">Methode</label>
                    <select id="methode" name="methode" bind:value={methode} disabled={!editable} class={fieldClass}>
                        <option value="" disabled>Bitte wählen</option>
                        <option value="1">Direkt</option>
                        <option value="2">Direkt mit Einstellung</option>
                        <option value="3">Substitution</option>
                        <option value="4">Differenziell</option>
                    </select>
                </div>
                <fieldset class="col-span-3 border border-gray-300 p-3">
                    <legend class="text-sm font-medium text-gray-600 px-2">Geometrie</legend>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Messeinrichtung</label>
                            <select id="geo_me" name="geo_me" bind:value={geo_me} disabled={!editable} class={fieldClass}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value="1">Fläche</option>
                                <option value="2">Kugel</option>
                                <option value="3">Zylinder</option>
                                <option value="4">Bohrung</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Messobjekt</label>
                            <select id="geo_mo" name="geo_mo" bind:value={geo_mo} disabled={!editable} class={fieldClass}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value="1">Fläche</option>
                                <option value="2">Kugel</option>
                                <option value="3">Zylinder</option>
                                <option value="4">Bohrung</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Einstellnormal</label>
                            <select id="geo_bn" name="geo_bn" bind:value={geo_bn} disabled={!editable} class={fieldClass}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value="1">Fläche</option>
                                <option value="2">Kugel</option>
                                <option value="3">Zylinder</option>
                                <option value="4">Bohrung</option>
                            </select>
                        </div>
                    </div>
                </fieldset>
            </div>
            <ModellRightPanel
                bind:description
                bind:formel
                bind:formeldesc
                {editable}
            />
        </div>

        <ComponentTable
            components={data.modell.components}
            {editable}
            on:addComponent={onNewComponentClick}
            on:openComponent={(e) => onOpenComponent(e.detail.event, e.detail.compId)}
            on:deleteComponent={(e) => deleteComponent(e.detail)}
        />
    </form>

    {#if showConflictDialog}
        <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg shadow-lg p-6 w-96 space-y-3">
                <h2 class="text-base font-semibold text-gray-800">Modell wird verwendet</h2>
                <p class="text-sm text-gray-600">
                    Dieses Modell wird in <strong>{conflictCount}</strong>
                    {conflictCount === 1 ? 'Datensatz' : 'Datensätzen'} verwendet
                    und kann nicht geändert werden.
                </p>
                <p class="text-sm text-gray-600">
                    Möchtest du stattdessen eine Kopie erstellen und diese bearbeiten?
                </p>
                <div class="flex gap-2 pt-2">
                    <button
                        on:click={createCopy}
                        class="flex-1 bg-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-800"
                    >
                        Kopie erstellen
                    </button>
                    <button
                        on:click={() => {
                            showConflictDialog = false;
                            if (browser) sessionStorage.removeItem('pendingModellData');
                        }}
                        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 rounded hover:bg-gray-100"
                    >
                        Abbrechen
                    </button>
                </div>
            </div>
        </div>
    {/if}
    {#if toast}
    <div class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded shadow-lg text-sm text-white transition-all
        {toast.type === 'success' ? 'bg-[#1f3b5e]' : 'bg-red-600'}">
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
                <p class="text-sm text-gray-700">
                    Es gibt ungespeicherte Änderungen. Möchtest du die Seite wirklich verlassen?
                </p>
                <p class="text-xs text-gray-500">
                    Alle nicht gespeicherten Änderungen gehen verloren.
                </p>
            </div>
            <div class="px-5 py-3 flex justify-end gap-2 border-t border-gray-200" style="background-color: #f0f0f0;">
                <button
                    on:click={() => {
                        showUnsavedDialog = false;
                        pendingNavigation = null;
                    }}
                    class="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-200 transition"
                >
                    Abbrechen
                </button>
                <button
                    on:click={() => {
                        showUnsavedDialog = false;
                        pendingNavigation?.();
                        pendingNavigation = null;
                    }}
                    class="px-4 py-1.5 text-sm text-white rounded transition"
                    style="background-color: #1f3b5e;"
                >
                    Trotzdem verlassen
                </button>
            </div>
        </div>
    </div>
{/if}
</section>

<Modal open={componentDialogOpen} on:close={closeModal}>
    <div class="max-h-[80vh] overflow-y-auto p-4">
        <NewCompPage data={$page.state.newComponent} />
    </div>
</Modal>

<Modal open={showComponent} on:close={closeModal}>
    <div class="max-h-[80vh] overflow-y-auto p-4">
        <CompInfoPage data={$page.state.componentInfo} />
    </div>
</Modal>