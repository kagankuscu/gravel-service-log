<script lang="ts">
	import { onMount } from 'svelte';
	import { rides as ridesApi, bikes as bikesApi } from '$lib/api';
	import { authStore } from '$lib/auth.svelte';
	import { formatDistance, formatDate } from '$lib/utils';
	import type { Ride, Bike } from '$lib/types';
	import { Activity, Plus, Trash2 } from 'lucide-svelte';

	let allRides = $state<Ride[]>([]);
	let bikeList = $state<Bike[]>([]);
	let loading = $state(true);
	let showForm = $state(false);
	let error = $state('');
	let submitting = $state(false);

	// Filter
	let filterBikeId = $state<number | ''>('');

	// Form
	let formBikeId = $state<number | ''>('');
	let formDistance = $state(0);
	let formDate = $state(new Date().toISOString().substring(0, 10));
	let formNotes = $state('');

	const unit = $derived(authStore.user?.preferred_unit ?? 'KM');

	const filteredRides = $derived(
		filterBikeId === ''
			? allRides
			: allRides.filter((r) => r.bike_id === Number(filterBikeId))
	);

	function getBikeName(id: number) {
		return bikeList.find((b) => b.id === id)?.name ?? `Bike #${id}`;
	}

	onMount(async () => {
		try {
			[allRides, bikeList] = await Promise.all([ridesApi.list(), bikesApi.list()]);
		} finally {
			loading = false;
		}
	});

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (formBikeId === '') return;
		error = '';
		submitting = true;
		try {
			const created = await ridesApi.create({
				bike_id: Number(formBikeId),
				distance: formDistance,
				date: formDate ? new Date(formDate).toISOString() : undefined,
				notes: formNotes || undefined
			});
			allRides = [created, ...allRides];
			showForm = false;
			formDistance = 0;
			formNotes = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to log ride';
		} finally {
			submitting = false;
		}
	}

	async function handleDelete(ride: Ride) {
		if (!confirm('Delete this ride? Odometer will be reverted.')) return;
		await ridesApi.remove(ride.id);
		allRides = allRides.filter((r) => r.id !== ride.id);
	}
</script>

<svelte:head>
	<title>Rides — GravelLog</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-gravel-900">Rides</h1>
		<button class="btn-primary" onclick={() => (showForm = !showForm)}>
			<Plus size={16} /> Log Ride
		</button>
	</div>

	<!-- Log ride form -->
	{#if showForm}
		<div class="card border-gravel-200">
			<h2 class="font-semibold text-gravel-800 mb-4">Log a Ride</h2>
			{#if error}
				<div class="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
			{/if}
			<form onsubmit={handleSubmit} class="space-y-4">
				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label class="label" for="ride-bike">Bike *</label>
						<select id="ride-bike" class="input" bind:value={formBikeId} required>
							<option value="">Select a bike…</option>
							{#each bikeList.filter((b) => b.is_active) as bike}
								<option value={bike.id}>{bike.name}</option>
							{/each}
						</select>
					</div>
					<div>
						<label class="label" for="ride-dist">Distance ({unit}) *</label>
						<input id="ride-dist" type="number" min="0.1" step="0.1" class="input" bind:value={formDistance} required />
					</div>
					<div>
						<label class="label" for="ride-date">Date</label>
						<input id="ride-date" type="date" class="input" bind:value={formDate} />
					</div>
					<div>
						<label class="label" for="ride-notes">Notes</label>
						<input id="ride-notes" class="input" bind:value={formNotes} placeholder="Morning loop…" />
					</div>
				</div>
				<div class="flex gap-3">
					<button type="button" class="btn-secondary" onclick={() => (showForm = false)}>Cancel</button>
					<button type="submit" class="btn-primary" disabled={submitting}>
						{submitting ? 'Logging…' : 'Log Ride'}
					</button>
				</div>
			</form>
		</div>
	{/if}

	<!-- Filter -->
	<div class="flex items-center gap-3">
		<select class="input max-w-xs" bind:value={filterBikeId}>
			<option value="">All bikes</option>
			{#each bikeList as bike}
				<option value={bike.id}>{bike.name}</option>
			{/each}
		</select>
		<span class="text-sm text-gravel-400">{filteredRides.length} rides</span>
	</div>

	<!-- Rides list -->
	{#if loading}
		<div class="text-center py-12 text-gravel-400">Loading…</div>
	{:else if filteredRides.length === 0}
		<div class="card text-center py-12">
			<Activity size={40} class="text-gravel-300 mx-auto mb-3" />
			<p class="text-gravel-500">No rides logged yet.</p>
		</div>
	{:else}
		<div class="card p-0 overflow-hidden">
			<table class="w-full text-sm">
				<thead class="bg-gravel-50 border-b border-gravel-100">
					<tr>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium">Date</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium">Bike</th>
						<th class="text-right px-4 py-3 text-gravel-600 font-medium">Distance</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium hidden sm:table-cell">Notes</th>
						<th class="px-4 py-3"></th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gravel-50">
					{#each filteredRides.slice().sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()) as ride}
						<tr class="hover:bg-gravel-50 transition-colors">
							<td class="px-4 py-3 text-gravel-700">{formatDate(ride.date)}</td>
							<td class="px-4 py-3 text-gravel-700">{getBikeName(ride.bike_id)}</td>
							<td class="px-4 py-3 text-right font-semibold text-gravel-800">
								{formatDistance(ride.distance, unit)}
							</td>
							<td class="px-4 py-3 text-gravel-400 hidden sm:table-cell italic">
								{ride.notes ?? '—'}
							</td>
							<td class="px-4 py-3">
								<button
									class="text-red-400 hover:text-red-600 p-1 rounded hover:bg-red-50 transition-colors"
									onclick={() => handleDelete(ride)}
								>
									<Trash2 size={14} />
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
