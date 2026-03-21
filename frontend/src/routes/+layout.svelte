<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authStore } from '$lib/auth.svelte';
	import {
		Bike,
		Activity,
		Settings,
		LayoutDashboard,
		Wrench,
		LogOut,
		Menu,
		X
	} from 'lucide-svelte';

	let { children } = $props();

	const publicRoutes = ['/login', '/register'];
	let menuOpen = $state(false);

	onMount(async () => {
		await authStore.init();
	});

	$effect(() => {
		if (!authStore.loading) {
			const isPublic = publicRoutes.includes($page.url.pathname);
			if (!authStore.isAuthenticated && !isPublic) {
				goto('/login');
			} else if (authStore.isAuthenticated && isPublic) {
				goto('/');
			}
		}
	});

	const navItems = [
		{ href: '/', label: 'Dashboard', icon: LayoutDashboard },
		{ href: '/bikes', label: 'Bikes', icon: Bike },
		{ href: '/rides', label: 'Rides', icon: Activity },
		{ href: '/components', label: 'Components', icon: Settings },
		{ href: '/service', label: 'Service', icon: Wrench }
	];

	function handleLogout() {
		authStore.logout();
		goto('/login');
	}
</script>

{#if authStore.loading}
	<div class="min-h-screen flex items-center justify-center">
		<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gravel-700"></div>
	</div>
{:else if publicRoutes.includes($page.url.pathname)}
	{@render children()}
{:else if authStore.isAuthenticated}
	<div class="min-h-screen flex flex-col">
		<!-- Top bar -->
		<header class="bg-gravel-800 text-white shadow-md">
			<div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<button
						class="md:hidden p-1 rounded hover:bg-gravel-700"
						onclick={() => (menuOpen = !menuOpen)}
					>
						{#if menuOpen}
							<X size={20} />
						{:else}
							<Menu size={20} />
						{/if}
					</button>
					<a href="/" class="flex items-center gap-2 font-bold text-lg tracking-tight">
						<Bike size={22} class="text-gravel-300" />
						<span>GravelLog</span>
					</a>
				</div>

				<!-- Desktop nav -->
				<nav class="hidden md:flex items-center gap-1">
					{#each navItems as item}
						<a
							href={item.href}
							class="flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-colors
								{$page.url.pathname === item.href
								? 'bg-gravel-600 text-white'
								: 'text-gravel-200 hover:bg-gravel-700 hover:text-white'}"
						>
							<item.icon size={16} />
							{item.label}
						</a>
					{/each}
				</nav>

				<div class="flex items-center gap-2">
					<span class="hidden md:block text-sm text-gravel-300">{authStore.user?.username}</span>
					<button
						onclick={handleLogout}
						class="flex items-center gap-1 text-gravel-300 hover:text-white text-sm px-2 py-1 rounded hover:bg-gravel-700 transition-colors"
					>
						<LogOut size={16} />
						<span class="hidden md:inline">Logout</span>
					</button>
				</div>
			</div>
		</header>

		<!-- Mobile menu -->
		{#if menuOpen}
			<div class="md:hidden bg-gravel-700 border-b border-gravel-600">
				{#each navItems as item}
					<a
						href={item.href}
						onclick={() => (menuOpen = false)}
						class="flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
							{$page.url.pathname === item.href
							? 'bg-gravel-600 text-white'
							: 'text-gravel-200 hover:bg-gravel-600 hover:text-white'}"
					>
						<item.icon size={16} />
						{item.label}
					</a>
				{/each}
			</div>
		{/if}

		<!-- Page content -->
		<main class="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
			{@render children()}
		</main>
	</div>
{/if}
