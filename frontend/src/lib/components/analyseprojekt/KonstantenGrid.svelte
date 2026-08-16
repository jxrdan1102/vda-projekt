<script lang="ts">
    import { tick } from 'svelte';
    import { tcMapping } from 'C:\\Users\\Jason\\vda-projekt\\backend\\tcParameterMapping';

    // ---------------------------------------------------------------
    // Props
    // ---------------------------------------------------------------

    /** Die Liste der Konstanten (analyseprojekt.anakonst) */
    export let konstanten: any[] = [];

    /**
     * Optionale Filterfunktion – wird für jede Konstante aufgerufen.
     * Gibt sie `false` zurück, wird die Karte ausgeblendet.
     * Standard: alle anzeigen.
     *
     * Beispiel (Standard-Analyseprojekt):
     *   filterFn={(k) => (k.constnum != 2 && k.constnum != 3 && k.constnum != 4) || tolfaktor}
     */
    export let filterFn: ((konst: any) => boolean) | null = null;

    // ---------------------------------------------------------------
    // KMG-Logik (identisch in beiden Seiten)
    // ---------------------------------------------------------------
    const kmgConstnums = new Set([102, 103, 104, 105, 141, 161]);

    function isKMG(constnum: number): boolean {
        return kmgConstnums.has(constnum);
    }

    function isEditable(konst: any): boolean {
        return !isKMG(konst.constnum);
    }

    // ---------------------------------------------------------------
    // Edit-Zustand
    // ---------------------------------------------------------------
    let editingConstId: number | null = null;
    let constvalEdit = 0;
    let editInput: any;

    async function startEditConst(konst: any) {
        if (isKMG(konst.constnum)) return;
        editingConstId = konst.id;
        constvalEdit = konst.constval ?? 0;
        await tick();
        editInput?.focus();
    }

    function cancelEdit() {
        editingConstId = null;
    }

    // ---------------------------------------------------------------
    // Speichern – gibt das aktualisierte Array nach oben weiter
    // ---------------------------------------------------------------

    // ---------------------------------------------------------------
    // Event-Dispatcher für Parent-Kommunikation
    // ---------------------------------------------------------------
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher<{
        saved: { id: number; constval: number };
    }>();

    // ---------------------------------------------------------------
    // Gefilterte + sortierte Liste (reaktiv)
    // ---------------------------------------------------------------
    const unitOrder: Record<string, number> = {
        '°C': 1,
        '1/°K': 2,
        'K': 3,
        'mm': 4,
        'µm': 5,
        'N': 6,
        '%': 7,
        '°': 8,
        '10-6/K': 9,
    };

    $: displayKonstanten = [...konstanten]
        .filter(k => filterFn ? filterFn(k) : true)
        .sort((a, b) => {
            const unitA = tcMapping[a.constnum]?.einheit || '';
            const unitB = tcMapping[b.constnum]?.einheit || '';
            const orderA = unitOrder[unitA] ?? 999;
            const orderB = unitOrder[unitB] ?? 999;
            if (orderA !== orderB) return orderA - orderB;
            if (unitA !== unitB) return unitA.localeCompare(unitB);
            const nameA = tcMapping[a.constnum]?.übersetzung || tcMapping[a.constnum]?.key || '';
            const nameB = tcMapping[b.constnum]?.übersetzung || tcMapping[b.constnum]?.key || '';
            return nameA.localeCompare(nameB);
        });
    // Für die Inline-Logik: Wir erstellen Temp-Werte für alle Konstanten
    $: {
        konstanten.forEach(k => {
            if (k.constvalTemp === undefined) {
                // Nur umwandeln, wenn k.constval wirklich existiert (nicht null/undefined)
                // Falls null, setzen wir einen leeren String, damit isDirty nicht triggert
                k.constvalTemp = k.constval != null 
                    ? k.constval.toString().replace('.', ',') 
                    : "";
            }
        });
    }

