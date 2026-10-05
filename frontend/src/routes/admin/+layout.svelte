<script lang="ts">
    import { page } from '$app/state';
    let { children, data } = $props();

    const items = $derived([
        { href: '/admin', label: 'Übersicht', icon: '▦' },
        ...(data.isSuperadmin ? [{ href: '/admin/firmen', label: 'Firmen', icon: '🏢' }] : []),
        { href: '/admin/nutzer', label: data.isSuperadmin ? 'Alle Nutzer' : 'Nutzer meiner Firma', icon: '👤' },
        { href: '/konto', label: 'Mein Konto', icon: '⚙' }
    ]);

    const isActive = (href: string) =>
        href === '/admin' ? page.url.pathname === '/admin' : page.url.pathname.startsWith(href);
</script>

<div class="max-w-7xl mx-auto mt-6 flex gap-6">
    <aside class="w-56 shrink-0">
        <div class="bg-white rounded border overflow-hidden">
            <div class="px-4 py-3 border-b text-xs font-semibold uppercase tracking-wide text-gray-500">
                {data.isSuperadmin ? 'Superadmin' : 'Firmen-Admin'}
            </div>
            <nav class="flex flex-col py-1 text-sm">
                {#each items as item (item.href)}
                    <a
                        href={item.href}
                        class="flex items-center gap-2 px-4 py-2 border-l-4 transition
                            {isActive(item.href)
                                ? 'border-[#1f3b5e] bg-blue-50 font-medium text-[#1f3b5e]'
                                : 'border-transparent text-gray-700 hover:bg-gray-50'}"
                    >
                        <span class="w-5 text-center" aria-hidden="true">{item.icon}</span>
                        {item.label}
                    </a>
                {/each}
            </nav>
        </div>
    </aside>

    <section class="flex-1 min-w-0">
        {@render children()}
    </section>
</div>
