<script lang="ts">
    import NewModelPage from './add/+page.svelte';
    import {page} from '$app/stores';
    import {goto, preloadData, pushState} from '$app/navigation';
    import Modal from "$lib/components/Modal.svelte";

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
        history.back(); // entfernt state und schließt modal
    }

    async function deleteProjekt(projektId: number) {
        const confirmed = confirm("Möchtest du dieses Modell wirklich löschen?");
        if (!confirmed) return;

        try {
            const res = await fetch(`http://localhost:9999/anamu/${projektId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!res.ok) throw new Error('Fehler beim Löschen des Modells');

            data.analyseprojekt = data.analyseprojekt.filter((c: any) => c.id !== projektId);
        } catch (err) {
            console.error(err);
            console.log('Fehler im Catch-Block:', err); // <-- was steht hier?

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

        const res = await fetch(`http://localhost:9999/anamu/${duplicateProjektId}/duplicate`, {
            method: "POST",
            credentials: 'include',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name: duplicateName}),
        });

        if (res.ok) {
            const result = await res.json();
            console.log("Duplikat erstellt:", result);
            // Optional: Liste aktualisieren
            showDuplicateModal = false;
        } else {
            alert("Fehler beim Duplizieren");
        }
    }

    function goToProjekt (id: number, prozess: number) {
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

</script>

<div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Page Header -->
    <div class="flex items-center gap-4 text-2xl font-semibold text-gray-600 mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
            <path d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
        </svg>

        <span>Analyseprojekte</span>
    </div>

    <!-- Filter Row -->
    <div class="grid grid-cols-5 gap-2 mb-4">
        <input class="border rounded px-2 py-1" placeholder="Projekt" />
        <input class="border rounded px-2 py-1" placeholder="Änderungsstand" />
        <input class="border rounded px-2 py-1" placeholder="Modell" />
        <input class="border rounded px-2 py-1" placeholder="Identnummer" />
        <input class="border rounded px-2 py-1" placeholder="Datum" />
    </div>

    <!-- Table Header -->
    <div class="bg-gray-200 border border-gray-300 rounded-t-md flex items-center font-semibold px-4 py-2">
        <div class="w-1/2">Analyseprojekt</div>
        <div class="w-1/2">Änderungsstand</div>
        <div class="w-1/2">Identnummer</div>
        <div class="w-1/2 flex justify-between items-center">
            <span>Datum</span>
            <button on:click={() => {loadModels(); showForm = !showForm;}} title="Neues Modell hinzufügen" class="focus:outline-none" aria-label="Neues Modell hinzufügen">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-green-600 hover:scale-110 transition-transform">
                    <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    </div>

    {#if showForm}
        <!-- Eingabeformular -->
        <form method="POST" class="bg-gray-100 border border-t-0 border-gray-300 px-4 py-3 flex flex-wrap items-center gap-4">
            <input id="name" name="name" required placeholder="Name" class="border border-gray-300 rounded px-2 py-1 w-48 text-sm"/>

            <input id="aenderungszustand" name="aenderungszustand" placeholder="Änderungsstand" class="border border-gray-300 rounded px-2 py-1 w-48 text-sm" />

            <select id="modell" name="modell" required
                    class="border border-gray-300 rounded px-2 py-1 w-48 text-sm"
                    on:change={handleSelectChange}>
                <option value="" disabled selected>Modell wählen</option>
                {#each models as modell}
                    <option value={modell.id}>{modell.name} (ID: {modell.id})</option>
                {/each}
            </select>

            <input id="aufgabe_modell"
                   hidden
                   name="aufgabe_modell"
                   bind:value={aufgabe_modell_value}
            />
            <button type="submit" class="bg-green-100 text-green-800 hover:bg-green-200 border border-green-300 rounded px-3 py-1 text-sm font-medium transition-colors">
                Erstellen
            </button>
        </form>
    {/if}

    <!-- Table Body -->
    <div class="border border-t-0 border-gray-300 divide-y divide-gray-200">
        {#each data.analyseprojekt as analyseprojekt}
            <div class="flex px-4 py-1 hover:bg-gray-100 cursor-pointer" on:dblclick={() => goToProjekt(analyseprojekt.id, analyseprojekt.modell.aufgabe_modell)}>
                <div class="w-1/2">{analyseprojekt.name}</div>
                <div class="w-1/2">{analyseprojekt.aenderungszustand}</div>
                <div class="w-1/2">{analyseprojekt.identnr}</div>
                <div class="w-1/2 flex justify-between items-center">
                    <span>{analyseprojekt.creation}</span>
                    <div class="flex gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" on:click={() => openDuplicateModal(analyseprojekt.id)} fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-gray-500 hover:text-blue-500 cursor-pointer">
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
    <div class="fixed inset-0 flex items-center justify-center z-50">
        <div class="bg-white rounded-xl p-6 shadow-xl w-full max-w-md">
            <h2 class="text-xl font-semibold mb-4">Analyseprojekt duplizieren</h2>

            <label class="block text-sm font-medium text-gray-700 mb-1">Neuer Projektname</label>
            <input
                    type="text"
                    bind:value={duplicateName}
                    class="w-full border border-gray-300 rounded px-3 py-2 mb-4 focus:outline-none focus:ring focus:border-blue-500"
                    placeholder="z. B. Mein Projekt (Kopie)"
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
                        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
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
