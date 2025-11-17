<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from "$app/stores";
    import Modal from "$lib/components/Modal.svelte";
    import KmgInfoPage from "./kmgkmg/+page.svelte";
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
    async function saveCompField(event: any, id: number) {
        event.preventDefault();
        const payload: Record<string, any> = {};

        if (editingCompField?.field) {
            payload[editingCompField.field] = compFieldValue;
        }

        const response = await fetch(`/api/anakomponent/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            const index = analyseprojekt.anakomp.findIndex((k: any) => k.id === id);
            if (index !== -1 && editingCompField?.field) {
                analyseprojekt.anakomp[index][editingCompField.field] = compFieldValue;
            }
            editingCompField = null;
        } else {
            alert("Fehler beim Speichern der Komponente");
        }
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

    $: showKmg = !!$page.state?.kmgInfo;


    async function openKmg() {
        const href = `/analyseprojekt/${analyseprojektId}/kmg`;
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

    <div class="border border-gray-300 rounded overflow-hidden bg-gray-200">
        <div class="flex items-center gap-2 px-2 py-1 bg-gray-100 border-b">
            Komponenten

        </div>
            <table class="w-full text-sm border-t">
            <thead class="bg-gray-200 text-gray-700">
            <tr>
                <th class="px-3 py-1 text-left">Komponente</th>
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
                    on:click={() => selectedRow = i}>
                    <td class="px-3 py-1">{Components[comp.komponente.kompid] ? Components[comp.komponente.kompid] : COMPONENTS[comp.komponente.kompid]}</td>
                    <td
                            class="px-2 py-1 clickable-cell"
                            on:dblclick={() => startEditCompField(comp, 'terml0')}
                    >
                        {#if editingCompField?.id === comp.id && editingCompField?.field === 'terml0'}
                            <form on:submit|preventDefault={(e) => saveCompField(e, comp.id)} class="flex items-center gap-1">
                                <div class="flex justify-end gap-2 mt-1">
                                    <input type="hidden" name="compId" value={comp.id} />

                                    <input id="terml0"
                                           name="terml0"
                                           type="number"
                                           step="any"
                                           bind:this={editInput}
                                           bind:value={compFieldValue}
                                           class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0"
                                           autofocus
                                           on:click|stopPropagation
                                           on:keydown={(e) => handleKeyDown(e, comp, 'terml0')}
                                    />
                                    <button type="submit" class="text-sm text-green-700">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                    <button type="button" on:click={cancelEditCompField} class="text-sm text-red-600">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                </div>
                            </form>
                        {:else}
                            <span class="inline-block w-full min-h-[1.2rem]">{comp.terml0 ?? '\u00A0'}</span>
                        {/if}
                    </td>
                    <td
                            class="px-2 py-1 clickable-cell"
                            on:dblclick={() => startEditCompField(comp, 'terml1')}
                    >
                        {#if editingCompField?.id === comp.id && editingCompField?.field === 'terml1'}
                            <form on:submit|preventDefault={(e) => saveCompField(e, comp.id)} class="flex items-center gap-1">
                                <div class="flex justify-end gap-2 mt-1">
                                    <input type="hidden" name="compId" value={comp.id} />

                                    <input id="terml1"
                                           name="terml1"
                                           type="number"
                                           step="any"
                                           bind:this={editInput}
                                           bind:value={compFieldValue}
                                           class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0"
                                           autofocus
                                           on:click|stopPropagation
                                           on:keydown={(e) => handleKeyDown(e, comp, 'terml1')}
                                    />
                                    <button type="submit" class="text-sm text-green-700">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                    <button type="button" on:click={cancelEditCompField} class="text-sm text-red-600">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                </div>
                            </form>
                        {:else}
                            <span class="inline-block w-full min-h-[1.2rem]">{comp.terml1 ?? '\u00A0'}</span>
                        {/if}
                    </td>
                    <td
                            class="px-2 py-1 clickable-cell"
                            on:dblclick={() => startEditCompField(comp, 'verteilung')}
                    >
                        {#if editingCompField?.id === comp.id && editingCompField?.field === 'verteilung'}
                            <form on:submit|preventDefault={(e) => saveCompField(e, comp.id)} class="flex items-center gap-1">
                                <div class="flex justify-end gap-2 mt-1">
                                    <input type="hidden" name="compId" value={comp.id} />
                                    <select id="verteilung"
                                            name="verteilung"
                                            bind:this={editInput}
                                            bind:value={compFieldValue}
                                            class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0"
                                            autofocus
                                            on:click|stopPropagation
                                            on:keydown={(e) => handleKeyDown(e, comp, 'verteilung')}
                                    >
                                        <option value="" disabled>Bitte wählen</option>
                                        <option value={1}>Rechteckverteilung</option>
                                        <option value={2}>Normalverteilung</option>
                                        <option value={3}>Dreieckverteilung</option>
                                    </select>
                                    <button type="submit" class="text-sm text-green-700">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                    <button type="button" on:click={cancelEditCompField} class="text-sm text-red-600">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                </div>
                            </form>
                        {:else}
                            <span class="inline-block w-full min-h-[1.2rem]">{getVerteilungText(comp.verteilung) || '\u00A0'}</span>
                        {/if}
                    </td>

                    <td
                            class="px-2 py-1 clickable-cell"
                            on:dblclick={() => startEditCompField(comp, 'wertart')}
                    >
                        {#if editingCompField?.id === comp.id && editingCompField?.field === 'wertart'}
                            <form on:submit|preventDefault={(e) => saveCompField(e, comp.id)} class="flex items-center gap-1">
                                <div class="flex justify-end gap-2 mt-1">
                                    <input type="hidden" name="compId" value={comp.id} />
                                    <select id="wertart"
                                            name="wertart"
                                            bind:this={editInput}
                                            bind:value={compFieldValue}
                                            class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0"
                                            autofocus
                                            on:click|stopPropagation
                                            on:keydown={(e) => handleKeyDown(e, comp, 'wertart')}
                                    >
                                        <option value="" disabled>Bitte wählen</option>
                                        <option value={1}>Halbweite</option>
                                        <option value={2}>Spannweite</option>
                                        <option value={3}>Standardabweichung</option>
                                    </select>
                                    <button type="submit" class="text-sm text-green-700">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                    <button type="button" on:click={cancelEditCompField} class="text-sm text-red-600">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                </div>
                            </form>
                        {:else}
                            <span class="inline-block w-full min-h-[1.2rem]">{getWertartText(comp.wertart) || '\u00A0'}</span>
                        {/if}
                    </td>
                    <td
                            class="px-2 py-1 clickable-cell"
                            on:dblclick={() => startEditCompField(comp, 'freigrad')}
                    >
                        {#if editingCompField?.id === comp.id && editingCompField?.field === 'freigrad'}
                            <form on:submit|preventDefault={(e) => saveCompField(e, comp.id)} class="flex items-center gap-1">
                                <div class="flex justify-end gap-2 mt-1">
                                    <input type="hidden" name="compId" value={comp.id} />

                                    <select id="freigrad"
                                           name="freigrad"
                                           bind:this={editInput}
                                           bind:value={compFieldValue}
                                           class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-black focus:ring-0"
                                           autofocus
                                           on:click|stopPropagation
                                           on:keydown={(e) => handleKeyDown(e, comp, 'freigrad')}>
                                        <option value="" disabled>Bitte wählen</option>
                                        <option value={1}>Unbegrenzt</option>
                                        <option value={2}>N-1</option>
                                    </select>

                                    <button type="submit" class="text-sm text-green-700">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                    <button type="button" on:click={cancelEditCompField} class="text-sm text-red-600">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </button>
                                </div>
                            </form>
                        {:else}
                            <span class="inline-block w-full min-h-[1.2rem]">{getFreigradText(comp.freigrad) || '\u00A0'}</span>
                        {/if}
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
    {#if analyseprojekt.anakonst?.length > 0}
        <h2 class="text-base font-semibold">Konstanten</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 lg:grid-cols-4 lg:grid-cols-5 gap-3">
            {#each analyseprojekt.anakonst as konst, index}
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

</section>


<Modal open={showKmg} on:close={closeModal}>
    <KmgInfoPage data={$page.state.kmgInfo} />
</Modal>
