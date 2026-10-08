<script lang="ts">
    import {goto} from '$app/navigation';
    import {page} from '$app/stores';

    let username = '';
    let password = '';
    let errorMessage = '';
    let loading = false;
    let from = '/dashboard';
    $: {
        const urlFrom = $page.url.searchParams.get('from');
        if (urlFrom) {
            from = urlFrom;
        }
    }

    const handleLogin = async () => {
        errorMessage = '';
        loading = true;
        try {
            const response = await fetch('/backend/auth/token', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Login fehlgeschlagen');
            }

            if (from === '/') from = '/dashboard';
            // invalidateAll: Layout neu laden, damit Navigation/Rolle sofort stimmen
            goto(from, { invalidateAll: true });

        } catch (e: any) {
            errorMessage = e.message || 'Ein Fehler ist aufgetreten';
        } finally {
            loading = false;
        }
    };
</script>

<!-- Tailwind-Stil -->
<div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="w-full max-w-md bg-white p-8 rounded-xl shadow-md border border-gray-200">
        <h2 class="text-2xl font-bold text-center text-gray-800 mb-6">Kistner Metrologie – Login</h2>

        {#if errorMessage}
            <p class="text-red-600 text-sm mb-4 text-center">{errorMessage}</p>
        {/if}

        <form on:submit|preventDefault={handleLogin} class="space-y-4">
            <div>
                <label for="username" class="block text-sm font-medium text-gray-700">Benutzername</label>
                <input
                        id="username"
                        type="text"
                        bind:value={username}
                        required
                        class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-700">Passwort</label>
                <input
                        id="password"
                        type="password"
                        bind:value={password}
                        required
                        class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
            </div>

            <button
                    type="submit"
                    class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md transition disabled:opacity-50"
                    disabled={loading}
            >
                {#if loading}Wird gesendet...{:else}Anmelden{/if}
            </button>
        </form>
    </div>
</div>
