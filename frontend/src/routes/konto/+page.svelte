<script lang="ts">
    import { enhance } from '$app/forms';
    import { ROLE_LABELS } from '$lib/roles';
    let { data, form } = $props();
    const input = 'mt-1 block w-full border border-gray-300 rounded px-2 py-1 text-sm';
</script>

<div class="max-w-md mx-auto mt-8 space-y-6">
    <section class="bg-white rounded border p-4 text-sm space-y-1">
        <h2 class="text-lg font-semibold mb-2">Mein Konto</h2>
        {#if data.me}
            <p><span class="text-gray-500">Benutzer:</span> {data.me.username}</p>
            <p><span class="text-gray-500">Rolle:</span> {ROLE_LABELS[data.me.role] ?? data.me.role}</p>
            <p><span class="text-gray-500">Firma:</span> {data.me.company_name ?? '–'}</p>
        {/if}
    </section>

    <section class="bg-white rounded border p-4 text-sm">
        <h3 class="font-semibold mb-2">Passwort ändern</h3>
        {#if form?.error}<p class="text-red-600 mb-2">{form.error}</p>{/if}
        {#if form?.success}<p class="text-green-700 mb-2">{form.success}</p>{/if}
        <form method="POST" action="?/changePassword" use:enhance class="space-y-2">
            <label class="block">Altes Passwort
                <input type="password" name="old_password" required class={input} />
            </label>
            <label class="block">Neues Passwort (min. 8 Zeichen)
                <input type="password" name="new_password" minlength="8" required class={input} />
            </label>
            <label class="block">Neues Passwort wiederholen
                <input type="password" name="new_password_repeat" minlength="8" required class={input} />
            </label>
            <button class="bg-gray-800 text-white px-4 py-1 rounded hover:bg-gray-700">Speichern</button>
        </form>
    </section>
</div>
