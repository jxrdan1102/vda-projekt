<script lang="ts">
    import {goto} from '$app/navigation';
    import {browser} from '$app/environment';

    let username = '';
    let password = '';
    let errorMessage = '';
    let loading = false;

    const handleLogin = async () => {
        errorMessage = '';
        loading = true;

        try {
            const response = await fetch('http://localhost:9999/auth/token', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Login fehlgeschlagen');
            }

            const data = await response.json();

            if (browser) {
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
            }

            goto('/kmgs');
        } catch (e) {
            errorMessage = e.message || 'Ein Fehler ist aufgetreten';
        } finally {
            loading = false;
        }
    };
</script>

<style>
    /* Dein Stil wie oben – kannst du beibehalten */
</style>

<div class="login-form">
    <h2>Login</h2>

    {#if errorMessage}
        <p class="error">{errorMessage}</p>
    {/if}

    {#if loading}
        <p class="loading">Lade...</p>
    {/if}

    <form on:submit|preventDefault={handleLogin}>
        <label for="username">Benutzername</label>
        <input type="text" id="username" bind:value={username} required />

        <label for="password">Passwort</label>
        <input type="password" id="password" bind:value={password} required />

        <button type="submit" disabled={loading}>
            {#if loading}Wird gesendet...{:else}Anmelden{/if}
        </button>
    </form>
    <a href="/admin">Test</a>
</div>
