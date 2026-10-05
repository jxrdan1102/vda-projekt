<script lang="ts">
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
    import { ROLE_LABELS, type AdminUser } from '$lib/roles';

    let { data, form } = $props();

    // Rollen, die der angemeldete Nutzer vergeben darf (Backend prüft das zusätzlich)
    const assignableRoles = $derived(
        data.isSuperadmin ? ['user', 'readonly', 'admin', 'superadmin'] : ['user', 'readonly']
    );

    // Firmenfilter steht in der URL (?firma=ID), damit Links aus der Firmenliste funktionieren
    const companyFilter = $derived(page.url.searchParams.get('firma') ?? '');
    let search = $state('');
    let newUserRole = $state('user');
    let passwordFor = $state<number | null>(null);

    const users = $derived(
        (data.users as AdminUser[]).filter(
            (u) =>
                (companyFilter === '' || String(u.fk_company ?? '') === companyFilter) &&
                u.username.toLowerCase().includes(search.toLowerCase())
        )
    );

    function setFilter(value: string) {
        const url = new URL(page.url);
        if (value) url.searchParams.set('firma', value);
        else url.searchParams.delete('firma');
        goto(url, { replaceState: true, keepFocus: true, noScroll: true });
    }

    function canManage(u: AdminUser): boolean {
        if (u.id === data.currentUserId) return false;
        return data.isSuperadmin || u.role === 'user' || u.role === 'readonly';
    }

    function confirmSubmit(message: string) {
        return (e: SubmitEvent) => {
            if (!confirm(message)) e.preventDefault();
        };
    }

    // Selects direkt beim Ändern absenden
    function submitOnChange(e: Event) {
        (e.currentTarget as HTMLElement).closest('form')?.requestSubmit();
    }

    const input = 'border border-gray-300 rounded px-2 py-1 text-sm';
    const sel = input + ' pr-8';
    const btn = 'px-3 py-1 rounded text-sm';
</script>

<h1 class="text-2xl font-semibold mb-4">{data.isSuperadmin ? 'Alle Nutzer' : 'Nutzer meiner Firma'}</h1>

