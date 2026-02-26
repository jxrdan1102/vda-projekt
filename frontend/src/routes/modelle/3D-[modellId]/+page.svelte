<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from '$app/stores';
    import Modal from "$lib/components/Modal.svelte";
    import NewCompPage from "../3D-[modellId]/addComponent/+page.svelte";
    import CompInfoPage from '../3D-[modellId]/component-[componentId]/+page.svelte';
    import {COMPONENTS, Components} from "$lib/Mapping.js";

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
    let artdesmasses: number = data.modell?.artdesmasses ?? null;
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
    // Reaktiv: Optionen hängen von Element1 ab
    $: punktmusterOptionen = (() => {
        switch (Element1) {
            case "Gerade":
                return [
                    { value: 1, label: "in Reihe" },
                    { value: 2, label: "an den Enden" }
                ];
            case "Ebene":
                return [
                    { value: 1, label: "in Reihe oder im Raster" },
                    { value: 2, label: "an den Enden" },
                    { value: 3, label: "kreisförmig" }

                ];
            case "Zylinder":
            case "Kegel":
                return [
                    { value: 1, label: "gleichmäßig verteilt" },
                    { value: 2, label: "zwei Radialschnitte" }
                ];
            default:
                return [];
        }
    })();
    // Reaktiv: Optionen hängen von Element1 ab
    $: punktmuster2Optionen = (() => {
        switch (Bezug1) {
            case "Gerade":
                return [
                    { value: 1, label: "in Reihe" },
                    { value: 2, label: "an den Enden" }
                ];
            case "Ebene":
                return [
                    { value: 1, label: "in Reihe oder im Raster" },
                    { value: 2, label: "an den Enden" },
                    { value: 3, label: "kreisförmig" }

                ];
            case "Zylinder":
            case "Kegel":
                return [
                    { value: 1, label: "gleichmäßig verteilt" },
                    { value: 2, label: "zwei Radialschnitte" }
                ];
            default:
                return [];
        }
    })();
    // Sichtbarkeitslogik reaktiv berechnen
    $: showPunktmusterR1 = ["Gerade", "Ebene", "Zylinder", "Kegel"].includes(Element1);
    $: showElement2Taster1 = ["Kreis", "Punkt"].includes(Element1);

    $: showPunktmusterR2 = ["Gerade", "Ebene", "Zylinder", "Kegel"].includes(Bezug1);
    $: showBezug2Taster2 = ["Kreis", "Punkt"].includes(Bezug1);
    $: showTasterschaft1 = Element1 === "Halbkugel" || ((Element1 === "Punkt" || Element1 === "Gerade" || Element1 === "Ebene") && taster == 2);
    $: showTasterschaft2 = Element2 === "Halbkugel" || ((Element2 === "Punkt" || Element2 === "Gerade" || Element2 === "Ebene") && taster == 2);

    $: showArtDesMasses =
        (Element1 === "Punkt" || Element1 === "Gerade" || Element1 === "Ebene") &&
        (Element2 === "Punkt" || Element2 === "Gerade" || Element2 === "Ebene") && taster == 1;

    $: showWinkelE1 =
        (Element1 === "Gerade" || Element1 === "Ebene" || Element1 === "Zylinder" || Element1 === "Kegel") && abstand == 1;

    $: showWinkelE2 =
        (Element2 === "Gerade" || Element2 === "Ebene" || Element2 === "Zylinder" || Element2 === "Kegel") && abstand == 1;

    // Optionen für Element 1 dynamisch
    $: optionsWinkelE1 =
        (Element1 === "Gerade")
            ? [
                { value: 1, label: "in Reihe" },
                { value: 2, label: "an den Enden" },
            ]
            : (Element1 === "Zylinder" || Element1 === "Kegel")
                ? [
                    { value: 4, label: "gleichmäßig verteilt" },
                    { value: 5, label: "zwei Radialschnitte" },
                ]
                : (Element1 === "Ebene")
                    ? [
                        { value: 1, label: "in Reihe oder im Raster" },
                        { value: 2, label: "an den Enden" },
                        { value: 3, label: "kreisförmig" },

                    ]
                    : [];

    // Optionen für Element 2 dynamisch
    $: optionsWinkelE2 =
        (Element2 === "Gerade")
            ? [
                { value: 1, label: "in Reihe" },
                { value: 2, label: "an den Enden" },
            ]
            : (Element2 === "Zylinder" || Element2 === "Kegel")
                ? [
                    { value: 4, label: "gleichmäßig verteilt" },
                    { value: 5, label: "zwei Radialschnitte" },
                ]
                : (Element2 === "Ebene")
                    ? [
                            { value: 1, label: "in Reihe oder im Raster" },
                            { value: 2, label: "an den Enden" },
                            { value: 3, label: "kreisförmig" },

                        ]
                    : [];

    $: showPunktmuster = Element1 == "Zylinder";
    $: showPunktmuster1 = Bezug1 == "Zylinder";
    let aufgabe_modell = data.modell.aufgabe_modell
    async function saveModell() {
        const payload = {
            name,
            Element1,
            Element2,
            abstand,
            taster,
            aufgabe,
            aufgabe_modell,
            tasterschaft1,
            tasterschaft2,
            artdesmasses,
            winkelE1,
            winkelE2,
            Bezug1,
            Bezug2,
            punktmuster,
            description,
            formel,
            formeldesc,
            merkmal,
            element,
            punktmusterB1,
            punktmusterR1,
            punktmusterR2,
            taster1,
            taster2
        };
        console.log("OnChange funktioniert", payload);
        const res = await fetch(`http://localhost:9999/modells/${modellId}/alterModell`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        data.modell.components = await res.json()
        // wenn die Response JSON ist
        console.log('Response Body:', data);
        if (!res.ok) {
            console.error('Fehler beim Speichern', await res.text());
        } else {
            console.log('Modell gespeichert', payload);
        }
    }

</script>
<section class="w-8xl space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" class="max-w-8xl space-y-6">
    <!-- Titel -->
        <input type="number" name="aufgabe" bind:value={data.modell.aufgabe} hidden class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
        <input type="number" name="aufgabe_modell" hidden bind:value={data.modell.aufgabe_modell} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />

    <h1 class="text-base font-semibold border-b pb-2">{prozesstitel} {data.modell.aufgabe}
        <button type="submit" class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
            Speichern
        </button>
    </h1>
        {#if form?.success}
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded">
                {form.message}
            </div>
        {/if}

        {#if form?.error}
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded">
                {form.error}
            </div>
        {/if}

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
                            <option value={1}>derselbe Taster</option>
                            <option value={2}>verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Punkt">Punkt</option>
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
                            <option value="Punkt">Punkt</option>
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
                            <option value={2}>Gerade</option>
                            <option value={3}>Ebene</option>
                            <option value={4}>Kreis</option>
                            <option value={5}>Halbkugel</option>
                            <option value={6}>Zylinder</option>
                            <option value={7}>Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Merkmal</label>
                        <select id="merkmal" name="merkmal" bind:value={merkmal}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>Geradheit</option>
                            <option value={2}>Ebenheit</option>
                            <option value={3}>Rundheit</option>
                            <option value={4}>Zylinderform</option>
                            <option value={5}>Flächenform</option>
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
                            <option value={1}>derselbe Taster</option>
                            <option value={2}>verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Halbkugel">Halbkugel</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    {#if showPunktmuster}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Punktmuster</label>
                            <select id="punktmuster" name="punktmuster" bind:value={punktmuster}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value=1>gleichmäßig verteilt</option>
                                <option value=2>zwei Radialschnitte</option>
                            </select>
                        </div>
                    {/if}
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug1</label>
                        <select id="Bezug1" name="Bezug1" bind:value={Bezug1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    {#if showPunktmuster1}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Punktmuster 1</label>
                            <select id="punktmusterB1" name="punktmusterB1" bind:value={punktmusterB1}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>gleichmäßig verteilt</option>
                                <option value={2}>zwei Radialschnitte</option>
                            </select>
                        </div>
                    {/if}
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug2</label>
                        <select id="Bezug2" name="Bezug2" bind:value={Bezug2}  class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value=0>-</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
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
            {#if aufgabe === 3}
                <div class="mb-3 w-lg pl-5 grid grid-cols-3 gap-2">
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Modell</label>
                        <input type="text" name="name" bind:value={name} class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
                    </div>
                    <!-- Merkmal (immer sichtbar) -->
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Merkmal</label>
                        <select id="merkmal" name="merkmal" bind:value={merkmal}
                                class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>Parallelität</option>
                            <option value={2}>Rechtwinkligkeit</option>
                            <option value={3}>Neigung</option>
                        </select>
                    </div>

                    <!-- Element 1 (immer sichtbar) -->
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select bind:value={Element1} id="Element1" name="Element1" class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Punkt">Punkt</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>

                    <!-- Bezug 1 (immer sichtbar) -->
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug 1</label>
                        <select bind:value={Bezug1} id="Bezug1" name="Bezug1" class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Punkt">Punkt</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>

                    <!-- Bedingte Blöcke für Element 1 -->
                    {#if showPunktmusterR1}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Punktmuster R1</label>
                            <select bind:value={punktmusterR1} id="punktmusterR1" name="punktmusterR1"
                                    class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                {#each punktmusterOptionen as opt}
                                    <option value={opt.value}>{opt.label}</option>
                                {/each}
                            </select>
                        </div>
                    {/if}

                    {#if showElement2Taster1}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Element 2</label>
                            <select bind:value={Element2} id="Element2" name="Element2"
                                    class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value="Punkt">Punkt</option>
                                <option value="Gerade">Gerade</option>
                                <option value="Ebene">Ebene</option>
                                <option value="Kreis">Kreis</option>
                                <option value="Zylinder">Zylinder</option>
                                <option value="Kegel">Kegel</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Taster 1</label>
                            <select bind:value={taster1} id="taster1" name="taster1"
                                    class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>derselbe Taster</option>
                                <option value={2}>verschiedene Taster</option>
                            </select>
                        </div>
                    {/if}

                    <!-- Bedingte Blöcke für Bezug 1 -->
                    {#if showPunktmusterR2}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Punktmuster R2</label>
                            <select bind:value={punktmusterR2} id="punktmusterR2" name="punktmusterR2"
                                    class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                {#each punktmuster2Optionen as opt}
                                    <option value={opt.value}>{opt.label}</option>
                                {/each}
                            </select>
                        </div>
                    {/if}

                    {#if showBezug2Taster2}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Bezug 2</label>
                            <select bind:value={Bezug2} id="Bezug2" name="Bezug2"
                                    class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value="Punkt">Punkt</option>
                                <option value="Gerade">Gerade</option>
                                <option value="Ebene">Ebene</option>
                                <option value="Kreis">Kreis</option>
                                <option value="Zylinder">Zylinder</option>
                                <option value="Kegel">Kegel</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Taster 2</label>
                            <select bind:value={taster2} id="taster2" name="taster2"
                                    class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>derselbe Taster</option>
                                <option value={2}>verschiedene Taster</option>
                            </select>
                        </div>
                    {/if}
                </div>
            {/if}
            {#if aufgabe === 2}
                <div class="mb-3 w-lg pl-5 grid grid-cols-3 gap-2">

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Modell</label>
                        <input type="text" bind:value={name} id="name" name="name"
                               class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white" />
                    </div>

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select bind:value={Element1} id="Element1" name="Element1" on:input={saveModell}
                                class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Punkt">Punkt</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                            <option value="Halbkugel">Halbkugel</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 2</label>
                        <select bind:value={Element2} id="Element2" name="Element2" on:input={saveModell}
                                class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Punkt">Punkt</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                            <option value="Halbkugel">Halbkugel</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Abstand</label>
                        <select bind:value={abstand} id="abstand" name="abstand" on:input={saveModell}
                                class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>in der Nullebene des Koordinatensystems</option>
                            <option value={2}>im Schwerpunkt</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster</label>
                        <select bind:value={taster} id="taster" name="taster" on:change={saveModell}
                                class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>derselbe Taster</option>
                            <option value={2}>verschiedene Taster</option>
                        </select>
                    </div>

                    {#if showWinkelE1}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Winkel zu Element 1</label>
                            <select bind:value={winkelE1} id="winkelE1" name="winkelE1" on:change={saveModell} class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                {#each optionsWinkelE1 as opt}
                                    <option value={opt.value}>{opt.label}</option>
                                {/each}
                            </select>
                        </div>
                    {/if}


                    {#if showWinkelE2}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Winkel zu Element 2</label>
                            <select bind:value={winkelE2} id="winkelE2" name="winkelE2" on:change={saveModell} class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                {#each optionsWinkelE2 as opt}
                                    <option value={opt.value}>{opt.label}</option>
                                {/each}
                            </select>
                        </div>
                    {/if}


                    {#if showTasterschaft1}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Tasterschaft 1</label>
                            <select bind:value={tasterschaft1} id="tasterschaft1" on:change={saveModell} name="tasterschaft1" class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>senkrecht</option>
                                <option value={2}>parallel zu Auswerterichtung</option>
                            </select>
                        </div>
                    {/if}

                    {#if showTasterschaft2}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Tasterschaft 2</label>
                            <select bind:value={tasterschaft2} id="tasterschaft2" on:change={saveModell} name="tasterschaft2" class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>senkrecht</option>
                                <option value={2}>parallel zu Auswerterichtung</option>
                            </select>
                        </div>
                    {/if}

                    {#if showArtDesMasses}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Art des Maßes</label>
                            <select bind:value={artdesmasses} id="artdesmasses" on:change={saveModell} name="artdesmasses" class="w-full h-6 border border-gray-400 px-2 text-sm py-0 bg-white">
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>Stufenmaß</option>
                                <option value={2}>Innen- ode Außenmaß</option>
                            </select>
                        </div>
                    {/if}
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
                <tr class="{selectedRow === i ? 'bg-green-300' : 'hover:bg-green-200'} cursor-pointer"
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