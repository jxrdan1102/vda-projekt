<script lang="ts">
    import { tick } from 'svelte';
    import { createEventDispatcher } from 'svelte';
    import { COMPONENTS, Components } from '$lib/Mapping';
    import type { ColumnDef } from './types';

    // ---------------------------------------------------------------
    // Props
    // ---------------------------------------------------------------

    /** Die Komponentenliste aus analyseprojekt.anakomp */
    export let komponenten: any[];

    /**
     * Spaltendefinitionen – importiere STANDARD_COLUMNS oder DREID_COLUMNS
     * aus ./types.ts, oder definiere eigene.
     */
    export let columns: ColumnDef[];

    /**
     * Edit-Modus:
     * - 'inline'  → Standard: alle Felder immer sichtbar (bind:value + Temp-Werte),
     *               "Alle speichern"-Button, Tab-Navigation über editInputs-Map
     * - 'dblclick' → 3D: Doppelklick öffnet eine Zelle, restliche schreibgeschützt
     */
    export let editMode: 'inline' | 'dblclick' = 'inline';

    /**
     * Zeigt den "Alle speichern"-Button (nur sinnvoll bei editMode='inline')
     */
    export let showSaveAll: boolean = editMode === 'inline';

    // ---------------------------------------------------------------
    // Interner Zustand
    // ---------------------------------------------------------------

    // Für editMode='inline': Temp-Kopien und editInputs-Map
    $: {
        if (editMode === 'inline') {
            komponenten.forEach(comp => {
                // Sicherstellen, dass das Zeilen-Objekt existiert (behebt den Binding-Fehler)
                if (!editInputs[comp.id]) {
                    editInputs[comp.id] = {};
                }
                
                columns.forEach(col => {
                    const tmpKey = col.field + 'Temp';
                    if (comp[tmpKey] === undefined) comp[tmpKey] = comp[col.field];
                    
                    // Optional: Falls du auch die einzelnen Felder vorinitialisieren willst
                    // if (!editInputs[comp.id][col.field]) editInputs[comp.id][col.field] = null as any;
                });
            });
        }
    }

    const editInputs: Record<number, Record<string, HTMLInputElement | HTMLSelectElement>> = {};

    let activeField: { id: number; field: string } | null = null;

    function isActive(comp: any, field: string) {
        return activeField?.id === comp.id && activeField?.field === field;
    }

    function isDirty(comp: any, field: string) {
        return String(comp[field + 'Temp']) !== String(comp[field]);
    }


    // ---------------------------------------------------------------
    // Speichern (inline-Modus, einzelne Komponente)
    // ---------------------------------------------------------------
    async function saveCompFieldInline(event: Event, compId: number) {
        event.preventDefault();

        const compIndex = komponenten.findIndex(c => c.id === compId);
        if (compIndex === -1) return;
        const comp = komponenten[compIndex];

        // In deiner save-Funktion vor dem Fetch:
        const payload: Record<string, any> = {};
        columns.forEach(col => {
            let val = comp[col.field + 'Temp'];
            if (val === '' || val === null || val === undefined) {
                payload[col.field] = null;
            } else {
                // Komma zu Punkt und ab zur API als Zahl
                let normalized = val.toString().replace(',', '.');
                payload[col.field] = parseFloat(normalized);
            }
        });

        const response = await fetch(`/api/anakomponent/${compId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            alert('Fehler beim Speichern');
            return;
        }

        Object.assign(comp, payload);
        columns.forEach(col => { comp[col.field + 'Temp'] = payload[col.field]; });
        komponenten = [...komponenten];
        activeField = null;
        dispatch('saved');
    }
    let selectedRow: number | null = null;

    // ---------------------------------------------------------------
    // "Alle speichern" (inline-Modus)
    // ---------------------------------------------------------------
    async function saveAllComponents() {
        // Wir filtern die Komponenten, die mathematisch gesehen geändert wurden
        const dirtyComps = komponenten.filter(comp =>
            columns.some(col => isDirty(comp, col.field))
        );

        for (const comp of dirtyComps) {
            const payload: Record<string, any> = {};
            
            columns.forEach(col => {
                let val = comp[col.field + 'Temp'];
                
                // 1. Wenn das Feld leer ist -> null
                if (val === '' || val === null || val === undefined) {
                    payload[col.field] = null;
                } else {
                    // 2. Komma zu Punkt umwandeln (falls es ein String ist)
                    let normalized = val.toString().replace(',', '.');
                    // 3. Als Zahl (Float) in den Payload packen
                    const num = parseFloat(normalized);
                    payload[col.field] = isNaN(num) ? null : num;
                }
            });

            try {
                const response = await fetch(`/api/anakomponent/${comp.id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                if (response.ok) {
                    // Nach dem Speichern: Das Original-Objekt mit den neuen Zahlen aktualisieren
                    Object.assign(comp, payload);
                    
                    // WICHTIG: Auch die Temp-Werte wieder auf den neuen Stand bringen
                    columns.forEach(col => {
                        comp[col.field + 'Temp'] = payload[col.field];
                    });
                } else {
                    console.error(`Fehler beim Speichern von Komponente ${comp.id}`);
                }
            } catch (err) {
                console.error(err);
            }
        }

        komponenten = [...komponenten];
        alert('Alle Änderungen gespeichert!');
        dispatch('savedAll');
    }

    // ---------------------------------------------------------------
    // Tab-Navigation (inline-Modus)
    // ---------------------------------------------------------------
    $: fieldNames = columns.map(c => c.field);

    async function handleCompKeyDownInline(e: KeyboardEvent, comp: any, field: string) {
        if (e.key === 'Tab') {
            e.preventDefault();
            let idx = fieldNames.indexOf(field);
            let nextIdx = e.shiftKey ? idx - 1 : idx + 1;
            if (nextIdx < 0) nextIdx = fieldNames.length - 1;
            if (nextIdx >= fieldNames.length) nextIdx = 0;
            const nextEl = editInputs[comp.id]?.[fieldNames[nextIdx]];
            if (nextEl) nextEl.focus();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            await saveCompFieldInline(e, comp.id);
        }
    }


    // ---------------------------------------------------------------
    // berechnen-Checkbox (3D-spezifisch, per showBerechnenCheckbox)
    // ---------------------------------------------------------------
    async function saveBerechnen(id: number, newValue: boolean) {
        try {
            const response = await fetch(`/api/anakomponent/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ berechnen: newValue }),
            });
            if (!response.ok) alert('Fehler beim Speichern der Änderung');
        } catch (error) {
            console.error('Speicherfehler:', error);
        }
    }

    // ---------------------------------------------------------------
    // Event-Dispatcher
    // ---------------------------------------------------------------
    const dispatch = createEventDispatcher<{
        saved: void;
        savedAll: void;
    }>();


    const isHidden = (col, comp) =>
        (col.header === "Anzahl Messungen" && comp.wertart !== 4) ||
        (col.header === "Standardabweichung" && comp.wertart === 5 && comp.berechnen);


    function formatNumber(val) {
        // Wenn der Wert leer, null oder undefined ist, gib leeren String zurück
        if (val === null || val === undefined || val === '') return '';
        
        // Falls der Wert bereits ein String ist (z.B. durch handleNumberInput)
        // geben wir ihn einfach zurück, stellen aber sicher, dass Punkt zu Komma wird
        return val.toString().replace('.', ',');
    }

    function handleNumberInput(e, comp, field) {
        // Wir nehmen den Text 1:1 aus dem Input (z.B. "1," oder " " oder "1,2")
        const v = e.target.value;
        
        // Wir speichern den Text direkt im Temp-Feld
        comp[field + 'Temp'] = v;

        // Trigger Svelte Reactivity
        komponenten = [...komponenten];
    }

    function handleBlur(comp, field) {
        let val = comp[field + 'Temp'];
        if (val !== null && val !== '' && !isNaN(val)) {
            // Hier wird erst beim Verlassen des Feldes auf 3 Stellen gerundet
            comp[field + 'Temp'] = parseFloat(Number(val).toFixed(3));
        }
        komponenten = [...komponenten];
    }

</script>

<div class="border border-gray-300 rounded overflow-hidden bg-gray-200">
    <div class="flex items-center gap-2 px-2 py-1 bg-gray-100 border-b justify-between">
        <span>Komponenten</span>
        {#if showSaveAll && editMode === 'inline'}
            <button
                class="bg-gray-600 text-white text-sm px-3 py-1 rounded hover:bg-gray-700"
                on:click={saveAllComponents}
            >
                Alle speichern
            </button>
        {/if}
    </div>

    <table class="w-full text-sm border-t">
        <thead class="bg-gray-200 text-gray-700">
            <tr>
                <th class="px-3 py-1 text-left">Komponente</th>
                {#each columns as col}
                    <th class="px-2 py-1 text-left">{col.header}</th>
                {/each}
            </tr>
        </thead>
        <tbody class="border-t divide-y divide-gray-500">
            {#each komponenten as comp, i}
                <tr
                    class="{selectedRow === i ? 'bg-cyan-600' : 'hover:bg-gray-100'} cursor-pointer"
                    on:click={() => selectedRow = i}
                >
                    <!-- Komponentenname -->
                    <td class="px-3 py-1">
                        {Components[comp.komponente.kompid] ?? COMPONENTS[comp.komponente.kompid]}
                    </td>

                    <!-- Dynamische Spalten -->
                    {#each columns as col}
                        <td class="px-2 py-1y"
                        >
                            <!-- ==================== INLINE-MODUS ==================== -->
                            {#if editMode === 'inline'}
                                <form
                                    on:submit|preventDefault={(e) => saveCompFieldInline(e, comp.id)}
                                    class="flex items-center gap-1"
                                >
                                    {#if col.type === 'checkbox' && col.showBerechnenCheckbox && comp.wertart == 5}
                                        <div class="flex items-center gap-2" style="min-width: 5em;"> A/3 
                                                <input
                                                    id="berechnen"
                                                    name="berechnen"
                                                    type="checkbox"
                                                    bind:checked={comp.berechnen}
                                                    on:change={() => saveBerechnen(comp.id, comp.berechnen)}
                                                />
                                        </div>
                                    {:else if col.type === 'checkbox' && comp.wertart != 5}
                                        <div class="flex items-center gap-2" style="min-width: 5em;">  
                                                <input
                                                    id="berechnen"
                                                    name="berechnen"
                                                    type="checkbox"
                                                    hidden
                                                    bind:checked={comp.berechnen}
                                                    on:change={() => saveBerechnen(comp.id, comp.berechnen)}
                                                />
                                        </div>
                                    {/if}
                                    {#if col.type === 'number'}
                                        <input
                                            type="number"
                                            name={col.field}
                                            step="1"
                                            bind:this={editInputs[comp.id][col.field]}                                            
                                            bind:value={comp[col.field + 'Temp']}
                                            disabled={isHidden(col, comp)}
                                            class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b
                                                focus:outline-none focus:ring-0
                                                {isActive(comp, col.field) ? 'bg-gray-100 border-black' : 'border-gray-400'}
                                                {isDirty(comp, col.field) ? 'text-blue-600' : ''}
                                                {isHidden(col, comp) ? 'opacity-0 pointer-events-none' : ''}"
                                        />
                                    {:else if col.type === 'select'}
                                        <select
                                            name={col.field}
                                            bind:this={editInputs[comp.id][col.field]}
                                            bind:value={comp[col.field + 'Temp']}
                                            class="w-full text-sm py-[2px] leading-5 bg-transparent border-0 border-b
                                                focus:outline-none focus:ring-0
                                                {isActive(comp, col.field) ? 'bg-gray-100 border-black' : 'border-gray-400'}
                                                {isDirty(comp, col.field) ? 'text-blue-600' : ''}"
                                            on:focus={() => activeField = { id: comp.id, field: col.field }}
                                            on:blur={() => activeField = null}
                                            on:keydown={(e) => handleCompKeyDownInline(e, comp, col.field)}
                                        >
                                            <option value="" disabled>Bitte wählen</option>
                                            {#each col.options ?? [] as opt}
                                                <option value={opt.value}>{opt.label}</option>
                                            {/each}
                                        </select>
                                    {:else if col.type === 'text'}
                                        <div class="relative w-full">
                                            <input
                                                type="text"
                                                inputmode="decimal"
                                                bind:this={editInputs[comp.id][col.field]}
                                                class="w-full pr-10 text-sm py-[2px] leading-5 bg-transparent border-0 border-b
                                                        focus:outline-none focus:ring-0
                                                        {isActive(comp, col.field) ? 'bg-gray-100 border-black' : 'border-gray-400'}
                                                        {isDirty(comp, col.field) ? 'text-blue-600' : ''}
                                                        {isHidden(col, comp) ? 'opacity-0 pointer-events-none' : ''}"
                                                value={formatNumber(comp[col.field + 'Temp'])}
                                                on:input={(e) => handleNumberInput(e, comp, col.field)}
                                                on:focus={() => activeField = { id: comp.id, field: col.field }}
                                                on:blur={() => activeField = null}
                                                on:keydown={(e) => handleCompKeyDownInline(e, comp, col.field)}
                                            />
                                            {#if col.field != "terml1"}
                                            <span class="absolute right-1 top-1/2 -translate-y-1/2 text-gray-500 text-sm pointer-events-none">
                                                µm
                                            </span>
                                            {/if}
                                        </div>
                                    {/if}
                                </form>
                            {/if}
                        </td>
                    {/each}
                </tr>
            {/each}
        </tbody>
    </table>
</div>