{#if form?.error}
    <p class="mb-4 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{form.error}</p>
{:else if form?.success}
    <p class="mb-4 rounded border border-green-300 bg-green-50 px-3 py-2 text-sm text-green-800">{form.success}</p>
{/if}

<div class="bg-white rounded border mb-6">
    <div class="flex flex-wrap items-center gap-3 px-4 py-2 border-b bg-gray-50 text-sm">
        <input bind:value={search} placeholder="Suchen…" class="{input} w-48" />
        {#if data.isSuperadmin}
            <label>Firma:
                <select class={sel} value={companyFilter} onchange={(e) => setFilter(e.currentTarget.value)}>
                    <option value="">alle</option>
                    {#each data.companies as c (c.id)}
                        <option value={String(c.id)}>{c.name}</option>
                    {/each}
                </select>
            </label>
        {/if}
        <span class="ml-auto text-gray-500">{users.length} Nutzer</span>
    </div>

    <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
            <tr>
                <th class="px-4 py-2 text-left">Benutzer</th>
                {#if data.isSuperadmin}<th class="px-4 py-2 text-left">Firma</th>{/if}
                <th class="px-4 py-2 text-left">Rolle</th>
                <th class="px-4 py-2 text-left">Status</th>
                <th class="px-4 py-2 text-right">Aktionen</th>
            </tr>
        </thead>
        <tbody class="divide-y">
            {#each users as u (u.id)}
                {@const manageable = canManage(u)}
                <tr class={u.is_active ? '' : 'text-gray-400'}>
                    <td class="px-4 py-2">
                        {u.username}
                        {#if u.id === data.currentUserId}<span class="text-xs text-gray-500">(du)</span>{/if}
                    </td>

                    {#if data.isSuperadmin}
                        <td class="px-4 py-2">
                            {#if u.role === 'superadmin'}
                                –
                            {:else}
                                <form method="POST" action="?/update" use:enhance>
                                    <input type="hidden" name="id" value={u.id} />
                                    <select name="fk_company" class={sel} onchange={submitOnChange}>
                                        {#each data.companies as c (c.id)}
                                            <option value={c.id} selected={c.id === u.fk_company}>{c.name}</option>
                                        {/each}
                                    </select>
                                </form>
                            {/if}
                        </td>
                    {/if}

                    <td class="px-4 py-2">
                        {#if manageable}
                            <form method="POST" action="?/update" use:enhance>
                                <input type="hidden" name="id" value={u.id} />
                                <select name="role" class={sel} onchange={submitOnChange}>
                                    {#each assignableRoles as r (r)}
                                        <option value={r} selected={r === u.role}>{ROLE_LABELS[r]}</option>
                                    {/each}
                                </select>
                            </form>
                        {:else}
                            {ROLE_LABELS[u.role] ?? u.role}
                        {/if}
                    </td>

                    <td class="px-4 py-2">
                        <span class="rounded px-2 py-0.5 text-xs {u.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'}">
                            {u.is_active ? 'aktiv' : 'deaktiviert'}
                        </span>
                    </td>

                    <td class="px-4 py-2">
                        <div class="flex justify-end gap-2">
                            {#if manageable}
                                {#if passwordFor === u.id}
                                    <form
                                        method="POST"
                                        action="?/password"
                                        use:enhance={() => async ({ update }) => {
                                            passwordFor = null;
                                            await update();
                                        }}
                                        class="flex gap-1"
                                    >
                                        <input type="hidden" name="id" value={u.id} />
                                        <input name="password" type="password" minlength="8" required placeholder="Neues Passwort"
                                            class="{input} w-36" autocomplete="new-password" />
                                        <button class="{btn} bg-gray-800 text-white">OK</button>
                                        <button type="button" class="{btn} bg-gray-200" onclick={() => (passwordFor = null)}>✕</button>
                                    </form>
                                {:else}
                                    <button class="{btn} bg-gray-200 hover:bg-gray-300" onclick={() => (passwordFor = u.id)}>Passwort setzen</button>
                                {/if}
                                <form method="POST" action="?/update" use:enhance>
                                    <input type="hidden" name="id" value={u.id} />
                                    <input type="hidden" name="is_active" value={String(!u.is_active)} />
                                    <button class="{btn} bg-gray-200 hover:bg-gray-300">{u.is_active ? 'Deaktivieren' : 'Aktivieren'}</button>
                                </form>
                                <form method="POST" action="?/delete" use:enhance onsubmit={confirmSubmit(`Nutzer "${u.username}" wirklich löschen?`)}>
                                    <input type="hidden" name="id" value={u.id} />
                                    <button class="{btn} bg-red-600 text-white hover:bg-red-700">Löschen</button>
                                </form>
                            {:else if u.id === data.currentUserId}
                                <a href="/konto" class="{btn} bg-gray-200 hover:bg-gray-300">Mein Konto</a>
                            {/if}
                        </div>
                    </td>
                </tr>
            {:else}
                <tr><td colspan="5" class="px-4 py-3 text-gray-500">Keine Nutzer gefunden.</td></tr>
            {/each}
        </tbody>
    </table>
</div>

<div id="neu" class="bg-white rounded border p-4">
    <h2 class="font-medium mb-3">Neuen Nutzer anlegen</h2>
    <form method="POST" action="?/create" use:enhance class="flex flex-wrap items-end gap-3 text-sm">
        <label class="flex flex-col">Benutzername
            <input name="username" required class={input} autocomplete="off" />
        </label>
        <label class="flex flex-col">Passwort (min. 8 Zeichen)
            <input name="password" type="password" minlength="8" required class={input} autocomplete="new-password" />
        </label>
        <label class="flex flex-col">Rolle
            <select name="role" bind:value={newUserRole} class={sel}>
                {#each assignableRoles as r (r)}
                    <option value={r}>{ROLE_LABELS[r]}</option>
                {/each}
            </select>
        </label>
        {#if data.isSuperadmin && newUserRole !== 'superadmin'}
            <label class="flex flex-col">Firma
                <select name="fk_company" required class={sel} value={companyFilter}>
                    <option value="" disabled>Bitte wählen</option>
                    {#each data.companies as c (c.id)}
                        <option value={String(c.id)}>{c.name}</option>
                    {/each}
                </select>
            </label>
        {/if}
        <button class="{btn} bg-gray-800 text-white hover:bg-gray-700">Nutzer anlegen</button>
    </form>
</div>
