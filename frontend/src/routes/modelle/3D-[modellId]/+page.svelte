<script lang="ts">
    import {goto, preloadData, pushState} from "$app/navigation";
    import {page} from '$app/stores';
    import Modal from "$lib/components/Modal.svelte";
    import NewCompPage from "../3D-[modellId]/addComponent/+page.svelte";
    import CompInfoPage from '../3D-[modellId]/component-[componentId]/+page.svelte';
    import {COMPONENTS, Components, prozessMapping} from "$lib/Mapping.js";
    import ComponentTable from '$lib/components/modelle/ComponentTable.svelte';
    import ModellRightPanel from '$lib/components/modelle/ModellRightPanel.svelte';
    import EditToggle from '$lib/components/modelle/EditToggle.svelte';
    export let data;
    let editable = !data.modell.is_builtin;

import { browser } from '$app/environment';

import { onMount } from 'svelte';

onMount(async () => {
    if (aufgabe && (!data.modell.components || data.modell.components.length === 0)) {
        await saveModell();
    }
});
// Reaktiv bei jeder Änderung speichern
$: if (browser) {
    sessionStorage.setItem('pendingModellData', JSON.stringify({
        name, Element1, Element2, Bezug1, Bezug2,
        aufgabe, aufgabe_modell, taster, merkmal, element,
        punktmusterB1, tasterschaft1, tasterschaft2, artdesmasses,
        punktmusterR1, punktmusterR2, taster1, taster2,
        abstand, winkelE1, winkelE2,
        punktmuster: punktmuster ? parseInt(punktmuster) : null,
        description, formel, formeldesc
    }));
}

$: if (form?.code === 'FK_IN_USE') {
    if (browser) {
        const saved = sessionStorage.getItem('pendingModellData');
        if (saved) {
            const parsed = JSON.parse(saved);
            name = parsed.name;
            Element1 = parsed.Element1;
            Element2 = parsed.Element2;
            Bezug1 = parsed.Bezug1;
            Bezug2 = parsed.Bezug2;
            aufgabe = parsed.aufgabe;
            taster = parsed.taster;
            merkmal = parsed.merkmal;
            element = parsed.element;
            punktmusterB1 = parsed.punktmusterB1;
            tasterschaft1 = parsed.tasterschaft1;
            tasterschaft2 = parsed.tasterschaft2;
            artdesmasses = parsed.artdesmasses;
            punktmusterR1 = parsed.punktmusterR1;
            punktmusterR2 = parsed.punktmusterR2;
            taster1 = parsed.taster1;
            taster2 = parsed.taster2;
            abstand = parsed.abstand;
            winkelE1 = parsed.winkelE1;
            winkelE2 = parsed.winkelE2;
            punktmuster = parsed.punktmuster?.toString() ?? null;
            description = parsed.description;
            formel = parsed.formel;
            formeldesc = parsed.formeldesc;
        }
    }
    conflictCount = form.count ?? 0;
    showConflictDialog = true;
}


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

    $: fieldClass = `w-full h-6 border border-gray-400 px-2 text-sm py-0 ${editable ? 'bg-white' : 'bg-gray-50 cursor-not-allowed opacity-60'}`;
    $: inputClass = `w-full h-6 border border-gray-400 px-2 text-sm py-2 ${editable ? 'bg-white' : 'bg-gray-50 cursor-not-allowed opacity-60'}`;

export let form: {
    success?: boolean;
    message?: string;
    error?: string;
    code?: string;
    count?: number;
} | null = null;
let showConflictDialog = false;
let conflictCount = 0;

$: if (form?.code === 'FK_IN_USE') {
    conflictCount = form.count ?? 0;
    showConflictDialog = true;
}
    $: modellId = $page.params.modellId;
    $: componentDialogOpen = !!$page.state?.newComponent;
    $: showComponent = !!$page.state?.componentInfo;
