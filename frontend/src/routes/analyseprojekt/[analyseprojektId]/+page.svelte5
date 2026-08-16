<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from "$app/stores";
    import {COMPONENTS, Components} from "$lib/Mapping";
    import {tcMapping} from "C:\\Users\\Jason\\vda-projekt\\backend\\tcParameterMapping";
    import {tick} from 'svelte';


    let editingCompField: { id: number; field: string } | null = null;
    let compFieldValue: any = "";
    async function saveBerechnen(id: number, newValue: boolean) {
        try {
            const response = await fetch(`/api/anakomponent/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({ berechnen: newValue })
            });

            if (!response.ok) {
                alert('Fehler beim Speichern der Änderung');
            }
        } catch (error) {
            console.error('Speicherfehler:', error);
            alert('Fehler beim Speichern der Änderung');
        }
    }

    async function startEditCompField(comp: any, field: string) {
        editingCompField = { id: comp.id, field };
        compFieldValue = comp[field]; // Nur einen Wert verwenden!
        await tick();
        editInput?.focus();
    }
    const kmgConstnums = new Set([102, 103, 104, 105, 141, 161]);

    function isKMG(konst: number) {
        return kmgConstnums.has(konst);
    }
    function isEditable(konst: any) {
        // Beispiel: Konstanten mit isKMG true sind nicht editierbar
        return !isKMG(konst.constnum);
    }

    async function handleKeyDownConst(event: KeyboardEvent, konst: any, index: number) {
        if (event.key === 'Tab') {
            event.preventDefault();

            // Speichern
            await saveConstVal(event, konst.id);
            await tick();

            // Nächste editierbare Konstante finden
            let nextIndex = index;
            const length = analyseprojekt.anakonst.length;
            do {
                nextIndex = event.shiftKey ? nextIndex - 1 : nextIndex + 1;

                if (nextIndex >= length) nextIndex = 0;
                if (nextIndex < 0) nextIndex = length - 1;

                // Falls wir wieder beim Start sind und nichts editierbar, abbrechen (Safety)
                if (nextIndex === index) {
                    // Keine andere editierbare Konstante gefunden
                    return;
                }

            } while (!isEditable(analyseprojekt.anakonst[nextIndex]));

            // Edit-Modus auf nächste editierbare Konstante setzen
            startEditConst(analyseprojekt.anakonst[nextIndex]);

            await tick();
            editInput?.focus();
        }
        else if (event.key === 'Escape') {
            cancelEdit();
        }
    }
    function cancelEditCompField() {
        editingCompField = null;
    }

    let editingConstId: number | null = null;
    let constvalEdit = 0;

    let editInput: any;

    async function startEditConst(konst: any) {
        if (isKMG(konst.constnum)) return; // kein Edit bei KMG
        editingConstId = konst.id;
        constvalEdit = konst.constval ?? 0;

        await tick(); // sicherstellen, dass das Input gerendert wurde
        editInput?.focus();
    }


    function cancelEdit() {
        editingConstId = null;
    }


    const editableFields = ['terml0', 'terml1', 'verteilung', 'wertart', 'freigrad'];
    async function handleKeyDown(e: KeyboardEvent, comp: any, fieldName: string) {
        if (e.key === 'Tab') {
            e.preventDefault();

            // Erst aktuelle Eingabe speichern
            await tick(); // bind:value wartet auf Update
            await saveCompField(e, comp.id);

            // Index des aktuellen Feldes
            let currentIndex = editableFields.indexOf(fieldName);

            // Nächstes Feld bestimmen
            let nextIndex = e.shiftKey ? currentIndex - 1 : currentIndex + 1;

            // Wrap around
            if (nextIndex >= editableFields.length) nextIndex = 0;
            if (nextIndex < 0) nextIndex = editableFields.length - 1;

            let nextField = editableFields[nextIndex];

            // anzahl_messungen nur aktiv, wenn wertart === 4
            if (nextField === 'anzahl_messungen' && comp.wertart !== 4) {
                nextIndex = e.shiftKey ? nextIndex - 1 : nextIndex + 1;
                if (nextIndex >= editableFields.length) nextIndex = 0;
                if (nextIndex < 0) nextIndex = editableFields.length - 1;
                nextField = editableFields[nextIndex];
            }

            // Nächstes Feld aktivieren
            startEditCompField(comp, nextField);

        } else if (e.key === 'Escape') {
            cancelEditCompField();
        }
    }



    async function saveConstVal(event: any, id: number) {
        event.preventDefault();
        const payload: Record<string, any> = {};

        if (editingConstId) {
            payload['constval'] = constvalEdit;
        }

        const response = await fetch(`/api/anakonstant/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            const index = analyseprojekt.anakonst.findIndex((k: any) => k.id === id);
            if (index !== -1) {
                analyseprojekt.anakonst[index].constval = constvalEdit;
            }
            editingConstId = null;
        } else {
            alert("Fehler beim Speichern der Konstante");
        }
    }


    export let data;
    let analyseprojekt = data.analyseprojekt;
    $: analyseprojektId = $page.params.analyseprojektId;

    let name = analyseprojekt.name ?? "";
    let aenderungszustand = analyseprojekt.aenderungszustand ?? "";
    let identnr = analyseprojekt.identnr ?? null;
    let remark = analyseprojekt.remark ?? "";
    let tolfaktor = analyseprojekt.tolfaktor === 1 || analyseprojekt.tolfaktor === true;


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

    let fk_modell = 0;

    async function saveCompField(event: Event, compId: number) {
        event.preventDefault();

        const compIndex = analyseprojekt.anakomp.findIndex(c => c.id === compId);
        if (compIndex === -1) return;

        const comp = analyseprojekt.anakomp[compIndex];

        const payload = {
            terml0: comp.terml0Temp,
            terml1: comp.terml1Temp,
            verteilung: comp.verteilungTemp,
            wertart: comp.wertartTemp,
            freigrad: comp.freigradTemp
        };

        const response = await fetch(`/api/anakomponent/${compId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            alert("Fehler beim Speichern");
            return;
        }

        // Alles synchronisieren
        Object.assign(comp, payload);
        Object.assign(comp, {
            terml0Temp: payload.terml0,
            terml1Temp: payload.terml1,
            verteilungTemp: payload.verteilung,
            wertartTemp: payload.wertart,
            freigradTemp: payload.freigrad
        });

        analyseprojekt.anakomp = [...analyseprojekt.anakomp];
        activeField = null;
    }

    async function handleCompKeyDown(e: KeyboardEvent, comp: any, field: string) {
        if (e.key === 'Tab') {
            e.preventDefault();

            const fields = ['terml0', 'terml1', 'verteilung', 'wertart', 'freigrad'];
            let idx = fields.indexOf(field);

            let nextIdx = e.shiftKey ? idx - 1 : idx + 1;

            if (nextIdx < 0) nextIdx = fields.length - 1;
            if (nextIdx >= fields.length) nextIdx = 0;

            const nextField = fields[nextIdx];

            await tick(); // wichtig!

            const nextEl = editInputs[comp.id]?.[nextField];
            if (nextEl) {
                nextEl.focus();
            }
        }
        else if (e.key === 'Enter') {
            e.preventDefault();
            await saveCompField(e, comp.id);
            return;
        }
    }

    // Beim Laden der Tabelle sicherstellen, dass Temp-Werte existieren
    analyseprojekt.anakomp.forEach(comp => {
        if (comp.terml0Temp === undefined) comp.terml0Temp = comp.terml0;
        if (comp.terml1Temp === undefined) comp.terml1Temp = comp.terml1;
        if (comp.verteilungTemp === undefined) comp.verteilungTemp = comp.verteilung;
        if (comp.wertartTemp === undefined) comp.wertartTemp = comp.wertart;
        if (comp.freigradTemp === undefined) comp.freigradTemp = comp.freigrad;
    });

    let activeField: { id: number; field: string } | null = null;
    function isActive(comp, field) {
        return activeField?.id === comp.id && activeField?.field === field;
    }

    function isDirty(comp, field) {
        return String(comp[field + 'Temp']) !== String(comp[field]);
    }

    async function saveAllComponents() {
        const dirtyComps = analyseprojekt.anakomp.filter(comp => {
            return (
                comp.terml0Temp !== comp.terml0 ||
                comp.terml1Temp !== comp.terml1 ||
                comp.verteilungTemp !== comp.verteilung ||
                comp.wertartTemp !== comp.wertart ||
                comp.freigradTemp !== comp.freigrad
            );
        });

        for (const comp of dirtyComps) {
            const payload = {
                terml0: comp.terml0Temp,
                terml1: comp.terml1Temp,
                verteilung: comp.verteilungTemp,
                wertart: comp.wertartTemp,
                freigrad: comp.freigradTemp
            };

            try {
                const response = await fetch(`/api/anakomponent/${comp.id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    console.error(`Fehler beim Speichern von Komponente ${comp.id}`);
                } else {
                    // Synchronisieren
                    Object.assign(comp, payload);
                }
            } catch (err) {
                console.error(err);
            }
        }

        // Reaktivität triggern
        analyseprojekt.anakomp = [...analyseprojekt.anakomp];
        alert("Alle Änderungen gespeichert!");
    }

    const editInputs: Record<number, Record<string, HTMLInputElement | HTMLSelectElement>> = {};

    analyseprojekt.anakomp.forEach(comp => {
        if (!editInputs[comp.id]) {
            editInputs[comp.id] = {};
        }
    });

    const unitOrder = {
        "°C": 1,   // Temperatur
        "1/°K": 2,
        "K": 3,
        "mm": 4,   // Länge
        "N": 5,     // Kraft
        "%": 6,
    };

    $: sortedKonstanten = [...(analyseprojekt.anakonst || [])].sort((a, b) => {
        const unitA = tcMapping[a.constnum]?.einheit || "";
        const unitB = tcMapping[b.constnum]?.einheit || "";

        const orderA = unitOrder[unitA] ?? 999;
        const orderB = unitOrder[unitB] ?? 999;

        // zuerst nach definierter Reihenfolge
        if (orderA !== orderB) return orderA - orderB;

        // danach alphabetisch nach Einheit
        if (unitA !== unitB) return unitA.localeCompare(unitB);

        // dann alphabetisch nach Name
        const nameA = tcMapping[a.constnum]?.übersetzung || tcMapping[a.constnum]?.key;
        const nameB = tcMapping[b.constnum]?.übersetzung || tcMapping[b.constnum]?.key;

        return nameA.localeCompare(nameB);
    });


    async function openReport() {
    const start = "2024-01-01";
    const end = "2024-12-31";

    const response = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/report?start_date=${start}&end_date=${end}`, {
        method: 'GET',          // oder POST, falls dein Endpoint POST erwartet
        credentials: 'include', // Cookies mitsenden
        headers: { 'Content-Type': 'application/json' },

    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    window.open(url);
}
</script>

<section class="space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" action="?/speichern">
        <h1 class="text-base font-semibold border-b pb-2">Analyseprojekt
            <button type="button" name="berechnen" on:click={() => goto(`/analyseprojekt/${analyseprojektId}/MU`) } class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
                Berechnen
            </button>
            <button type="submit" name="speichern" class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
                Speichern
            </button>
            <button type="button" on:click={openReport} class="bg-gray-600 mr-2 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right">
                Report öffnen
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
                <label for="tolfaktor" class="text-gray-700 text-xs object-bottom">Eignungskennwert</label>
                <input type="checkbox" name="tolfaktor" id="tolfaktor" bind:checked={tolfaktor} class="h-4 w-4 text-gray-600 border-gray-400 rounded" />
            </div>
            <input hidden type="number" name="fk_modell" id="fk_modell" bind:value={data.analyseprojekt.modell.id} class="h-4 w-4 text-gray-600 border-gray-400 rounded" />


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


    {#if analyseprojekt.anakonst?.length > 0}
        <h2 class="text-base font-semibold">Konstanten</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 lg:grid-cols-4 lg:grid-cols-5 gap-3">
            {#each sortedKonstanten as konst, index}
                {#if (konst.constnum != 2 && konst.constnum != 3 && konst.constnum != 4) || tolfaktor == true }
                <div class="bg-white border border-gray-300 rounded px-3 py-1 hover:shadow
      {isKMG(konst.constnum) ? 'opacity-70 cursor-not-allowed' : 'cursor-text'}"
                     on:dblclick={() => !isKMG(konst.constnum) && startEditConst(konst)}
                >
                    {#if editingConstId === konst.id}
                        <form
                                on:submit|preventDefault={(e) => saveConstVal(e, konst.id)}
                                class="space-y-1"
                        >
                            <div class="text-sm font-bold">{tcMapping[konst.constnum].übersetzung || tcMapping[konst.constnum].key}</div>
                            <div class="flex justify-end gap-2 mt-1">

                                <input
                                        type="number"
                                        step="any"
                                        bind:this={editInput}
                                        bind:value={constvalEdit}
                                        class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0"
                                        autofocus
                                        on:keydown={(e) => handleKeyDownConst(e, konst, index)}
                                />
                                {tcMapping[konst.constnum].einheit}

                                <button type="submit" class="text-sm text-green-700">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                    </svg>
                                </button>
                                <button type="button" on:click={cancelEdit} class="text-sm text-red-600">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                    </svg>
                                </button>
                            </div>
                        </form>
                    {:else}
                        <div class="text-sm font-bold">{tcMapping[konst.constnum].übersetzung || tcMapping[konst.constnum].key}</div>
                        <div class="flex">
                            <input
                                    type="text"
                                    readonly
                                    value={`${konst.constval} ${tcMapping[konst.constnum].einheit}`}
                                    class="w-min text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-transparent text-gray-700 focus:outline-none focus:ring-0"
                                    style="caret-color: transparent; /* verhindert blinkenden Cursor */"
                                    tabindex="-1"
                            /></div>
                    {/if}
                </div>
                {/if }
            {/each}

        </div>
    {/if}

    <div class="border border-gray-300 rounded overflow-hidden bg-gray-200">
        <div class="flex items-center gap-2 px-2 py-1 bg-gray-100 border-b justify-between">
        <span>Komponenten</span>
        <button
                class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700 float-right"
                on:click={saveAllComponents}
        >
            Alle speichern
        </button>
    </div>
        <table class="w-full text-sm border-t">
            <thead class="bg-gray-200 text-gray-700">
            <tr>
                <th class="px-5 py-1 text-left ">Komponente</th>
                <th class="px-5 py-1 text-left w-10">L0 längenunabhängiger Term</th>
                <th class="px-5 py-1 text-left w-10">L1 längenabhängiger Term</th>
                <th class="px-5 py-1 text-left w-50">Verteilung</th>
                <th class="px-5 py-1 text-left w-50">Streuungsparameter</th>
                <th class="px-5 py-1 text-left w-50">Freiheitsgrad</th>
            </tr>
            </thead>
            <tbody class="border-t divide-y divide-gray-500">
            {#each analyseprojekt.anakomp as comp, i}
                {@const terml0Ref = undefined}
                {@const terml1Ref = undefined}
                {@const verteilungRef = undefined}
                {@const wertartRef = undefined}
                {@const freigradRef = undefined}
                <tr class="{selectedRow === i ? 'bg-green-200' : 'hover:bg-gray-100'} cursor-pointer" on:click={() => selectedRow = i}>
                    <td class="px-5 py-1">{Components[comp.komponente.kompid] ?? COMPONENTS[comp.komponente.kompid]}</td>

                    <!-- L0 -->
                    <td class="px-5 py-1">
                        <form on:submit|preventDefault={(e) => saveCompField(e, comp.id, 'terml0')} class="flex items-center gap-1">
                            <input type="number"
                                   name="terml0"
                                   step="any"
                                   bind:this={editInputs[comp.id]['terml0']}
                                   bind:value={comp.terml0Temp}
                                   class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0
                                   {isActive(comp,'terml0') ? 'bg-gray-100 border-black' : 'bg-transparent border-gray-400'}
                                   {isDirty(comp,'terml0') ? 'text-blue-600' : ''}"

                                    on:focus={() => activeField = { id: comp.id, field: 'terml0' }}
                                    on:blur={() => activeField = null}
                                   on:keydown={(e) => handleCompKeyDown(e, comp, 'terml0')}
                            />
                        </form>
                    </td>

                    <!-- L1 -->
                    <td class="px-5 py-1">
                        <form on:submit|preventDefault={(e) => saveCompField(e, comp.id, 'terml1')} class="flex items-center gap-1">
                            <input type="number"
                                   name="terml1"
                                   step="any"
                                   bind:this={editInputs[comp.id]['terml1']}
                                   bind:value={comp.terml1Temp}
                                   class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0
                                   {isActive(comp,'terml1') ? 'bg-gray-100 border-black' : 'bg-transparent border-gray-400'}
                                   {isDirty(comp,'terml1') ? 'text-blue-600' : ''}"

                                   on:focus={() => activeField = { id: comp.id, field: 'terml1' }}
                                   on:blur={() => activeField = null}
                                   on:keydown={(e) => handleCompKeyDown(e, comp, 'terml1')}
                            />
                        </form>
                    </td>

                    <!-- Verteilung -->
                    <td class="px-5 py-1">
                        <form on:submit|preventDefault={(e) => saveCompField(e, comp.id, 'verteilung')} class="flex items-center gap-1">
                            <select bind:value={comp.verteilungTemp}
                                    bind:this={editInputs[comp.id]['verteilung']}
                                    name="verteilung"
                                    class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0
                                    {isActive(comp,'verteilung') ? 'bg-gray-100 border-black' : 'bg-transparent border-gray-400'}
                                   {isDirty(comp,'verteilung') ? 'text-blue-600' : ''}"

                                    on:focus={() => activeField = { id: comp.id, field: 'verteilung' }}
                                    on:blur={() => activeField = null}
                                    on:keydown={(e) => handleCompKeyDown(e, comp, 'verteilung')}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>Rechteckverteilung</option>
                                <option value={2}>Normalverteilung</option>
                                <option value={3}>Dreieckverteilung</option>
                            </select>
                        </form>
                    </td>

                    <!-- Wertart -->
                    <td class="px-5 py-1">
                        <form on:submit|preventDefault={(e) => saveCompField(e, comp.id, 'wertart')} class="flex items-center gap-1">
                            <select bind:value={comp.wertartTemp}
                                    bind:this={editInputs[comp.id]['wertart']}
                                    name="wertart"
                                    class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0
                                    {isActive(comp,'wertart') ? 'bg-gray-100 border-black' : 'bg-transparent border-gray-400'}
                                    {isDirty(comp,'wertart') ? 'text-blue-600' : ''}"

                                    on:focus={() => activeField = { id: comp.id, field: 'wertart' }}
                                    on:blur={() => activeField = null}
                                    on:keydown={(e) => handleCompKeyDown(e, comp, 'wertart')}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>Halbweite</option>
                                <option value={2}>Spannweite</option>
                                <option value={3}>Standardabweichung</option>
                            </select>
                        </form>
                    </td>

                    <!-- Freiheitsgrad -->
                    <td class="px-5 py-1">
                        <form on:submit|preventDefault={(e) => saveCompField(e, comp.id, 'freigrad')} class="flex items-center gap-1">
                            <select bind:value={comp.freigradTemp}
                                    bind:this={editInputs[comp.id]['freigrad']}
                                    name="freigrad"
                                    class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0
                                    {isActive(comp,'freigrad') ? 'bg-gray-100 border-black' : 'bg-transparent border-gray-400'}
                                    {isDirty(comp,'freigrad') ? 'text-blue-600' : ''}"

                                    on:focus={() => activeField = { id: comp.id, field: 'freigrad' }}
                                    on:blur={() => activeField = null}
                                    on:keydown={(e) => handleCompKeyDown(e, comp, 'freigrad')}     on:focus={() => editingCompField = { id: comp.id, field: 'terml0' }}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>Unbegrenzt</option>
                                <option value={2}>N-1</option>
                            </select>
                        </form>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>

</section>