// Die universelle isDirty Funktion für den Farb-Check
    function isDirty(konst: any) {
        if (konst.constvalTemp === undefined) return false;
        const sTemp = String(konst.constvalTemp).replace(',', '.').trim();
        const sOrig = String(konst.constval ?? '').replace(',', '.').trim();
        
        // Numerischer Vergleich, damit "1,2" und "1,20" gleich behandelt werden
        const nTemp = parseFloat(sTemp);
        const nOrig = parseFloat(sOrig);
        
        if (isNaN(nTemp) && isNaN(nOrig)) return false;
        return nTemp !== nOrig;
    }

    function handleNumberInput(e: any, konst: any) {
        konst.constvalTemp = e.target.value;
        konstanten = [...konstanten];
    }

    async function saveConstVal(konst: any) {
        const sTemp = String(konst.constvalTemp).replace(',', '.').trim();
        const numericValue = parseFloat(sTemp);
        if (isNaN(numericValue)) return;

        const response = await fetch(`/api/anakonstant/${konst.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ constval: numericValue }),
        });

        if (response.ok) {
            konst.constval = numericValue;
            konst.constvalTemp = numericValue.toString().replace('.', ',');
            konstanten = [...konstanten];
            dispatch('saved', { id: konst.id, constval: numericValue });
        }
    }

    async function handleKeyDown(event: KeyboardEvent, konst: any, index: number) {
        if (event.key === 'Enter' || event.key === 'Tab') {
            // Nur speichern, wenn sich wirklich was geändert hat
            if (isDirty(konst)) {
                await saveConstVal(konst);
            }

            // Bei Tab zur nächsten Konstante springen
            if (event.key === 'Tab') {
                event.preventDefault();
                const nextIdx = event.shiftKey ? index - 1 : index + 1;
                const allInputs = document.querySelectorAll('.konst-input') as NodeListOf<HTMLInputElement>;
                if (allInputs[nextIdx]) {
                    allInputs[nextIdx].focus();
                }
            }
        }
    }
</script>

{#if displayKonstanten.length > 0}
    <h2 class="text-base font-semibold mb-2">Konstanten</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-3">
        {#each displayKonstanten as konst, index}
            <div class="bg-white border border-gray-300 rounded px-3 py-2 hover:shadow transition-shadow h-full flex flex-col justify-between {isKMG(konst.constnum) ? 'opacity-50' : ''}">
                
                <div class="text-xs font-bold text-gray-500 mb-2 leading-tight">
                    {tcMapping[konst.constnum]?.übersetzung || tcMapping[konst.constnum]?.key}
                </div>

                <div class="flex items-end gap-1 mt-auto overflow-hidden">
                    <div class="flex items-center border-b border-gray-300 focus-within:border-black transition-colors">
                        <input
                            type="text"
                            inputmode="decimal"
                            class="konst-input min-w-[20px] max-w-full text-sm py-[2px] px-0 leading-5 bg-transparent border-0
                            focus:outline-none focus:ring-0
                            {isKMG(konst.constnum)
                                ? 'text-gray-400'
                                : isDirty(konst)
                                    ? 'text-blue-600'
                                    : 'text-gray-900'}"
                            size={Math.max(1, konst.constvalTemp?.toString().length || 1)}
                            value={konst.constvalTemp}
                            readonly={isKMG(konst.constnum)}
                            on:input={(e) => handleNumberInput(e, konst)}
                            on:keydown={(e) => handleKeyDown(e, konst, index)}
                        />
                        
                        <span class="text-[10px] text-gray-500 ml-1 pb-[2px]">
                            {tcMapping[konst.constnum]?.einheit || ''}
                        </span>
                    </div>

                    {#if isDirty(konst) && !isKMG(konst.constnum)}
                        <button 
                            type="button" 
                            on:click={() => saveConstVal(konst)}
                            class="text-blue-600 shrink-0 mb-[2px] hover:text-blue-800 transition-colors"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </button>
                    {/if}
                </div>
            </div>
        {/each}
    </div>
{/if}