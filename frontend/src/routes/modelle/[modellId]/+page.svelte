<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from '$app/stores';
    import Modal from "$lib/components/Modal.svelte";
    import NewCompPage from "../[modellId]/addComponent/+page.svelte";
    import CompInfoPage from '../[modellId]/component-[componentId]/+page.svelte';
    import {COMPONENTS, Components} from "$lib/Mapping.js";

    export let data;

    // Lokale reactive Variablen
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
    let aufgabe_modell: number = data.modell?.aufgabe_modell ?? 0;

    let description: string = data.modell?.description ?? '';
    let formeldesc: string = data.modell?.formeldesc ?? '';

    let formel = data.modell.formel ?? '';
    let modellId = data.modellId;
    let message = '';
    let error = '';
    export let form: {
        success?: boolean;
        message?: string;
        error?: string;
    } | null = null;
    $: modellId = $page.params.modellId;
    $: componentDialogOpen = !!$page.state?.newComponent;
    $: showComponent = !!$page.state?.componentInfo;

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
    function closeModal() {
        history.back(); // entfernt state und schließt modal
    }
    let selectedRow: number | null = null;

    $: prozesstitel = (() => {
        switch (data.modell.aufgabe_modell) {
            case 1:
                return 'Prüfprozess';
            case 2:
                return 'Kalibrierprozess';
            case 3:
                return '3D-Prüfprozess';
            default:
                return 'Fehler';
        }
    })();


    async function deleteComponent(compId: number) {
        const confirmed = confirm("Möchtest du diese Komponente wirklich löschen?");
        if (!confirmed) return;

        try {
            const res = await fetch(`http://localhost:9999/components/${compId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            if (!res.ok) throw new Error('Fehler beim Löschen der Komponente');

            data.modell.components = data.modell.components.filter((c: any) => c.id !== compId);
        } catch (err) {
            console.error(err);
            alert('Löschen fehlgeschlagen');
        }
    }

    const ModelTextLabels: Record<number, string> = {
        0: '',
        1: 'Das ist eine tolle Komponente',
        2: 'Diese Komponente ist sehr nützlich',
    };
</script>
<section class="w-8xl space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" class="max-w-8xl space-y-6">
    <!-- Titel -->
        <input type="number" name="aufgabe_modell" hidden bind:value={data.modell.aufgabe_modell} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />

    <h1 class="text-base font-semibold border-b pb-2">{prozesstitel}
        <button type="submit" name="action" value="continue" class="ml-2 bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
            Speichern & Schließen
        </button>
        <button type="submit" name="action" value="close" class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
            Speichern & Weiter
        </button>
    </h1>

    <!-- Formulareingabe oben -->
    <div class="flex gap-20 border rounded p-3 bg-gray-100">
        <div class="mr-5">
        <div class="mb-3">
            <label class="block text-gray-700 text-xs mb-1">Modell</label>
            <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
        </div>
        <div>
            <label class="block text-gray-700 text-xs mb-1">Aufgabe</label>
            <div class="flex flex-col gap-1 px-1">
                <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_ausenmessung" class="h-4 w-4 text-gray-600 border-gray-400 rounded" bind:checked={tsk_ausenmessung}/> Außenmessung</label>
                <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_innenmessung" class="h-4 w-4 text-gray-600 border-gray-400 rounded" bind:checked={tsk_innenmessung}/> Innenmessung</label>
                <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_tiefenmessung" class="h-4 w-4 text-gray-600 border-gray-400 rounded" bind:checked={tsk_tiefenmessung}/> Tiefenmessung</label>
                <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_hoehenmessung" class="h-4 w-4 text-gray-600 border-gray-400 rounded" bind:checked={tsk_hoehenmessung}/> Höhenmessung</label>
                <label class="text-gray-700 text-xs object-bottom"><input type="checkbox" name="tsk_stufenmessung" class="h-4 w-4 text-gray-600 border-gray-400 rounded" bind:checked={tsk_stufenmessung}/> Stufenmessung</label>
            </div>
        </div>
        </div>
        <div class="">
        <div class="mx-20 mb-3">
            <label class="block text-gray-700 text-xs mb-1">Methode</label>
            <select id="methode" name="methode" bind:value={methode}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
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
                    <select id="geo_me" name="geo_me" bind:value={geo_me}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                        <option value="" disabled>Bitte wählen</option>
                        <option value="1">Fläche</option>
                        <option value="2">Kugel</option>
                        <option value="3">Zylinder</option>
                        <option value="4">Bohrung</option>
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 text-xs mb-1">Messobjekt</label>
                    <select id="geo_mo" name="geo_mo" bind:value={geo_mo}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                        <option value="" disabled>Bitte wählen</option>
                        <option value="1">Fläche</option>
                        <option value="2">Kugel</option>
                        <option value="3">Zylinder</option>
                        <option value="4">Bohrung</option>
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 text-xs mb-1">Einstellnormal</label>
                    <select id="geo_bn" name="geo_bn" bind:value={geo_bn}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                        <option value="" disabled >Bitte wählen</option>
                        <option value="1">Fläche</option>
                        <option value="2">Kugel</option>
                        <option value="3">Zylinder</option>
                        <option value="4">Bohrung</option>
                    </select>
                </div>
            </div>
        </fieldset>
        </div>
        <div class="border-l p-3 pl-20 w-xl">
            <div class="mb-1">
                <label class="block text-gray-700 text-xs mb-1">Beschreibung – Modell</label>
                <textarea bind:value={description} name="beschreibung" class="w-full h-10 border border-gray-400 px-2 text-sm py-0 bg-white" rows="2"></textarea>
            </div>
            <div class="mb-1">
                <label class="block text-gray-700 text-xs mb-1">Formel</label>
                <input type="text" bind:value={formel} name="formel" class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white" />
            </div>
            <div class="mb-1">
                <label class="block text-gray-700 text-xs mb-1">Beschreibung – Formel</label>
                <input type="text" bind:value={formeldesc} name="formeldesc" class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white" />
            </div>
        </div>
    </div>

    <!-- Komponentenliste -->
    <div class="border border-gray-300 rounded overflow-hidden bg-gray-200">
        <div class="flex items-center gap-2 p-2 bg-gray-100 border-b">

        </div>

        <!-- Tabelle -->
        <table class="w-full text-sm border-t">
            <thead class="bg-gray-200 text-gray-700">
            <tr>
                <th class="px-2 py-1 text-left w-1"></th>
                <th class="px-2 py-1 text-left">Komponente</th>
                <th class="px-2 py-1 text-left">Beschreibung</th>
                <th class="float-right p-1">
                    <svg on:click={onNewComponentClick} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-5.5 hover:text-gray-800 cursor-pointer">
                        <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clip-rule="evenodd" />
                    </svg>
                </th>
            </tr>
            </thead>
            <tbody>
            {#each data.modell.components as comp, i}
                <tr class="{selectedRow === i ? 'bg-cyan-800' : 'hover:bg-cyan-900'} {selectedRow === i ? 'text-white' : 'hover:text-white'} cursor-pointer"
                    on:click={() => selectedRow = i}
                    on:dblclick={(e) => onOpenComponent(e, comp.id)}>
                    <td class="px-2 py-1 text-left w-0.5">{i + 1}</td>
                    <td class="px-2 py-1">{Components[comp.kompid] ? Components[comp.kompid] : COMPONENTS[comp.kompid]}</td>
                    <td class="px-2 py-1">{ModelTextLabels[comp.modltxtid] ?? ''}</td>
                    <td class="float-right px-1">
                        <button type="button" on:click={() => deleteComponent(comp.id)}>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-red-500 hover:text-red-700 cursor-pointer">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                            </svg>
                        </button>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>

    </form>
</section>

<Modal open={componentDialogOpen} on:close={closeModal} >
    <div class="max-h-[80vh] overflow-y-auto p-4">
        <NewCompPage data={$page.state.newComponent} />
    </div>
</Modal>

<Modal open={showComponent} on:close={closeModal} >
    <div class="max-h-[80vh] overflow-y-auto p-4">
        <CompInfoPage data={$page.state.componentInfo} />
    </div>
</Modal>