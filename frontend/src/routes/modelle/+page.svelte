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

    async function deleteModell(modellId: number) {
        const confirmed = confirm("Möchtest du dieses Modell wirklich löschen?");
        if (!confirmed) return;

        try {
            const res = await fetch(`http://localhost:9999/modells/${modellId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!res.ok) throw new Error('Fehler beim Löschen des Modells');

            data.modelle = data.modelle.filter((c: any) => c.id !== modellId);
        } catch (err) {
            console.error(err);
            console.log('Fehler im Catch-Block:', err); // <-- was steht hier?

            alert('Löschen fehlgeschlagen');
        }
    }
    let showDuplicateModal = false;
    let duplicateModelId: number | null = null;
    let duplicateName = "";

    function openDuplicateModal(id: number) {
        duplicateModelId = id;
        duplicateName = "";
        showDuplicateModal = true;
    }

    async function confirmDuplicate() {
        if (!duplicateModelId) return;

        const res = await fetch(`http://localhost:9999/modells/${duplicateModelId}/duplicate`, {
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
    function goToModell(id: number, prozess: number) {
        console.log("einzigartig",prozess);
        if (prozess === 3) goto(`http://localhost:5173/modelle/3D-${id}`)
        else goto(`http://localhost:5173/modelle/${id}`)
    }
</script>



<style>
    tbody tr:nth-child(odd) {
        background-color: rgba(200, 200, 200, 0.3);
    }
</style>

<div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Page Header -->
    <div class="flex items-center gap-4 text-2xl font-semibold text-gray-600 mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
            <path fill-rule="evenodd" d="M12 6.75a5.25 5.25 0 0 1 6.775-5.025.75.75 0 0 1 .313 1.248l-3.32 3.319c.063.475.276.934.641 1.299.365.365.824.578 1.3.64l3.318-3.319a.75.75 0 0 1 1.248.313 5.25 5.25 0 0 1-5.472 6.756c-1.018-.086-1.87.1-2.309.634L7.344 21.3A3.298 3.298 0 1 1 2.7 16.657l8.684-7.151c.533-.44.72-1.291.634-2.309A5.342 5.342 0 0 1 12 6.75ZM4.117 19.125a.75.75 0 0 1 .75-.75h.008a.75.75 0 0 1 .75.75v.008a.75.75 0 0 1-.75.75h-.008a.75.75 0 0 1-.75-.75v-.008Z" clip-rule="evenodd" />
            <path d="m10.076 8.64-2.201-2.2V4.874a.75.75 0 0 0-.364-.643l-3.75-2.25a.75.75 0 0 0-.916.113l-.75.75a.75.75 0 0 0-.113.916l2.25 3.75a.75.75 0 0 0 .643.364h1.564l2.062 2.062 1.575-1.297Z" />
            <path fill-rule="evenodd" d="m12.556 17.329 4.183 4.182a3.375 3.375 0 0 0 4.773-4.773l-3.306-3.305a6.803 6.803 0 0 1-1.53.043c-.394-.034-.682-.006-.867.042a.589.589 0 0 0-.167.063l-3.086 3.748Zm3.414-1.36a.75.75 0 0 1 1.06 0l1.875 1.876a.75.75 0 1 1-1.06 1.06L15.97 17.03a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
        </svg>
        <span>Modelle</span>
    </div>

    <!-- Filter Row -->
    <div class="grid grid-cols-5 gap-2 mb-4">
        <input class="border rounded px-2 py-1" placeholder="Prozess" />
        <input class="border rounded px-2 py-1" placeholder="Aufgabe" />
        <input class="border rounded px-2 py-1" placeholder="Methode" />
        <input class="border rounded px-2 py-1" placeholder="Messeinrichtung" />
        <input class="border rounded px-2 py-1" placeholder="Messobjekt" />
    </div>

    <!-- Table Header -->
    <div class="bg-gray-200 border border-gray-300 rounded-t-md flex items-center font-semibold px-4 py-2">
        <div class="w-1/2">Modell</div>
        <div class="w-1/2 flex justify-between items-center">
            <span>Beschreibung</span>
            <a href="/modelle/add" on:click={onNewModellClick} title="Neues Modell hinzufügen">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-green-600 hover:scale-110 transition-transform">
                    <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clip-rule="evenodd" />
                </svg>
            </a>
        </div>
    </div>

    <!-- Table Body -->
    <div class="border border-t-0 border-gray-300 divide-y divide-gray-200">
        {#each data.modelle as modell}
            <div class="flex px-4 py-1 hover:bg-gray-100 cursor-pointer" on:dblclick={() => goToModell(modell.id,modell.aufgabe_modell)}>
                <div class="w-1/2">{modell.name}</div>
                <div class="w-1/2 flex justify-between items-center">
                    <span>{modell.description}</span>
                    <div class="flex gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" on:click={() => openDuplicateModal(modell.id)} fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-gray-500 hover:text-blue-500 cursor-pointer">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.5 8.25V6a2.25 2.25 0 0 0-2.25-2.25H6A2.25 2.25 0 0 0 3.75 6v8.25A2.25 2.25 0 0 0 6 16.5h2.25m8.25-8.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-7.5A2.25 2.25 0 0 1 8.25 18v-1.5m8.25-8.25h-6a2.25 2.25 0 0 0-2.25 2.25v6" />
                        </svg>
                        <svg xmlns="http://www.w3.org/2000/svg" on:click={() => deleteModell(modell.id)} fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-red-500 hover:text-red-700 cursor-pointer">
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
            <h2 class="text-xl font-semibold mb-4">Modell duplizieren</h2>

            <label class="block text-sm font-medium text-gray-700 mb-1">Neuer Modellname</label>
            <input
                    type="text"
                    bind:value={duplicateName}
                    class="w-full border border-gray-300 rounded px-3 py-2 mb-4 focus:outline-none focus:ring focus:border-blue-500"
                    placeholder="z. B. Mein Modell (Kopie)"
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
