<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from '$app/stores';
    import Modal from "$lib/components/Modal.svelte";
    import NewCompPage from "../3D-[modellId]/addComponent/+page.svelte";
    import CompInfoPage from '../3D-[modellId]/component-[componentId]/+page.svelte';
    import {COMPONENTS} from "$lib/Mapping.js";

    export let data;
    const ModelTextLabels: Record<number, string> = {
        0: '',
        1: 'Das ist eine tolle Komponente',
        2: 'Diese Komponente ist sehr nützlich',
    };
    // Lokale reactive Variablen
    let name: string = data.modell?.name ?? '';
    let Bezug1: string | null = data.modell?.Bezug1 ?? null;
    let Bezug2: string | null = data.modell?.Bezug2 ?? null;
    let Element1: string | null = data.modell?.Element1 ?? null;
    let Element2: string | null = data.modell?.Element2 ?? null;
    let punktmuster: string | null = data.modell?.punktmuster != null ? data.modell.punktmuster.toString() : null;
    let aufgabe: number = data.modell?.aufgabe ?? 0;
    let taster: number = data.modell?.taster ?? 0;
    let merkmal: number = data.modell?.merkmal ?? null;
    let element: number = data.modell?.element ?? null;
    let punktmusterB1: number = data.modell?.punktmusterB1 ?? null;
    let tasterschaft1: number = data.modell?.tasterschaft1 ?? null;
    let tasterschaft2: number = data.modell?.tasterschaft2 ?? null;
    let punktmusterR1: number = data.modell?.punktmusterR1 ?? null;
    let punktmusterR2: number = data.modell?.punktmusterR2 ?? null;
    let taster1: number = data.modell?.taster1 ?? null;
    let taster2: number = data.modell?.taster2 ?? null;
    let abstand: number = data.modell?.abstand ?? null;
    let winkelE1: number = data.modell?.winkelE1 ?? null;
    let winkelE2: number = data.modell?.winkelE2 ?? null;

    let description: string = data.modell?.description ?? '';
    let formeldesc: string = data.modell?.formeldesc ?? '';

    let formel = data.modell.formel ?? '';
    let modellId = data.modellId;

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

        const href = `/modelle/3D-${modellId}/addComponent`;
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

        const href = `/modelle/3D-${modellId}/component-${compId}`;
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
</script>
<section class="w-8xl space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" class="max-w-8xl space-y-6">
    <!-- Titel -->

    <h1 class="text-base font-semibold border-b pb-2">{prozesstitel} {data.modell.aufgabe}
        <button type="submit" class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
            Speichern
        </button>
    </h1>

    <!-- Formulareingabe oben -->
    <div class="flex gap-20 border rounded p-3 bg-gray-100">
        <div class="mr-5">
            {#if aufgabe === 7}
                <div class="mb-3 w-lg pl-5">
                    <label class="block text-gray-700 text-xs mb-1">Modell</label>
                    <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster</label>
                        <select id="taster" name="taster" bind:value={taster}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="1">derselbe Taster</option>
                            <option value="2">verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 2</label>
                        <select id="Element2" name="Element2" bind:value={Element2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                </div>
            {/if}
            {#if aufgabe === 6}
                <div class="mb-3 w-lg pl-5">
                    <label class="block text-gray-700 text-xs mb-1">Modell</label>
                    <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug 1</label>
                        <select id="Bezug1" name="Bezug1" bind:value={Bezug1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Punktmuster</label>
                        <select id="punktmuster" name="punktmuster" bind:value={punktmuster}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="1">gleichmäßig verteilt</option>
                            <option value="2">zwei Radialschnitte</option>
                            <option value="3">kreisförmig</option>
                        </select>
                    </div>
                </div>
            {/if}
            {#if aufgabe === 5}
                <div class="mb-3 w-lg pl-5">
                    <label class="block text-gray-700 text-xs mb-1">Modell</label>
                    <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element</label>
                        <select id="element" name="element" bind:value={element}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>Gerade</option>
                            <option value=2>Ebene</option>
                            <option value=3>Kreis</option>
                            <option value=4>Halbkugel</option>
                            <option value=5>Zylinder</option>
                            <option value=6>Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Merkmal</label>
                        <select id="merkmal" name="merkmal" bind:value={merkmal}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>Geradheit</option>
                            <option value=2>Ebenheit</option>
                            <option value=3>Rundheit</option>
                            <option value=4>Flächenform</option>
                            <option value=5>Zylinderform</option>
                        </select>
                    </div>
                </div>
            {/if}
            {#if aufgabe === 4}
                <div class="mb-3 w-lg pl-5 grid grid-cols-3 gap-2">
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Modell</label>
                        <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster</label>
                        <select id="taster" name="taster" bind:value={taster}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>derselbe Taster</option>
                            <option value=2>verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element</label>
                        <select id="element" name="element" bind:value={element}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>Gerade</option>
                            <option value=2>Ebene</option>
                            <option value=3>Kreis</option>
                            <option value=4>Halbkugel</option>
                            <option value=5>Zylinder</option>
                            <option value=6>Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Punktmuster</label>
                        <select id="punktmuster" name="punktmuster" bind:value={punktmuster}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>gleichmäßig verteilt</option>
                            <option value=2>zwei Radialschnitte</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug1</label>
                        <select id="Bezug1" name="Bezug1" bind:value={Bezug1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>Kreis</option>
                            <option value=2>Zylinder</option>
                            <option value=3>Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Punktmuster 1</label>
                        <select id="punktmusterB2" name="punktmusterB1" bind:value={punktmusterB1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>gleichmäßig verteilt</option>
                            <option value=2>zwei Radialschnitte</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug2</label>
                        <select id="Bezug2" name="Bezug2" bind:value={Bezug2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=0>-</option>
                            <option value=1>Kreis</option>
                            <option value=2>Zylinder</option>
                            <option value=3>Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Tasterschaft 1</label>
                        <select id="tasterschaft1" name="tasterschaft1" bind:value={tasterschaft1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>senkrecht</option>
                            <option value=2>parallel zu Auswerterichtung</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Tasterschaft 2</label>
                        <select id="tasterschaft2" name="tasterschaft2" bind:value={tasterschaft2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>senkrecht</option>
                            <option value=2>parallel zu Auswerterichtung</option>
                        </select>
                    </div>
                </div>
            {/if}
            {#if aufgabe === 3}
                <div class="mb-3 w-lg pl-5 grid grid-cols-3 gap-2">
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Modell</label>
                        <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Merkmal</label>
                        <select id="merkmal" name="merkmal" bind:value={merkmal}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>Geradheit</option>
                            <option value=2>Ebenheit</option>
                            <option value=3>Rundheit</option>
                            <option value=4>Flächenform</option>
                            <option value=5>Zylinderform</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 2</label>
                        <select id="Element2" name="Element2" bind:value={Element2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Punktmuster</label>
                        <select id="punktmusterR2" name="punktmusterR2" bind:value={punktmusterR2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>gleichmäßig verteilt</option>
                            <option value=2>zwei Radialschnitte</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug1</label>
                        <select id="Bezug1" name="Bezug1" bind:value={Bezug1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>Kreis</option>
                            <option value=2>Zylinder</option>
                            <option value=3>Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Punktmuster</label>
                        <select id="punktmusterR2" name="punktmusterR1" bind:value={punktmusterR1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>gleichmäßig verteilt</option>
                            <option value=2>zwei Radialschnitte</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug2</label>
                        <select id="Bezug2" name="Bezug2" bind:value={Bezug2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=0>-</option>
                            <option value=1>Kreis</option>
                            <option value=2>Zylinder</option>
                            <option value=3>Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster 1</label>
                        <select id="taster" name="taster1" bind:value={taster1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>derselbe Taster</option>
                            <option value=2>verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster 2</label>
                        <select id="taster2" name="taster2" bind:value={taster2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=1>derselbe Taster</option>
                            <option value=2>verschiedene Taster</option>
                        </select>
                    </div>
                </div>
            {/if}
            {#if aufgabe === 2}
                <div class="mb-3 w-lg pl-5 grid grid-cols-3 gap-2">
                    <div>
                    <label class="block text-gray-700 text-xs mb-1">Modell</label>
                    <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 2</label>
                        <select id="Element2" name="Element2" bind:value={Element2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Abstand</label>
                        <select id="abstand" name="abstand" bind:value={abstand}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>in der Nullebene des Koordinatensystems</option>
                            <option value={2}>im Schwerpunkt</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster</label>
                        <select id="taster" name="taster" bind:value={taster}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>derselbe Taster</option>
                            <option value={2}>verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Winkel zu Element 1</label>
                        <select id="winkelE1" name="winkelE1" bind:value={winkelE1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>in Reihe oder im Raster</option>
                            <option value={2}>an den Enden Taster</option>
                            <option value={3}>kreisförmig</option>
                            <option value={4}>gleichmäßig verteilt</option>
                            <option value={5}>zwei Radialschnitte</option>

                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Winkel zu Element 2</label>
                        <select id="winkelE2" name="winkelE2" bind:value={winkelE2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>in Reihe oder im Raster</option>
                            <option value={2}>an den Enden Taster</option>
                            <option value={3}>kreisförmig</option>
                            <option value={4}>gleichmäßig verteilt</option>
                            <option value={5}>zwei Radialschnitte</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Tasterschaft 1</label>
                        <select id="tasterschaft1" name="tasterschaft1" bind:value={tasterschaft1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>senkrecht</option>
                            <option value={2}>parallel zu Auswerterichtung</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Tasterschaft 2</label>
                        <select id="tasterschaft2" name="tasterschaft2" bind:value={tasterschaft2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>senkrecht</option>
                            <option value={2}>parallel zu Auswerterichtung</option>
                        </select>
                    </div>
                </div>
            {/if}
            {#if aufgabe === 1}
                <div class="mb-3 w-lg pl-5">
                    <label class="block text-gray-700 text-xs mb-1">Modell</label>
                    <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value='Kreis'>Kreis</option>
                            <option value='Halbkugel'>Halbkugel</option>
                            <option value='Zylinder'>Zylinder</option>
                        </select>
                    </div>
                </div>
            {/if}
        </div>
        <div class="border-l p-3 pl-20 w-xl">
            <div class="mb-1">
                <label class="block text-gray-700 text-xs mb-1">Beschreibung – Modell</label>
                <textarea bind:value={description} name="description" class="w-full h-10 border border-gray-400 px-2 text-sm py-0 bg-white" rows="2"></textarea>
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
                <th class="px-2 py-1 text-left">#</th>
                <th class="px-2 py-1 text-left">Komponente</th>
                <th class="px-2 py-1 text-left">ID</th>
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
                <tr class="{selectedRow === i ? 'bg-green-300' : 'hover:bg-green-200'} cursor-pointer"
                    on:click={() => selectedRow = i}
                    on:dblclick={(e) => onOpenComponent(e, comp.id)}>
                    <td class="px-2 py-1">{i + 1}</td>
                    <td class="px-2 py-1">{COMPONENTS[comp.kompid]}</td>
                    <td class="px-2 py-1">{comp.id}</td>
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