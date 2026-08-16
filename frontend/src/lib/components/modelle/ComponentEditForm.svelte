<script lang="ts">
    export let mode: 'standard' | '3d' = 'standard';
    export let data: { component: any, texts: any[] };
    import { Components } from '$lib/Mapping';
    $: textOptions = [
        { value: 0, label: '' },
        ...(Array.isArray(data?.texts) ? data.texts.map(t => ({
            value: t.id,
            label: t.deutsch ?? `Text ${t.id}`
        })) : [])
    ];

    const comp = data.component;

    let terml0: number = comp.terml0 ?? 0;
    let terml1: number = comp.terml1 ?? 0;
    let wertart: string = comp.wertart != null ? comp.wertart.toString() : '';
    let freigrad: string = comp.freigrad != null ? comp.freigrad.toString() : '';
    let frei_n_1: number = comp.frei_n_1 ?? 0;
    let verteilung: string = comp.verteilung != null ? comp.verteilung.toString() : '';
    let messpunkt_anzahl: number = comp.messpunkt_anzahl ?? '';
    let anzahl_messungen: number = comp.anzahl_messungen ?? '';
    $: methodeA = wertart === '4';
    let kflags: number = comp.kflags ?? 0;
    let modltxtid: number | null = comp.modltxtid ?? 0;

    function formatNumber(val: any) {
        if (val === null || val === undefined || val === '') return '';
        return val.toString().replace('.', ',');
    }

    function handleNumberInput(e: Event, field: 'terml0' | 'terml1') {
        const v = (e.target as HTMLInputElement).value;
        if (field === 'terml0') terml0 = v as any;
        else terml1 = v as any;
    }

    function handleBlur(field: 'terml0' | 'terml1') {
        const val = field === 'terml0' ? terml0 : terml1;
        if (val !== null && val !== '' && !isNaN(Number(String(val).replace(',', '.')))) {
            const num = parseFloat(String(val).replace(',', '.'));
            if (field === 'terml0') terml0 = num as any;
            else terml1 = num as any;
        }
    }

    const fieldClass = "w-full pr-10 text-sm py-[2px] leading-5 bg-transparent border-0 border-b border-gray-300 focus:outline-none focus:ring-0 focus:border-[#1f3b5e]";
    const labelClass = "text-xs font-medium text-[#2B6CB0]";
    </script>

<form method="POST" class="text-sm bg-white">
<div class="px-2 py-1 -mx-2 -mt-4 mb-3">
    <h2 style="color: #1f3b5e;" class="font-semibold text-base">
        {Components[comp.kompid] ?? comp.kompid}
    </h2>
</div>

    <div class="space-y-2 px-1">
        <div class="bg-gray-50 rounded p-3 grid grid-cols-2 gap-x-6 gap-y-4">
            {#if mode === 'standard'}
                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Term L0</span>
                    <div class="relative">
                        <input type="text" inputmode="decimal" name="terml0"
                            value={formatNumber(terml0)}
                            on:input={(e) => handleNumberInput(e, 'terml0')}
                            on:blur={() => handleBlur('terml0')}
                            class={fieldClass} />
                        <span class="absolute right-1 top-1/2 -translate-y-1/2 text-gray-400 text-xs pointer-events-none">µm</span>
                    </div>
                </label>

                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Term L1</span>
                    <div class="relative">
                        <input type="text" inputmode="decimal" name="terml1"
                            value={formatNumber(terml1)}
                            on:input={(e) => handleNumberInput(e, 'terml1')}
                            on:blur={() => handleBlur('terml1')}
                            class={fieldClass} />
                        <span class="absolute right-1 top-1/2 -translate-y-1/2 text-gray-400 text-xs pointer-events-none"></span>
                    </div>
                </label>

                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Verteilung</span>
                    <select name="verteilung" bind:value={verteilung} required class={fieldClass}>
                        <option value="" disabled selected>Bitte wählen</option>
                        <option value="1">Rechteckverteilung</option>
                        <option value="2">Normalverteilung</option>
                        <option value="3">Dreieckverteilung</option>
                    </select>
                </label>

                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Freiheitsgrad</span>
                    <select name="freigrad" bind:value={freigrad} required class={fieldClass}>
                        <option value="" disabled selected>Bitte wählen</option>
                        <option value="1">Unbegrenzt</option>
                        <option value="2">N-1</option>
                    </select>
                </label>

                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Frei n-1</span>
                    <input type="number" name="frei_n_1" bind:value={frei_n_1} class={fieldClass} />
                </label>

                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Wertart</span>
                    <select name="wertart" bind:value={wertart} required class={fieldClass}>
                        <option value="" disabled selected>Bitte wählen</option>
                        <option value="1">Halbweite</option>
                        <option value="2">Spannweite</option>
                        <option value="3">Standardabweichung</option>
                    </select>
                </label>

            {:else}
                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Methode</span>
                    <select name="wertart" bind:value={wertart} class={fieldClass}>
                        <option value="" disabled>Bitte wählen</option>
                        <option value="4">A</option>
                        <option value="5">B</option>
                    </select>
                </label>

                <label class="flex flex-col gap-1">
                    <span class={labelClass}>Anzahl Messpunkte</span>
                    <input type="number" name="messpunkt_anzahl" bind:value={messpunkt_anzahl} step="any" class={fieldClass} />
                </label>

                {#if methodeA}
                    <label class="flex flex-col gap-1">
                        <span class={labelClass}>Anzahl Messungen</span>
                        <input type="number" name="anzahl_messungen" bind:value={anzahl_messungen} step="any" class={fieldClass} />
                    </label>
                {/if}
            {/if}

            <label class="flex flex-col gap-1">
                <span class={labelClass}>Häufigkeit</span>
                <input type="number" name="kflags" bind:value={kflags} class={fieldClass} />
            </label>
        </div>

        {#if mode === '3d'}
            <div class="bg-gray-50 rounded p-3">
                <label class="flex flex-col gap-1">
                    <span class={labelClass}>
                        {methodeA ? 'Standardabweichung der Messreihe' : 'Standardabweichung am Ausgleichselement'}
                    </span>
                    <div class="relative">
                        <input type="text" inputmode="decimal" name="terml1"
                            value={formatNumber(terml1)}
                            on:input={(e) => handleNumberInput(e, 'terml1')}
                            on:blur={() => handleBlur('terml1')}
                            class={fieldClass} />
                        <span class="absolute right-1 top-1/2 -translate-y-1/2 text-gray-400 text-xs pointer-events-none">µm</span>
                    </div>
                </label>
            </div>
        {/if}

        <div class="bg-gray-50 rounded p-3">
            <label class="flex flex-col gap-1">
                <span class={labelClass}>Beschreibung</span>
                <select name="modltxtid" bind:value={modltxtid} class={fieldClass}>
                    {#each textOptions as opt}
                        <option value={opt.value}>{opt.label}</option>
                    {/each}
                </select>
            </label>
        </div>

        <div class="flex justify-end pt-1 pb-1">
            <button type="submit"
                class="text-white text-sm px-5 py-1.5 rounded"
                style="background-color: #1f3b5e;"
            >
                Speichern
            </button>
        </div>
    </div>
</form>