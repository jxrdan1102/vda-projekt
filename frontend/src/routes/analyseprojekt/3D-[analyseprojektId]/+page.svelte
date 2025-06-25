<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from "$app/stores";
    import Modal from "$lib/components/Modal.svelte";
    import NewModelPage from "./component-[anakompId]/+page.svelte";
    import NewConstPage from "./constant-[anakonstId]/+page.svelte";
    import KmgInfoPage from "./kmg/+page.svelte";
    import {COMPONENTS, tcMapping} from "$lib/Mapping";


    export let data;
    let analyseprojekt = data.analyseprojekt;
    $: analyseprojektId = $page.params.analyseprojektId;

    let name = analyseprojekt.name ?? "";
    let aenderungszustand = analyseprojekt.aenderungszustand ?? "";
    let identnr = analyseprojekt.identnr ?? null;
    let remark = analyseprojekt.remark ?? "";

    $: showConstModal = !!$page.state?.selectedConstant;
    $: modellDialogOpen = !!$page.state?.updateComp;
    $: showKmg = !!$page.state?.kmgInfo;


    async function onUpdateCompClick(compId: number) {
        const href = `/analyseprojekt/3D-${analyseprojektId}/component-${compId}`;
        const result = await preloadData(href);
        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { updateComp: result.data });
        } else {
            goto(href);
        }
    }

    async function openKmg() {
        const href = `/analyseprojekt/3D-${analyseprojektId}/kmg`;
        const result = await preloadData(href);
        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { kmgInfo: result.data });
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
            case 4: return 'A';
            case 5: return 'B';
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
        const href = `/analyseprojekt/3D-${analyseprojektId}/constant-${id}`;
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



    let selectedRow: number | null = null;
    const methodenMap: Record<number, string> = {
        1: "Direkt",
        2: "Direkt mit Einstellung",
        3: "Substitution",
        4: "Differenziell"
    };

    const geoMap: Record<number, string> = {
        1: "Fläche",
        2: "Kugel",
        3: "Zylinder",
        4: "Bohrung"
    };
    const aufgabenMap: Record<string, string> = {
        tsk_ausenmessung: "Außenmessung",
        tsk_innenmessung: "Innenmessung",
        tsk_tiefenmessung: "Tiefenmessung",
        tsk_hoehenmessung: "Höhenmessung",
        tsk_stufenmessung: "Stufenmessung"
    };
    function getAktiveAufgabe(modell: Record<string, number>): string {
        for (const key in aufgabenMap) {
            if (Number(modell[key]) === 1) return aufgabenMap[key as keyof typeof aufgabenMap];
        }
        return "Unbekannt";
    }
</script>

<section class="space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" action="?/speichern">
        <h1 class="text-base font-semibold border-b pb-2">Analyseprojekt
            <button type="button" name="berechnen" on:click={() => goto(`/analyseprojekt/3D-${analyseprojektId}/MU`) } class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
                Berechnen
            </button>
            <button type="submit" name="speichern" class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
                Speichern
            </button>
            <button type="button" on:click={openKmg} name="kmg" class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
                KMG
            </button>
        </h1>
        <div class="flex gap-10 justify-between mt-3">

        <div class="grid grid-cols-3 gap-3 border p-4 rounded bg-gray-100 w-2xl">
            <div>
                <label class="block text-gray-700 text-xs mb-1">Name</label>
                <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
            </div>
            <div>
                <label class="block text-gray-700 text-xs mb-1">Änderungszustand</label>
                <input type="text" name="aenderungszustand" bind:value={aenderungszustand} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
            </div>
            <div>
                <label class="block text-gray-700 text-xs mb-1">Identnummer</label>
                <input type="number" name="identnr" bind:value={identnr} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
            </div>
            <div>
                <label class="block text-gray-700 text-xs mb-1">Sachnummer</label>
                <input type="text" name="sachnummer" value="Sachnummer" class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
            </div>
            <div>
                <label class="block text-gray-700 text-xs mb-1">Bemerkung</label>
                <input type="text" name="remark" bind:value={remark} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
            </div>
            <div class="flex ml-6 items-center space-x-2 mb-1">
                <label for="eignungswert" class="text-gray-700 text-xs object-bottom">Eignungskennwert</label>
                <input type="checkbox" name="eignungswert" id="eignungswert" class="h-4 w-4 text-gray-600 border-gray-400 rounded" />
            </div>


        </div>
            <!-- Modellinformationen -->
            <div class="border p-4 rounded bg-gray-50 w-full md:w-1/2 space-y-2">
                <h2 class="text-sm font-semibold border-b pb-1 text-gray-800"> {data.analyseprojekt.modell.name}</h2>
                <div class="text-gray-800 text-sm space-y-1">
                    <div><span class="font-semibold">Aufgabe:</span> {getAktiveAufgabe(data.analyseprojekt.modell)}</div>
                    <div><span class="font-semibold">Methode:</span> {methodenMap[data.analyseprojekt.modell.methode]}</div>
                    <div><span class="font-semibold">Messobjekt:</span> {geoMap[data.analyseprojekt.modell.geo_mo]}</div>
                    <div><span class="font-semibold">Messeinrichtung:</span> {geoMap[data.analyseprojekt.modell.geo_me]}</div>
                </div>
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
                <th class="px-2 py-1 text-left">Komponente</th>
                <th class="px-2 py-1 text-left">Standardabweichung</th>
                <th class="px-2 py-1 text-left">Methode</th>
                <th class="px-2 py-1 text-left">Anzahl Messpunkte</th>
                <th class="px-2 py-1 text-left">Anzahl Messungen</th>
            </tr>
            </thead>
            <tbody>
            {#each analyseprojekt.anakomp as comp, i}
                <tr class="{selectedRow === i ? 'bg-green-200' : 'hover:bg-gray-100'} cursor-pointer"
                    on:click={() => selectedRow = i}
                    on:dblclick={() => onUpdateCompClick(comp.id)}>
                    <td class="px-2">{i + 1}</td>
                    <td class="px-2 py-1">{COMPONENTS[comp.komponente.kompid]}</td>
                    <td class="px-2 py-1">{comp.terml0}</td>
                    <td class="px-2 py-1">{getWertartText(comp.wertart)}</td>
                    <td class="px-2 py-1">{comp.messpunkt_anzahl}</td>
                    <td class="px-2 py-1">{comp.anzahl_messungen}</td>
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
                    <p><strong>{tcMapping[konst.constnum]}</strong></p>
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

<Modal open={showKmg} on:close={closeModal}>
    <KmgInfoPage data={$page.state.kmgInfo} />
</Modal>
