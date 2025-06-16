<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from "$app/stores";
    import Modal from "$lib/components/Modal.svelte";
    import NewModelPage from "./component-[anakompId]/+page.svelte";
    import NewConstPage from "./constant-[anakonstId]/+page.svelte";

    export let data;
    let analyseprojekt = data.analyseprojekt;
    $: analyseprojektId = $page.params.analyseprojektId;

    let name = analyseprojekt.name ?? "";
    let aenderungszustand = analyseprojekt.aenderungszustand ?? "";
    let identnr = analyseprojekt.identnr ?? null;
    let remark = analyseprojekt.remark ?? "";

    $: showConstModal = !!$page.state?.selectedConstant;
    $: modellDialogOpen = !!$page.state?.updateComp;

    async function onUpdateCompClick(compId: number) {
        const href = `/analyseprojekt/${analyseprojektId}/component-${compId}`;
        const result = await preloadData(href);
        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { updateComp: result.data });
        } else {
            goto(href);
        }
    }

    function getVerteilungText(value: any) {
        switch(value) {
            case 1: return 'Rechteckverteilung';
            case 2: return 'Normalverteilung';
            case 3: return 'Dreieckverteilung';
            case null:
            case undefined:
            case '':
                return '';
            default:
                return String(value);
        }
    }

    function getWertartText(value: any) {
        switch(value) {
            case 1: return 'Halbweite';
            case 2: return 'Spannweite';
            case 3: return 'Standardabweichung';
            case null:
            case undefined:
            case '':
                return '';
            default:
                return String(value);
        }
    }

    function getFreigradText(value: any) {
        switch(value) {
            case 1: return 'Unbegrenzt';
            case 2: return 'N-1';
            case null:
            case undefined:
            case '':
                return '';
            default:
                return String(value);
        }
    }


    async function onConstClick(id: number) {
        const href = `/analyseprojekt/${analyseprojektId}/constant-${id}`;
        const result = await preloadData(href);
        if (result.type === "loaded" && result.status === 200) {
            pushState(href, { selectedConstant: result.data });
        } else {
            goto(href);
        }
    }

    function closeModal() {
        history.back();
    }

    type EditFields = {
        terml0?: boolean;
        terml1?: boolean;
        verteilung?: boolean;
        freigrad?: boolean;
        wertart?: boolean;
        frei_n_1?: boolean;
        remark?: boolean;
    };

    type FieldName = keyof EditFields;


    const editableFields: FieldName[] = ['terml0', 'terml1', 'verteilung', 'freigrad', 'wertart', 'frei_n_1', 'remark'];
    let selectedRow: number | null = null;

</script>

<section class="space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" action="?/speichern">
    <h1 class="text-lg font-semibold border-b pb-1">Analyseprojekt
        <button type="submit" name="berechnen" formaction="?/berechnen" class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
            Berechnen
        </button>
        <button type="submit" name="speichern" class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
            Speichern
        </button>
    </h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 border p-4 rounded bg-gray-100">
        <div>
            <label class="block text-gray-700">Name</label>
            <input type="text" name="name" bind:value={name} class="w-full border border-gray-400 px-2 py-1 bg-white" />
        </div>
        <div>
            <label class="block text-gray-700">Änderungszustand</label>
            <input type="text" name="aenderungszustand" bind:value={aenderungszustand} class="w-full border border-gray-400 px-2 py-1 bg-white" />
        </div>
        <div>
            <label class="block text-gray-700">Identnummer</label>
            <input type="number" name="identnr" bind:value={identnr} class="w-full border border-gray-400 px-2 py-1 bg-white" />
        </div>
        <div class="md:col-span-3">
            <label class="block text-gray-700">Bemerkung</label>
            <input type="text" name="remark" bind:value={remark} class="w-full border border-gray-400 px-2 py-1 bg-white" />
        </div>

    </div>
    </form>
    <div class="border border-gray-300 rounded overflow-hidden bg-gray-200">
        <div class="flex items-center gap-2 px-2 py-1 bg-gray-100 border-b">
            Komponenten

        </div>
            <table class="w-full text-sm border-t">
            <thead class="bg-gray-200 text-gray-700">
            <tr>
                <th class="px-2 text-left"></th>
                <th class="px-2 py-1 text-left">ID</th>
                <th class="px-2 py-1 text-left">L0 längenunabhängiger Term</th>
                <th class="px-2 py-1 text-left">L1 längenunabhängiger Term</th>
                <th class="px-2 py-1 text-left">Verteilung</th>
                <th class="px-2 py-1 text-left">Streuungsparameter</th>
                <th class="px-2 py-1 text-left">Freiheitsgrad</th>
            </tr>
            </thead>
            <tbody>
            {#each analyseprojekt.anakomp as comp, i}
                <tr class="{selectedRow === i ? 'bg-green-200' : 'hover:bg-gray-100'} cursor-pointer"
                    on:click={() => selectedRow = i}
                    on:dblclick={() => onUpdateCompClick(comp.id)}>
                    <td class="px-2">{i + 1}</td>
                    <td class="px-2 py-1">{comp.id}</td>
                    <td class="px-2 py-1">{comp.terml0}</td>
                    <td class="px-2 py-1">{comp.terml1}</td>
                    <td class="px-2 py-1">{getVerteilungText(comp.verteilung)}</td>
                    <td class="px-2 py-1">{getWertartText(comp.wertart)}</td>
                    <td class="px-2 py-1">{getFreigradText(comp.freigrad)}</td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>

    {#if analyseprojekt.anakonst?.length > 0}
        <h2 class="text-base font-semibold">Konstanten</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 lg:grid-cols-4 lg:grid-cols-5 gap-3">
            {#each analyseprojekt.anakonst as konst}
                <div
                        class="bg-white border border-gray-300 rounded px-3 py-1 cursor-pointer hover:shadow"
                        on:dblclick={() => onConstClick(konst.id)}>
                    <p><strong>Konstante #{konst.id}</strong></p>
                    <p>Wert: {konst.constval}</p>
                </div>
            {/each}
        </div>
    {/if}


</section>

<Modal open={modellDialogOpen} on:close={closeModal}>
    <NewModelPage data={$page.state.updateComp} />
</Modal>

<Modal open={showConstModal} on:close={closeModal}>
    <NewConstPage data={$page.state.selectedConstant} />
</Modal>