function buildPayload(formEl: HTMLFormElement) {
    const formData = new FormData(formEl);

    function parseOptionalInt(key: string): number | undefined {
        const value = formData.get(key);
        if (value === null || value === '') return undefined;
        const parsed = parseInt(value.toString());
        return isNaN(parsed) ? undefined : parsed;
    }

    function parseOptionalString(key: string): string | undefined {
        const value = formData.get(key);
        if (value === null || value === '') return undefined;
        return value.toString();
    }

    const payload: Record<string, any> = {};

    const name = parseOptionalString('name');
    if (name !== undefined) payload.name = name;

    payload.tsk_ausenmessung = formData.has('tsk_ausenmessung') ? 1 : 0;
    payload.tsk_innenmessung = formData.has('tsk_innenmessung') ? 1 : 0;
    payload.tsk_tiefenmessung = formData.has('tsk_tiefenmessung') ? 1 : 0;
    payload.tsk_hoehenmessung = formData.has('tsk_hoehenmessung') ? 1 : 0;
    payload.tsk_stufenmessung = formData.has('tsk_stufenmessung') ? 1 : 0;

    const aufgabe_modell = parseOptionalInt('aufgabe_modell');
    if (aufgabe_modell !== undefined) payload.aufgabe_modell = aufgabe_modell;

    const aufgabe = parseOptionalInt('aufgabe');
    if (aufgabe !== undefined) payload.aufgabe = aufgabe;

    const bezug1 = parseOptionalString('Bezug1');
    if (bezug1 !== undefined) payload.Bezug1 = bezug1;

    const bezug2 = parseOptionalString('Bezug2');
    if (bezug2 !== undefined) payload.Bezug2 = bezug2;

    const element1 = parseOptionalString('Element1');
    if (element1 !== undefined) payload.Element1 = element1;

    const element2 = parseOptionalString('Element2');
    if (element2 !== undefined) payload.Element2 = element2;

    const punktmuster = parseOptionalInt('punktmuster');
    if (punktmuster !== undefined) payload.punktmuster = punktmuster;

    const description = parseOptionalString('description');
    if (description !== undefined) payload.description = description;

    const formel = parseOptionalString('formel');
    if (formel !== undefined) payload.formel = formel;

    const formeldesc = parseOptionalString('formeldesc');
    if (formeldesc !== undefined) payload.formeldesc = formeldesc;

    const optionalIntFields = [
        'taster', 'merkmal', 'element',
        'punktmusterB1', 'tasterschaft1', 'tasterschaft2', 'artdesmasses',
        'punktmusterR1', 'punktmusterR2', 'taster1', 'taster2',
        'abstand', 'winkelE1', 'winkelE2'
    ];
    for (const key of optionalIntFields) {
        const val = parseOptionalInt(key);
        if (val !== undefined) payload[key] = val;
    }

    return payload;
}

async function createCopy() {
    
    const copyRes = await fetch(`/backend/modells/${data.modellId}/copy`, {
        method: 'POST',
        credentials: 'include'
    });
    if (!copyRes.ok) {
        alert('Fehler beim Erstellen der Kopie');
        return;
    }
    const copyJson = await copyRes.json();
    const newId = copyJson.new_id;

    // Direkt Svelte-Variablen nutzen statt FormData
    const payload: Record<string, any> = {
        name,
        aufgabe_modell,
        aufgabe,
        description,
        formel,
        formeldesc,
        Element1,
        Element2,
        Bezug1,
        Bezug2,
        punktmuster: punktmuster ? parseInt(punktmuster) : undefined,
        taster,
        merkmal,
        element,
        punktmusterB1,
        tasterschaft1,
        tasterschaft2,
        artdesmasses,
        punktmusterR1,
        punktmusterR2,
        taster1,
        taster2,
        abstand,
        winkelE1,
        winkelE2,
    };

    // null/undefined rausfiltern
    Object.keys(payload).forEach(k => {
        if (payload[k] === undefined || payload[k] === null) delete payload[k];
    });

    const saveRes = await fetch(`/backend/modells/${newId}/r`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
    });

    if (!saveRes.ok) {
        alert('Kopie erstellt, aber Änderungen konnten nicht gespeichert werden');
    }

    showConflictDialog = false;
    // sessionStorage leeren bevor wir navigieren
    if (browser) sessionStorage.removeItem('pendingModellData');
    
    goto(`/modelle/3D-${newId}`);
}
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
    console.log('preload result:', result.data); // texts drin?
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



