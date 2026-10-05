<script lang="ts">
    import { enhance } from '$app/forms';
    let { data, form } = $props();

    let editing = $state<number | null>(null);

    function confirmSubmit(message: string) {
        return (e: SubmitEvent) => {
            if (!confirm(message)) e.preventDefault();
        };
    }

    const input = 'border border-gray-300 rounded px-2 py-1 text-sm';
    const btn = 'px-3 py-1 rounded text-sm';
</script>

<h1 class="text-2xl font-semibold mb-4">Firmen</h1>

{#if form?.error}
    <p class="mb-4 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">{form.error}</p>
{:else if form?.success}
    <p class="mb-4 rounded border border-green-300 bg-green-50 px-3 py-2 text-sm text-green-800">{form.success}</p>
{/if}

<div class="bg-white rounded border mb-6">
    <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
            <tr>
                <th class="px-4 py-2 text-left">Name</th>
                <th class="px-4 py-2 text-left">Nutzer</th>
                <th class="px-4 py-2 text-left">Status</th>
                <th class="px-4 py-2 text-right">Aktionen</th>
            </tr>
        </thead>
        <tbody class="divide-y">
            {#each data.companies as c (c.id)}
                <tr class={c.is_active ? '' : 'text-gray-400'}>
                    <td class="px-4 py-2">
                        {#if editing === c.id}
                            <form
                                method="POST"
                                action="?/update"
                                use:enhance={() => async ({ update }) => {
                                    editing = null;
                                    await update();
                                }}
                                class="flex gap-2"
                            >
                                <input type="hidden" name="id" value={c.id} />
                                <input name="name" value={c.name} required class="{input} w-64" />
                                <button class="{btn} bg-gray-800 text-white">Speichern</button>
                                <button type="button" class="{btn} bg-gray-200" onclick={() => (editing = null)}>Abbrechen</button>
                            </form>
                        {:else}
                            {c.name}
                        {/if}
                    </td>
                    <td class="px-4 py-2">
                        <a href="/admin/nutzer?firma={c.id}" class="text-blue-600 hover:underline">{c.user_count} Nutzer</a>
                    </td>
                    <td class="px-4 py-2">
                        <span class="rounded px-2 py-0.5 text-xs {c.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'}">
                            {c.is_active ? 'aktiv' : 'deaktiviert'}
                        </span>
                    </td>
                    <td class="px-4 py-2">
                        <div class="flex justify-end gap-2">
                            <a href="/admin/nutzer?firma={c.id}#neu" class="{btn} bg-gray-200 hover:bg-gray-300">+ Nutzer</a>
                            <button class="{btn} bg-gray-200 hover:bg-gray-300" onclick={() => (editing = c.id)}>Umbenennen</button>
                            <form method="POST" action="?/update" use:enhance>
                                <input type="hidden" name="id" value={c.id} />
                                <input type="hidden" name="is_active" value={String(!c.is_active)} />
                                <button class="{btn} bg-gray-200 hover:bg-gray-300">{c.is_active ? 'Deaktivieren' : 'Aktivieren'}</button>
                            </form>
                            <form method="POST" action="?/delete" use:enhance onsubmit={confirmSubmit(`Firma "${c.name}" wirklich löschen?`)}>
                                <input type="hidden" name="id" value={c.id} />
                                <button class="{btn} bg-red-600 text-white hover:bg-red-700">Löschen</button>
                            </form>
                        </div>
                    </td>
                </tr>
            {:else}
                <tr><td colspan="4" class="px-4 py-3 text-gray-500">Noch keine Firmen angelegt.</td></tr>
            {/each}
        </tbody>
    </table>
</div>

<div id="neu" class="bg-white rounded border p-4">
    <h2 class="font-medium mb-3">Neue Firma anlegen</h2>
    <form method="POST" action="?/create" use:enhance class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm items-end">
        <label class="flex flex-col">Firmenname
            <input name="name" required class={input} />
        </label>
        <label class="flex flex-col">Erster Admin (optional)
            <input name="admin_username" class={input} placeholder="Benutzername" autocomplete="off" />
        </label>
        <label class="flex flex-col">Admin-Passwort (min. 8 Zeichen)
            <input name="admin_password" type="password" minlength="8" class={input} autocomplete="new-password" />
        </label>
        <div class="sm:col-span-3">
            <button class="{btn} bg-gray-800 text-white hover:bg-gray-700">Firma anlegen</button>
        </div>
    </form>
</div>
