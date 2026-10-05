<script lang="ts">
    import { ROLE_LABELS } from '$lib/roles';
    let { data } = $props();

    const activeUsers = $derived(data.users.filter((u) => u.is_active).length);
    const byRole = $derived(
        Object.entries(
            data.users.reduce<Record<string, number>>((acc, u) => {
                acc[u.role] = (acc[u.role] ?? 0) + 1;
                return acc;
            }, {})
        )
    );

    const card = 'bg-white rounded border p-4';
</script>

<h1 class="text-2xl font-semibold mb-4">
    Übersicht{#if !data.isSuperadmin && data.companyName}&nbsp;– {data.companyName}{/if}
</h1>

<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
    {#if data.isSuperadmin}
        <a href="/admin/firmen" class="{card} hover:border-[#1f3b5e]">
            <div class="text-sm text-gray-500">Firmen</div>
            <div class="text-3xl font-semibold">{data.companies.length}</div>
            <div class="text-xs text-gray-500">{data.companies.filter((c) => c.is_active).length} aktiv</div>
        </a>
    {/if}
    <a href="/admin/nutzer" class="{card} hover:border-[#1f3b5e]">
        <div class="text-sm text-gray-500">Nutzer</div>
        <div class="text-3xl font-semibold">{data.users.length}</div>
        <div class="text-xs text-gray-500">{activeUsers} aktiv</div>
    </a>
    <div class={card}>
        <div class="text-sm text-gray-500 mb-1">Nach Rolle</div>
        {#each byRole as [role, count] (role)}
            <div class="flex justify-between text-sm"><span>{ROLE_LABELS[role] ?? role}</span><span>{count}</span></div>
        {/each}
    </div>
</div>

<div class={card}>
    <h2 class="font-medium mb-3">Schnellzugriff</h2>
    <div class="flex flex-wrap gap-3 text-sm">
        {#if data.isSuperadmin}
            <a href="/admin/firmen#neu" class="px-3 py-2 rounded bg-gray-800 text-white hover:bg-gray-700">+ Neue Firma</a>
        {/if}
        <a href="/admin/nutzer#neu" class="px-3 py-2 rounded bg-gray-800 text-white hover:bg-gray-700">+ Neuer Nutzer</a>
        <a href="/konto" class="px-3 py-2 rounded bg-gray-200 hover:bg-gray-300">Eigenes Passwort ändern</a>
    </div>
</div>