onMount(() => {
    const added = $page.url.searchParams.get('added');
    if (added) {
        showToast('Komponente wurde hinzugefügt');
        history.replaceState({}, '', window.location.pathname);
    }
    const edited = $page.url.searchParams.get('edited');
    if (edited) {
        showToast('Komponente wurde aktualisiert');
        history.replaceState({}, '', window.location.pathname);
    }
});
    async function deleteComponent(compId: number) {
    const confirmed = confirm("Möchtest du diese Komponente wirklich löschen?");
    if (!confirmed) return;
    try {
        const res = await fetch(`/backend/components/${compId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Fehler beim Löschen der Komponente');
        data.modell.components = data.modell.components.filter((c: any) => c.id !== compId);
        showToast('Komponente wurde gelöscht');
    } catch (err) {
        console.error(err);
        showToast('Löschen fehlgeschlagen', 'error');
    }
}
let toast: { message: string; type: 'success' | 'error' } | null = null;
let toastTimeout: ReturnType<typeof setTimeout>;

function showToast(message: string, type: 'success' | 'error' = 'success') {
    toast = { message, type };
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast = null, 3000);
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
        const res = await fetch(`/backend/modells/${modellId}/alterModell`, {
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
let showSaveMenu = false;

import { hasUnsavedChanges } from '$lib/stores/unsaved';
import { beforeNavigate } from '$app/navigation';

let showUnsavedDialog = false;
let pendingNavigation: (() => void) | null = null;

let isSaving = false;

let originalData = {
    name: data.modell?.name ?? '',
    aufgabe: data.modell?.aufgabe != null ? data.modell.aufgabe.toString() : null,
    Element1: data.modell?.Element1 ?? null,
    Element2: data.modell?.Element2 ?? null,
    Bezug1: data.modell?.Bezug1 ?? null,
    Bezug2: data.modell?.Bezug2 ?? null,
    abstand: data.modell?.abstand != null ? data.modell.abstand.toString() : null,
    taster: data.modell?.taster != null ? data.modell.taster.toString() : null,
    merkmal: data.modell?.merkmal != null ? data.modell.merkmal.toString() : null,
    element: data.modell?.element != null ? data.modell.element.toString() : null,
    punktmuster: data.modell?.punktmuster != null ? data.modell.punktmuster.toString() : null,
    punktmusterB1: data.modell?.punktmusterB1 != null ? data.modell.punktmusterB1.toString() : null,
    punktmusterR1: data.modell?.punktmusterR1 != null ? data.modell.punktmusterR1.toString() : null,
    punktmusterR2: data.modell?.punktmusterR2 != null ? data.modell.punktmusterR2.toString() : null,
    tasterschaft1: data.modell?.tasterschaft1 != null ? data.modell.tasterschaft1.toString() : null,
    tasterschaft2: data.modell?.tasterschaft2 != null ? data.modell.tasterschaft2.toString() : null,
    taster1: data.modell?.taster1 != null ? data.modell.taster1.toString() : null,
    taster2: data.modell?.taster2 != null ? data.modell.taster2.toString() : null,
    winkelE1: data.modell?.winkelE1 != null ? data.modell.winkelE1.toString() : null,
    winkelE2: data.modell?.winkelE2 != null ? data.modell.winkelE2.toString() : null,
    description: data.modell?.description ?? '',
    formel: data.modell?.formel ?? '',
    formeldesc: data.modell?.formeldesc ?? '',
};
let originalComponents = JSON.stringify(data.modell?.components ?? []);

hasUnsavedChanges.set(false);

$: hasUnsavedChanges.set(
    name !== originalData.name ||
    (aufgabe?.toString() ?? null) !== originalData.aufgabe ||
    Element1 !== originalData.Element1 ||
    Element2 !== originalData.Element2 ||
    Bezug1 !== originalData.Bezug1 ||
    Bezug2 !== originalData.Bezug2 ||
    (abstand?.toString() ?? null) !== originalData.abstand ||
    (taster?.toString() ?? null) !== originalData.taster ||
    (merkmal?.toString() ?? null) !== originalData.merkmal ||
    (element?.toString() ?? null) !== originalData.element ||
    (punktmuster?.toString() ?? null) !== originalData.punktmuster ||
    (punktmusterB1?.toString() ?? null) !== originalData.punktmusterB1 ||
    (punktmusterR1?.toString() ?? null) !== originalData.punktmusterR1 ||
    (punktmusterR2?.toString() ?? null) !== originalData.punktmusterR2 ||
    (tasterschaft1?.toString() ?? null) !== originalData.tasterschaft1 ||
    (tasterschaft2?.toString() ?? null) !== originalData.tasterschaft2 ||
    (taster1?.toString() ?? null) !== originalData.taster1 ||
    (taster2?.toString() ?? null) !== originalData.taster2 ||
    (winkelE1?.toString() ?? null) !== originalData.winkelE1 ||
    (winkelE2?.toString() ?? null) !== originalData.winkelE2 ||
    description !== originalData.description ||
    formel !== originalData.formel ||
    formeldesc !== originalData.formeldesc ||
    JSON.stringify(data.modell?.components ?? []) !== originalComponents
);

$: if (form?.success) {
    originalData = {
        name,
        aufgabe: aufgabe?.toString() ?? null,
        Element1, Element2, Bezug1, Bezug2,
        abstand: abstand?.toString() ?? null,
        taster: taster?.toString() ?? null,
        merkmal: merkmal?.toString() ?? null,
        element: element?.toString() ?? null,
        punktmuster: punktmuster?.toString() ?? null,
        punktmusterB1: punktmusterB1?.toString() ?? null,
        punktmusterR1: punktmusterR1?.toString() ?? null,
        punktmusterR2: punktmusterR2?.toString() ?? null,
        tasterschaft1: tasterschaft1?.toString() ?? null,
        tasterschaft2: tasterschaft2?.toString() ?? null,
        taster1: taster1?.toString() ?? null,
        taster2: taster2?.toString() ?? null,
        winkelE1: winkelE1?.toString() ?? null,
        winkelE2: winkelE2?.toString() ?? null,
        description, formel, formeldesc,
    };
    originalComponents = JSON.stringify(data.modell?.components ?? []);
    hasUnsavedChanges.set(false);
}

beforeNavigate(({ cancel, to }) => {
    if (isSaving) return;
    if ($hasUnsavedChanges) {
        cancel();
        showUnsavedDialog = true;
        pendingNavigation = () => {
            hasUnsavedChanges.set(false);
            if (to?.url) window.location.href = to.url.href;
        };
    }
});
async function handleSubmit(actionValue: string) {
    isSaving = true;
    hasUnsavedChanges.set(false);
    const formEl = document.querySelector('form') as HTMLFormElement;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'action';
    input.value = actionValue;
    formEl.appendChild(input);
    formEl.submit();
}
</script>
<svelte:window on:click={(e) => {
    if (showSaveMenu && !(e.target as HTMLElement).closest('.relative')) {
        showSaveMenu = false;
    }
}}/>
{#if showConflictDialog}
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-lg p-6 w-96 space-y-3">
      <h2 class="text-base font-semibold text-gray-800">Modell wird verwendet</h2>
      <p class="text-sm text-gray-600">
        Dieses Modell wird in <strong>{conflictCount}</strong>
        {conflictCount === 1 ? 'Datensatz' : 'Datensätzen'} verwendet
        und kann nicht geändert werden.
      </p>
      <p class="text-sm text-gray-600">
        Möchtest du stattdessen eine Kopie erstellen und diese bearbeiten?
      </p>
      <div class="flex gap-2 pt-2">
        <button
          on:click={createCopy}
          class="flex-1 bg-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-800"
        >
          Kopie erstellen
        </button>
        <button
          on:click={() => showConflictDialog = false}
          class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 rounded hover:bg-gray-100"
        >
          Abbrechen
        </button>
      </div>
    </div>
  </div>
{/if}
<section class="w-8xl space-y-4 text-sm font-sans text-gray-800 m-auto pt-5">
    <form method="POST" class="max-w-8xl space-y-6">
    <!-- Titel -->
        <input type="number" name="aufgabe" bind:value={data.modell.aufgabe} hidden disabled={!editable} class={inputClass} />
        <input type="number" name="aufgabe_modell" hidden bind:value={data.modell.aufgabe_modell} disabled={!editable} class={inputClass} />

<h1 class="text-base font-semibold border-b pb-2">{prozesstitel}: {prozessMapping[data.modell.aufgabe]}
    <div class="float-right flex">
        <button type="submit" name="action" value="save" disabled={data.modell.is_builtin}
            on:click={() => handleSubmit('save')} class="disabled:opacity-40 disabled:cursor-not-allowed bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700">
            Speichern
        </button>
        <div class="relative">
            <button type="button"
                disabled={data.modell.is_builtin}
                on:click={() => showSaveMenu = !showSaveMenu}
                class="disabled:opacity-40 disabled:cursor-not-allowed bg-gray-600 text-white text-sm px-2 py-1 rounded-r border-l border-gray-500 hover:bg-gray-700">
                ▾
            </button>
            {#if showSaveMenu}
                <div class="absolute right-0 mt-1 bg-white border border-gray-200 rounded shadow-lg z-50 w-44">
                    <button type="button" on:click={() => { showSaveMenu = false; handleSubmit('continue'); }}
                        class="bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700">
                        Speichern & Schließen
                    </button>
                    <button type="button" on:click={() => { showSaveMenu = false; handleSubmit('close'); }}
                        class="bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700">
                        Speichern & Weiter
                    </button>
                </div>
            {/if}
        </div>
    </div>
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
                    <input type="text" name="name" bind:value={name} disabled={!editable} class={inputClass} />
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster</label>
                        <select id="taster" name="taster" bind:value={taster}  disabled={!editable} on:change={saveModell} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>derselbe Taster</option>
                            <option value={2}>verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  disabled={!editable} class={fieldClass}>
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
                        <select id="Element2" name="Element2" bind:value={Element2} on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                    <input type="text" name="name" bind:value={name} disabled={!editable} class={inputClass} />

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select id="Element1" name="Element1" bind:value={Element1} on:change={saveModell} disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug 1</label>
                        <select id="Bezug1" name="Bezug1" bind:value={Bezug1} on:change={saveModell} disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Gerade">Gerade</option>
                            <option value="Ebene">Ebene</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Punktmuster</label>
                        <select id="punktmuster" name="punktmuster" bind:value={punktmuster} on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                    <input type="text" name="name" bind:value={name} disabled={!editable} class={inputClass} />

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element</label>
                        <select id="element" name="element" bind:value={element} on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                        <select id="merkmal" name="merkmal" bind:value={merkmal} on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                        <input type="text" name="name" bind:value={name} disabled={!editable} class={inputClass} />
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster</label>
                        <select id="taster" name="taster" bind:value={taster} on:change={saveModell} disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>derselbe Taster</option>
                            <option value={2}>verschiedene Taster</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element</label>
                        <select id="Element1" name="Element1" bind:value={Element1} on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                            <select id="punktmuster" name="punktmuster" bind:value={punktmuster} on:change={saveModell} disabled={!editable} class={fieldClass}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value=1>gleichmäßig verteilt</option>
                                <option value=2>zwei Radialschnitte</option>
                            </select>
                        </div>
                    {/if}
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug1</label>
                        <select id="Bezug1" name="Bezug1" bind:value={Bezug1} on:change={saveModell} disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    {#if showPunktmuster1}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Punktmuster 1</label>
                            <select id="punktmusterB1" name="punktmusterB1" bind:value={punktmusterB1} on:change={saveModell} disabled={!editable} class={fieldClass}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>gleichmäßig verteilt</option>
                                <option value={2}>zwei Radialschnitte</option>
                            </select>
                        </div>
                    {/if}
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Bezug2</label>
                        <select id="Bezug2" name="Bezug2" bind:value={Bezug2} on:change={saveModell} disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value=0>-</option>
                            <option value="Kreis">Kreis</option>
                            <option value="Zylinder">Zylinder</option>
                            <option value="Kegel">Kegel</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Tasterschaft 1</label>
                        <select id="tasterschaft1" name="tasterschaft1" bind:value={tasterschaft1} on:change={saveModell} disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>senkrecht</option>
                            <option value={2}>parallel zu Auswerterichtung</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Tasterschaft 2</label>
                        <select id="tasterschaft2" name="tasterschaft2" bind:value={tasterschaft2} on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                        <input type="text" name="name" bind:value={name} disabled={!editable} class={inputClass} />
                    </div>
                    <!-- Merkmal (immer sichtbar) -->
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Merkmal</label>
                        <select id="merkmal" name="merkmal" bind:value={merkmal} on:change={saveModell}
                                disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>Parallelität</option>
                            <option value={2}>Rechtwinkligkeit</option>
                            <option value={3}>Neigung</option>
                        </select>
                    </div>

                    <!-- Element 1 (immer sichtbar) -->
                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select bind:value={Element1} id="Element1" name="Element1" disabled={!editable} on:change={saveModell} class={fieldClass}>
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
                        <select bind:value={Bezug1} id="Bezug1" name="Bezug1" disabled={!editable} on:change={saveModell} class={fieldClass}>
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
                            <select bind:value={punktmusterR1} id="punktmusterR1" name="punktmusterR1" on:change={saveModell}
                                    disabled={!editable} class={fieldClass}>
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
                            <select bind:value={Element2} id="Element2" name="Element2" on:change={saveModell}
                                    disabled={!editable} class={fieldClass}>
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
                            <select bind:value={taster1} id="taster1" name="taster1" on:change={saveModell}
                                    disabled={!editable} class={fieldClass}>
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
                            <select bind:value={punktmusterR2} id="punktmusterR2" name="punktmusterR2" on:change={saveModell}
                                    disabled={!editable} class={fieldClass}>
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
                            <select bind:value={Bezug2} id="Bezug2" name="Bezug2" on:change={saveModell}
                                    disabled={!editable} class={fieldClass}>
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
                            <select bind:value={taster2} id="taster2" name="taster2" on:change={saveModell}
                                    disabled={!editable} class={fieldClass}>
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
                               disabled={!editable} class={inputClass} />
                    </div>

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element 1</label>
                        <select bind:value={Element1} id="Element1" name="Element1" on:input={saveModell}
                                disabled={!editable} class={fieldClass}>
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
                                disabled={!editable} class={fieldClass}>
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
                                disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>in der Nullebene des Koordinatensystems</option>
                            <option value={2}>im Schwerpunkt</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Taster</label>
                        <select bind:value={taster} id="taster" name="taster" on:change={saveModell}
                                disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value={1}>derselbe Taster</option>
                            <option value={2}>verschiedene Taster</option>
                        </select>
                    </div>

                    {#if showWinkelE1}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Winkel zu Element 1</label>
                            <select bind:value={winkelE1} id="winkelE1" name="winkelE1" on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                            <select bind:value={winkelE2} id="winkelE2" name="winkelE2" on:change={saveModell} disabled={!editable} class={fieldClass}>
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
                            <select bind:value={tasterschaft1} id="tasterschaft1" on:change={saveModell} name="tasterschaft1" disabled={!editable} class={fieldClass}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>senkrecht</option>
                                <option value={2}>parallel zu Auswerterichtung</option>
                            </select>
                        </div>
                    {/if}

                    {#if showTasterschaft2}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Tasterschaft 2</label>
                            <select bind:value={tasterschaft2} id="tasterschaft2" on:change={saveModell} name="tasterschaft2" disabled={!editable} class={fieldClass}>
                                <option value="" disabled>Bitte wählen</option>
                                <option value={1}>senkrecht</option>
                                <option value={2}>parallel zu Auswerterichtung</option>
                            </select>
                        </div>
                    {/if}

                    {#if showArtDesMasses}
                        <div>
                            <label class="block text-gray-700 text-xs mb-1">Art des Maßes</label>
                            <select bind:value={artdesmasses} id="artdesmasses" on:change={saveModell} name="artdesmasses" disabled={!editable} class={fieldClass}>
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
                    <input type="text" name="name" bind:value={name} disabled={!editable} class={inputClass} />

                    <div>
                        <label class="block text-gray-700 text-xs mb-1">Element</label>
                        <select id="Element1" name="Element1" bind:value={Element1}  disabled={!editable} class={fieldClass}>
                            <option value="" disabled>Bitte wählen</option>
                            <option value='Kreis'>Kreis</option>
                            <option value='Halbkugel'>Halbkugel</option>
                            <option value='Zylinder'>Zylinder</option>
                        </select>
                    </div>
                </div>
            {/if}
        </div>
        <ModellRightPanel
  bind:description
  bind:formel
  bind:formeldesc
  {editable}
/>
    </div>

    <!-- Komponentenliste -->
    <ComponentTable
  components={data.modell.components}
  {editable}
  on:addComponent={onNewComponentClick}
  on:openComponent={(e) => onOpenComponent(e.detail.event, e.detail.compId)}
  on:deleteComponent={(e) => deleteComponent(e.detail)}
/>
    </form>
    {#if toast}
    <div class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded shadow-lg text-sm text-white transition-all
        {toast.type === 'success' ? 'bg-[#1f3b5e]' : 'bg-red-600'}">
        {toast.message}
    </div>
{/if}

{#if showUnsavedDialog}
    <div class="fixed inset-0 flex items-center justify-center z-50" style="background: rgba(0,0,0,0.45);">
        <div class="bg-white rounded-lg shadow-xl w-[400px] overflow-hidden">
            <div class="px-5 py-4" style="background-color: #1f3b5e;">
                <h2 class="text-white font-semibold text-base">Ungespeicherte Änderungen</h2>
            </div>
            <div class="px-5 py-4 space-y-2">
                <p class="text-sm text-gray-700">
                    Es gibt ungespeicherte Änderungen. Möchtest du die Seite wirklich verlassen?
                </p>
                <p class="text-xs text-gray-500">
                    Alle nicht gespeicherten Änderungen gehen verloren.
                </p>
            </div>
            <div class="px-5 py-3 flex justify-end gap-2 border-t border-gray-200" style="background-color: #f0f0f0;">
                <button
                    on:click={() => {
                        showUnsavedDialog = false;
                        pendingNavigation = null;
                    }}
                    class="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-200 transition"
                >
                    Abbrechen
                </button>
                <button
                    on:click={() => {
                        showUnsavedDialog = false;
                        pendingNavigation?.();
                        pendingNavigation = null;
                    }}
                    class="px-4 py-1.5 text-sm text-white rounded transition"
                    style="background-color: #1f3b5e;"
                >
                    Trotzdem verlassen
                </button>
            </div>
        </div>
    </div>
{/if}
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