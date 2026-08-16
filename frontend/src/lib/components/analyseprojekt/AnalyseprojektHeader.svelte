<script lang="ts">
    // ---------------------------------------------------------------
    // Props
    // ---------------------------------------------------------------

    /** Das gesamte analyseprojekt-Objekt (für modell-Infos + fk_modell) */
    export let analyseprojekt: any;

    /** Bindable: name-Feld */
    export let name: string;

    /** Bindable: aenderungszustand-Feld */
    export let aenderungszustand: string;

    /** Bindable: identnr-Feld */
    export let identnr: number | null;

    /** Bindable: remark-Feld */
    export let remark: string;

    /** Bindable: tolfaktor-Checkbox */
    export let tolfaktor: boolean;

    // ---------------------------------------------------------------
    // Modell-Hilfsfunktionen (identisch in beiden Seiten)
    // ---------------------------------------------------------------
    const methodenMap: Record<number, string> = {
        1: 'Direkt',
        2: 'Direkt mit Einstellung',
        3: 'Substitution',
        4: 'Differenziell',
    };

    const geoMap: Record<number, string> = {
        1: 'Fläche',
        2: 'Kugel',
        3: 'Zylinder',
        4: 'Bohrung',
    };

    const aufgabenMap: Record<string, string> = {
        tsk_ausenmessung: 'Außenmessung',
        tsk_innenmessung: 'Innenmessung',
        tsk_tiefenmessung: 'Tiefenmessung',
        tsk_hoehenmessung: 'Höhenmessung',
        tsk_stufenmessung: 'Stufenmessung',
    };

    function getAktiveAufgabe(modell: Record<string, number>): string {
        for (const key in aufgabenMap) {
            if (Number(modell[key]) === 1) return aufgabenMap[key as keyof typeof aufgabenMap];
        }
        return 'Unbekannt';
    }
</script>

<!--
    Das <form>-Element selbst bleibt in der Page, damit der action="?/speichern"
    korrekt auf der jeweiligen Route landet. Der Header-Inhalt wird hier als
    Fragment gerendert und per <slot name="buttons"> um seitenspezifische Buttons
    ergänzt.
-->

<h1 class="text-base font-semibold border-b pb-2">
    Analyseprojekt
    <!-- Seitenspezifische Buttons (Berechnen, Speichern, KMG, Report ...) -->
    <slot name="buttons" />
</h1>

<div class="flex gap-10 justify-between mt-3">
    <!-- Eingabefelder -->
    <div class="grid grid-cols-3 gap-3 border p-4 rounded bg-gray-100 w-2xl">
        <div>
            <label class="block text-gray-700 text-xs mb-1">Name</label>
            <input
                type="text"
                name="name"
                bind:value={name}
                class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white"
            />
        </div>
        <div>
            <label class="block text-gray-700 text-xs mb-1">Änderungszustand</label>
            <input
                type="text"
                name="aenderungszustand"
                bind:value={aenderungszustand}
                class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white"
            />
        </div>
        <div>
            <label class="block text-gray-700 text-xs mb-1">Identnummer</label>
            <input
                type="number"
                name="identnr"
                bind:value={identnr}
                class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white"
            />
        </div>
        <div>
            <label class="block text-gray-700 text-xs mb-1">Sachnummer</label>
            <input
                type="text"
                name="sachnummer"
                value="Sachnummer"
                class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white"
            />
        </div>
        <div>
            <label class="block text-gray-700 text-xs mb-1">Bemerkung</label>
            <input
                type="text"
                name="remark"
                bind:value={remark}
                class="w-full h-6 border border-gray-400 px-2 text-sm py-2 bg-white"
            />
        </div>
        <div class="flex ml-6 items-center space-x-2 mb-1">
            <label for="tolfaktor" class="text-gray-700 text-xs object-bottom">Eignungskennwert</label>
            <input
                type="checkbox"
                name="tolfaktor"
                id="tolfaktor"
                bind:checked={tolfaktor}
                class="h-4 w-4 text-gray-600 border-gray-400 rounded"
            />
        </div>

        <!-- Nur Standard-Analyseprojekt braucht fk_modell im Form.
             Wird per slot optional eingeschleust. -->
        <slot name="hidden-fields" />
    </div>

    <!-- Modellinformationen -->
    <div class="border p-4 rounded bg-gray-50 w-full md:w-1/2 space-y-2">
        <h2 class="text-sm font-semibold border-b pb-1 text-gray-800">
            {analyseprojekt.modell.name}
        </h2>
        <div class="text-gray-800 text-sm space-y-1">
            <div><span class="font-semibold">Aufgabe:</span> {getAktiveAufgabe(analyseprojekt.modell)}</div>
            <div><span class="font-semibold">Methode:</span> {methodenMap[analyseprojekt.modell.methode]}</div>
            <div><span class="font-semibold">Messobjekt:</span> {geoMap[analyseprojekt.modell.geo_mo]}</div>
            <div><span class="font-semibold">Messeinrichtung:</span> {geoMap[analyseprojekt.modell.geo_me]}</div>
        </div>
    </div>
</div>
