<script lang="ts">
    let { data } = $props();

    const projektLink = (p: { id: number; modell: { aufgabe_modell: number | null } }) =>
        p.modell?.aufgabe_modell === 3 ? `/analyseprojekt/3D-${p.id}` : `/analyseprojekt/${p.id}`;

    function datum(iso: string | null) {
        if (!iso) return '';
        const d = new Date(iso);
        return isNaN(d.getTime())
            ? ''
            : d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) +
                  ', ' + d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
    }

    const tageszeit = (() => {
        const h = new Date().getHours();
        return h < 11 ? 'Guten Morgen' : h < 18 ? 'Guten Tag' : 'Guten Abend';
    })();

    const card = 'block bg-white rounded border p-4 hover:border-[#1f3b5e] hover:shadow-sm transition';
    const action = 'inline-flex items-center gap-1 px-4 py-2 rounded text-sm';
</script>

<div class="max-w-6xl mx-auto mt-6 space-y-6">
    <div>
        <h1 class="text-2xl font-semibold">{tageszeit}{data.me ? `, ${data.me.username}` : ''}</h1>
        {#if data.me?.company_name}
            <p class="text-sm text-gray-500">{data.me.company_name}</p>
        {/if}
    </div>

    <!-- Kennzahlen -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <a href="/analyseprojekt" class={card}>
            <div class="text-sm text-gray-500">Analyseprojekte</div>
            <div class="text-3xl font-semibold">{data.anzahl.projekte}</div>
        </a>
        <a href="/modelle" class={card}>
            <div class="text-sm text-gray-500">Modelle</div>
            <div class="text-3xl font-semibold">{data.anzahl.modelle}</div>
            {#if data.anzahl.eingebaut}
                <div class="text-xs text-gray-500">davon {data.anzahl.eingebaut} vorgegeben</div>
            {/if}
        </a>
        <div class="bg-white rounded border p-4">
            <div class="text-sm text-gray-500">Koordinatenmessgeräte (KMG)</div>
            <div class="text-3xl font-semibold">{data.anzahl.kmgs}</div>
        </div>
    </div>

    <!-- Schnellzugriff (nicht für "Nur lesen") -->
    {#if data.user?.role !== 'readonly'}
    <div class="flex flex-wrap gap-3">
        <a href="/analyseprojekt?open=neu" class="{action} bg-[#1f3b5e] text-white hover:bg-[#2a4d7a]">+ Neues Analyseprojekt</a>
        <a href="/modelle?neu=1" class="{action} bg-white border hover:bg-gray-50">+ Neues Modell</a>
        <a href="/import" class="{action} bg-white border hover:bg-gray-50">XML importieren</a>
    </div>
    {/if}

    <!-- Zuletzt bearbeitet -->
    <section class="bg-white rounded border">
        <div class="px-4 py-2 border-b bg-gray-50 font-medium">Zuletzt bearbeitete Analyseprojekte</div>
        {#if data.zuletzt.length}
            <ul class="divide-y text-sm">
                {#each data.zuletzt as p (p.id)}
                    <li>
                        <a href={projektLink(p)} class="flex items-center justify-between px-4 py-2 hover:bg-gray-50">
                            <span>
                                <span class="font-medium">{p.name}</span>
                                <span class="text-gray-500"> · {p.modell?.name}</span>
                            </span>
                            <span class="text-xs text-gray-500">{datum(p.modify ?? p.creation)}</span>
                        </a>
                    </li>
                {/each}
            </ul>
        {:else}
            <p class="px-4 py-6 text-sm text-gray-500">
                Noch keine Analyseprojekte.
                <a href="/analyseprojekt?open=neu" class="text-blue-600 hover:underline">Erstes Projekt anlegen</a>
            </p>
        {/if}
    </section>
</div>
