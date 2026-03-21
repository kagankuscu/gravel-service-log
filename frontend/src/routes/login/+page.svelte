<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/auth.svelte';
	import { Bike } from 'lucide-svelte';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = '';
		loading = true;
		try {
			await authStore.login(email, password);
			goto('/');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Login failed';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Login — GravelLog</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gravel-50 px-4">
	<div class="w-full max-w-sm">
		<div class="text-center mb-8">
			<div class="inline-flex items-center justify-center w-14 h-14 bg-gravel-800 rounded-2xl mb-4">
				<Bike size={28} class="text-white" />
			</div>
			<h1 class="text-2xl font-bold text-gravel-900">GravelLog</h1>
			<p class="text-sm text-gravel-500 mt-1">Track every ride, every component</p>
		</div>

		<div class="card">
			<h2 class="text-lg font-semibold text-gravel-800 mb-6">Sign in to your account</h2>

			{#if error}
				<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
					{error}
				</div>
			{/if}

			<form onsubmit={handleSubmit} class="space-y-4">
				<div>
					<label class="label" for="email">Email</label>
					<input
						id="email"
						type="email"
						class="input"
						placeholder="you@example.com"
						bind:value={email}
						required
					/>
				</div>

				<div>
					<label class="label" for="password">Password</label>
					<input
						id="password"
						type="password"
						class="input"
						placeholder="••••••••"
						bind:value={password}
						required
					/>
				</div>

				<button type="submit" class="btn-primary w-full justify-center" disabled={loading}>
					{loading ? 'Signing in…' : 'Sign in'}
				</button>
			</form>
		</div>

		<p class="text-center text-sm text-gravel-500 mt-4">
			Don't have an account?
			<a href="/register" class="text-gravel-700 font-medium hover:underline">Create one</a>
		</p>
	</div>
</div>
