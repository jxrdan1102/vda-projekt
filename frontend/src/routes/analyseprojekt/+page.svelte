<script lang="ts">
    import NewModelPage from './add/+page.svelte';
    import {page} from '$app/stores';
    import {goto, preloadData, pushState} from '$app/navigation';
    import Modal from "$lib/components/Modal.svelte";
    import { onMount } from 'svelte';
    export let data;

    $: modellDialogOpen = !!$page.state?.newModell;

    async function onNewModellClick(e: MouseEvent & { currentTarget: HTMLAnchorElement }) {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();

        const { href } = e.currentTarget;
        const result = await preloadData(href);

        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { newModell: result.data });
        } else {
            goto(href);
        }
    }

    function closeModal() {
        history.back();
    }

    async function deleteProjekt(projektId: number) {
        const confirmed = confirm("Möchtest du dieses Modell wirklich löschen?");
        if (!confirmed) return;

        try {
            const res = await fetch(`/backend/anamu/${projektId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!res.ok) throw new Error('Fehler beim Löschen des Modells');

            data.analyseprojekt = data.analyseprojekt.filter((c: any) => c.id !== projektId);
        } catch (err) {
            console.error(err);
            alert('Löschen fehlgeschlagen');
        }
    }

    let selectedModelId: number | null = null;
    let aufgabe_modell_value: string = "";

    function handleSelectChange(e: Event) {
        const id = Number((e.target as HTMLSelectElement).value);
        selectedModelId = id;

        const model = models.find(m => m.id === id);
        aufgabe_modell_value = model ? model.aufgabe_modell : "";
    }

    let showDuplicateModal = false;
    let duplicateProjektId: number | null = null;
    let duplicateName = "";

    function openDuplicateModal(id: number) {
        duplicateProjektId = id;
        duplicateName = "";
        showDuplicateModal = true;
    }

    async function confirmDuplicate() {
        if (!duplicateProjektId) return;

        const res = await fetch(`/backend/anamu/${duplicateProjektId}/duplicate`, {
            method: "POST",
            credentials: 'include',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name: duplicateName}),
        });

        if (res.ok) {
            const result = await res.json();
            console.log("Duplikat erstellt:", result);
            showDuplicateModal = false;
        } else {
            alert("Fehler beim Duplizieren");
        }
    }

    $: openId = $page.url.searchParams.get('open');
    onMount(() => {
            loadModels();
        const open = $page.url.searchParams.get('open');
        if (open) {
            loadModels();
            showForm = !showForm;
        }
        history.replaceState({}, '', '/analyseprojekt');
    });

    function goToProjekt(id: number, prozess: number) {
        if (prozess === 3) goto(`http://localhost:5173/analyseprojekt/3D-${id}`)
        else goto(`http://localhost:5173/analyseprojekt/${id}`)
    }

    let showForm = false;
    let models: any;

    async function loadModels() {
        const res = await fetch('/api/modelle');
        if (res.ok) {
            models = await res.json();
        } else {
            models = [];
        }
    }

    let filterProjekt = '';
let filterAenderungsstand = '';
let filterModell = '';
let filterIdentnummer = '';
let filterDatum = '';

let filterModellId = '';



$: gefilterteProjekte = data.analyseprojekt.filter((p: any) => {
    return (
        (!filterProjekt || p.name?.toLowerCase().includes(filterProjekt.toLowerCase())) &&
        (!filterAenderungsstand || p.aenderungszustand?.toLowerCase().includes(filterAenderungsstand.toLowerCase())) &&
        (!filterModellId || p.modell?.id === parseInt(filterModellId)) &&
        (!filterIdentnummer || p.identnr?.toString().includes(filterIdentnummer)) &&
        (!filterDatum || p.creation?.includes(filterDatum))
    );
});

let showModellFilter = false;
let filterModellProzess = '';
let filterModellAufgabe = '';
let filterModellMethode = '';
let filterModellMe = '';
let filterModellMo = '';

$: gefilterteModelsForFilter = (models ?? []).filter((m: any) => {
    let aufgabeMatch = true;
    if (filterModellAufgabe) {
        if (filterModellProzess === '3') {
            aufgabeMatch = m.aufgabe === parseInt(filterModellAufgabe);
        } else {
            aufgabeMatch = m[filterModellAufgabe] === 1;
        }
    }
    return (
        (!filterModellProzess || m.aufgabe_modell === parseInt(filterModellProzess)) &&
        aufgabeMatch &&
        (!filterModellMethode || m.methode === parseInt(filterModellMethode)) &&
        (!filterModellMe || m.geo_me === parseInt(filterModellMe)) &&
        (!filterModellMo || m.geo_mo === parseInt(filterModellMo))
    );
});

$: if (filterModellProzess) filterModellAufgabe = '';

$: selectedModellName = filterModellId
    ? (models ?? []).find((m: any) => m.id === parseInt(filterModellId))?.name ?? 'Modell'
    : 'Modell';
</script>
<svelte:window on:click={(e) => {
    if (showModellFilter && !(e.target as HTMLElement).closest('.relative')) {
        showModellFilter = false;
    }
}}/>
<style>
    .table-row:nth-child(odd) {
        background-color: #f5f5f5;
    }
    .table-row:hover {
        background-color: #e8eef5;
    }
</style>

<div class="max-w-7xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-2rem)]">
        <!-- Page Header -->
    <div class="flex items-center gap-4 text-2xl font-semibold mb-6" style="color: #1f3b5e;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
            <path d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
        </svg>
        <span>Analyseprojekte</span>
    </div>

<div class="grid grid-cols-5 gap-2 mb-4">
    <input bind:value={filterProjekt} class="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-400" placeholder="Projekt" />
    <input bind:value={filterAenderungsstand} class="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-400" placeholder="Änderungsstand" />
<div class="relative">
    <button
    type="button"
    on:click={() => { loadModels(); showModellFilter = !showModellFilter; }}
    class="w-full border border-gray-300 rounded px-2 py-1 text-sm text-left focus:outline-none focus:border-blue-400 bg-white {filterModellId ? 'text-black' : 'text-gray-500'}"
>
    {selectedModellName}
</button>

    {#if showModellFilter}
        <div class="absolute z-50 top-full left-0 mt-1 bg-white border border-gray-300 rounded shadow-lg p-3 w-[480px] space-y-2">
            <!-- Filter innerhalb des Panels -->
            <div class="grid grid-cols-5 gap-1">
                <select bind:value={filterModellProzess} class="border border-gray-200 rounded px-1 py-1 text-xs focus:outline-none focus:border-blue-400">
                    <option value="">Prozess</option>
                    <option value="1">Prüfprozess</option>
                    <option value="2">Kalibrierprozess</option>
                    <option value="3">3D-Prüfprozess</option>
                </select>
                <select bind:value={filterModellAufgabe} class="border border-gray-200 rounded px-1 py-1 text-xs focus:outline-none focus:border-blue-400">
                    <option value="">Aufgabe</option>
                    {#if filterModellProzess === '3'}
                        <option value="1">Durchmesser</option>
                        <option value="2">Abstand</option>
                        <option value="3">Richtung</option>
                        <option value="4">Koaxialität</option>
                        <option value="5">Form</option>
                        <option value="6">Winkel</option>
                        <option value="7">Position</option>
                    {:else}
                        <option value="tsk_ausenmessung">Außenmessung</option>
                        <option value="tsk_innenmessung">Innenmessung</option>
                        <option value="tsk_hoehenmessung">Höhenmessung</option>
                        <option value="tsk_tiefenmessung">Tiefenmessung</option>
                        <option value="tsk_stufenmessung">Stufenmessung</option>
                    {/if}
                </select>
                <select bind:value={filterModellMethode} class="border border-gray-200 rounded px-1 py-1 text-xs focus:outline-none focus:border-blue-400">
                    <option value="">Methode</option>
                    <option value="1">Direkt</option>
                    <option value="2">Direkt mit Einstellung</option>
                    <option value="3">Substitution</option>
                    <option value="4">Differenziell</option>
                </select>
                <select bind:value={filterModellMe} class="border border-gray-200 rounded px-1 py-1 text-xs focus:outline-none focus:border-blue-400">
                    <option value="">Messeinrichtung</option>
                    <option value="1">Fläche</option>
                    <option value="2">Kugel</option>
                    <option value="3">Zylinder</option>
                    <option value="4">Bohrung</option>
                </select>
                <select bind:value={filterModellMo} class="border border-gray-200 rounded px-1 py-1 text-xs focus:outline-none focus:border-blue-400">
                    <option value="">Messobjekt</option>
                    <option value="1">Fläche</option>
                    <option value="2">Kugel</option>
                    <option value="3">Zylinder</option>
                    <option value="4">Bohrung</option>
                </select>
            </div>

            <!-- Gefilterte Modelle -->
            <div class="max-h-48 overflow-y-auto border border-gray-200 rounded divide-y divide-gray-100">
                {#if !models}
                    <div class="px-3 py-2 text-xs text-gray-400">Laden...</div>
                {:else if gefilterteModelsForFilter.length === 0}
                    <div class="px-3 py-2 text-xs text-gray-400">Keine Modelle gefunden</div>
                {:else}
                    {#each gefilterteModelsForFilter as m}
                        <button
                            type="button"
                            on:click={() => { filterModellId = m.id.toString(); showModellFilter = false; }}
                            class="w-full text-left px-3 py-1.5 text-xs hover:bg-[#e8eef5] {filterModellId === m.id.toString() ? 'bg-[#e8eef5] font-medium text-[#1f3b5e]' : ''}"
                        >
                            {m.name}
                        </button>
                    {/each}
                {/if}
            </div>

            <!-- Reset -->
            {#if filterModellId}
                <button
                    type="button"
                    on:click={() => { filterModellId = ''; showModellFilter = false; }}
                    class="text-xs text-gray-500 hover:text-red-500"
                >
                    Filter zurücksetzen
                </button>
            {/if}
        </div>
    {/if}
</div>
    <input bind:value={filterIdentnummer} class="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-400" placeholder="Identnummer" />
<input 
    type="date" 
    bind:value={filterDatum} 
    class="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-400 {filterDatum ? 'text-black' : 'text-gray-400'}"
/></div>

    <!-- Table Header -->
    <div class="border border-gray-300 rounded-t-md grid grid-cols-4 items-center font-semibold px-4 py-2 text-sm" style="background-color: #fafafb; color: #2B6CB0;">
        <div class="w-1/2">Analyseprojekt</div>
        <div class="w-1/2">Änderungsstand</div>
        <div class="w-1/2">Identnummer</div>
        <div class="flex justify-between items-center">
            <span>Datum</span>
            <button on:click={() => {loadModels(); showForm = !showForm;}} title="Neues Projekt hinzufügen" class="focus:outline-none" aria-label="Neues Projekt hinzufügen">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 hover:scale-110 transition-transform" style="color: #2B6CB0;">
                    <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    </div>

    {#if showForm}
        <form method="POST" class="border border-t-0 border-gray-300 px-4 py-3 flex flex-wrap items-center gap-4" style="background-color: #e8eef5;">
            <input id="name" name="name" required placeholder="Name"
                class="border border-gray-300 rounded px-2 py-1 w-48 text-sm focus:outline-none focus:border-blue-400" />

            <input id="aenderungszustand" name="aenderungszustand" placeholder="Änderungsstand"
                class="border border-gray-300 rounded px-2 py-1 w-48 text-sm focus:outline-none focus:border-blue-400" />

            <select id="modell" name="modell" required
                class="border border-gray-300 rounded px-2 py-1 w-48 text-sm focus:outline-none focus:border-blue-400"
                on:change={handleSelectChange}>
                <option value="" disabled selected>Modell wählen</option>
                {#each models as modell}
                    <option value={modell.id} selected={openId == modell.id}>{modell.name} (ID: {modell.id})</option>
                {/each}
            </select>

            <input id="aufgabe_modell" hidden name="aufgabe_modell" bind:value={aufgabe_modell_value} />

            <button type="submit"
                class="text-white rounded px-3 py-1 text-sm font-medium transition-colors hover:opacity-90"
                style="background-color: #2d4a7a;">
                Erstellen
            </button>
        </form>
    {/if}

    <!-- Table Body -->
<div class="border border-t-0 border-gray-300 divide-y divide-gray-200 overflow-y-auto flex-1">
{#each gefilterteProjekte as analyseprojekt}
            <div class="grid  odd:bg-[#ebebec] even:bg-[#fafafb] grid-cols-4 px-4 py-2 cursor-pointer text-sm" on:dblclick={() => goToProjekt(analyseprojekt.id, analyseprojekt.modell.aufgabe_modell)}>
                <div class="w-1/2">{analyseprojekt.name}</div>
                <div class="w-1/2">{analyseprojekt.aenderungszustand}</div>
                <div class="w-1/2">{analyseprojekt.identnr}</div>
                <div class=" flex justify-between items-center">
<span class="text-gray-600">
    {analyseprojekt.creation 
        ? new Date(analyseprojekt.creation).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) 
        : '—'}
</span>                    <div class="flex gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" on:click={() => openDuplicateModal(analyseprojekt.id)} fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 cursor-pointer transition-colors" style="color: #4a90d9;" on:mouseenter={e => e.currentTarget.style.color='#1f3b5e'} on:mouseleave={e => e.currentTarget.style.color='#4a90d9'}>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.5 8.25V6a2.25 2.25 0 0 0-2.25-2.25H6A2.25 2.25 0 0 0 3.75 6v8.25A2.25 2.25 0 0 0 6 16.5h2.25m8.25-8.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-7.5A2.25 2.25 0 0 1 8.25 18v-1.5m8.25-8.25h-6a2.25 2.25 0 0 0-2.25 2.25v6" />
                        </svg>
                        <svg xmlns="http://www.w3.org/2000/svg" on:click={() => deleteProjekt(analyseprojekt.id)} fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-red-500 hover:text-red-700 cursor-pointer">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                        </svg>
                    </div>
                </div>
            </div>
        {/each}
    </div>
</div>

{#if showDuplicateModal}
    <div class="fixed inset-0 flex items-center justify-center z-50" style="background-color: rgba(26,43,74,0.4);">
        <div class="bg-white rounded-xl p-6 shadow-xl w-full max-w-md">
            <h2 class="text-xl font-semibold mb-4" style="color: #1f3b5e;">Analyseprojekt duplizieren</h2>

            <label class="block text-sm font-medium text-gray-700 mb-1">Neuer Projektname</label>
            <input
                type="text"
                bind:value={duplicateName}
                class="w-full border border-gray-300 rounded px-3 py-2 mb-4 focus:outline-none focus:ring focus:border-blue-400"
                placeholder="z. B. Mein Projekt (Kopie)"
            />

            <div class="flex justify-end gap-3">
                <button
                    on:click={() => (showDuplicateModal = false)}
                    class="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                    Abbrechen
                </button>
                <button
                    on:click={confirmDuplicate}
                    class="text-white px-4 py-2 rounded hover:opacity-90 transition-opacity"
                    style="background-color: #2d4a7a;"
                >
                    Kopieren
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Modal -->
<Modal open={modellDialogOpen} on:close={closeModal}>
    <NewModelPage data={$page.state.newModell} />
</Modal>