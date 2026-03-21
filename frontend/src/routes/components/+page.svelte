<script lang="ts">
	import { onMount } from 'svelte';
	import { components as componentsApi, bikes as bikesApi } from '$lib/api';
	import { authStore } from '$lib/auth.svelte';
	import { formatDistance, wearColor, wearLabel } from '$lib/utils';
	import type { ComponentStatus, Bike } from '$lib/types';
	import { Settings, Plus, Pencil } from 'lucide-svelte';

	let statuses = $state<ComponentStatus[]>([]);
	let bikeList = $state<Bike[]>([]);
	let loading = $state(true);

	// Edit modal
	let editComp = $state<ComponentStatus | null>(null);
	let editBrand = $state('');
	let editLimit = $state<number | ''>('');
	let editActive = $state(true);
	let editSaving = $state(false);
	let editError = $state('');

	const unit = $derived(authStore.user?.preferred_unit ?? 'KM');

	function getBikeName(id: number) {
		return bikeList.find((b) => b.id === id)?.name ?? `Bike #${id}`;
	}

	function getBadgeClass(pct: number) {
		const c = wearColor(pct);
		if (c === 'red') return 'badge-red';
		if (c === 'yellow') return 'badge-yellow';
		return 'badge-green';
	}

	onMount(async () => {
		try {
			[statuses, bikeList] = await Promise.all([componentsApi.status(), bikesApi.list()]);
		} finally {
			loading = false;
		}
	});

	function openEdit(comp: ComponentStatus) {
		editComp = comp;
		editBrand = comp.brand_model ?? '';
		editLimit = comp.lifespan_limit ?? '';
		editActive = comp.is_active;
		editError = '';
	}

	async function handleEdit(e: SubmitEvent) {
		e.preventDefault();
		if (!editComp) return;
		editError = '';
		editSaving = true;
		try {
			await componentsApi.patch(editComp.id, {
				brand_model: editBrand || undefined,
				lifespan_limit: editLimit !== '' ? Number(editLimit) : undefined,
				is_active: editActive
			});
			// Refresh status
			statuses = await componentsApi.status();
			editComp = null;
		} catch (err) {
			editError = err instanceof Error ? err.message : 'Failed to save';
		} finally {
			editSaving = false;
		}
	}

	const sorted = $derived(
		[...statuses].sort((a, b) => (b.wear_percentage ?? 0) - (a.wear_percentage ?? 0))
	);
</script>

<svelte:head>
	<title>Components — GravelLog</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gravel-900">Components</h1>
			<p class="text-sm text-gravel-500 mt-0.5">Track wear across all your bikes</p>
		</div>
		<a href="/bikes" class="btn-secondary text-sm">
			<Plus size={14} /> Add via Bike
		</a>
	</div>

	{#if loading}
		<div class="text-center py-12 text-gravel-400">Loading…</div>
	{:else if sorted.length === 0}
		<div class="card text-center py-12">
			<Settings size={40} class="text-gravel-300 mx-auto mb-3" />
			<p class="text-gravel-500 mb-2">No components with lifespan limits tracked yet.</p>
			<p class="text-sm text-gravel-400">Go to a bike's detail page to add components.</p>
		</div>
	{:else}
		<div class="card p-0 overflow-hidden">
			<table class="w-full text-sm">
				<thead class="bg-gravel-50 border-b border-gravel-100">
					<tr>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium">Part</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium hidden md:table-cell">Bike</th>
						<th class="text-right px-4 py-3 text-gravel-600 font-medium">Worn</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium">Status</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium w-48 hidden sm:table-cell">Progress</th>
						<th class="px-4 py-3"></th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gravel-50">
					{#each sorted as comp}
						{@const pct = comp.wear_percentage ?? 0}
						<tr class="hover:bg-gravel-50 transition-colors {!comp.is_active ? 'opacity-50' : ''}">
							<td class="px-4 py-3">
								<p class="font-medium text-gravel-900">{comp.part_type}</p>
								{#if comp.brand_model}
									<p class="text-xs text-gravel-400">{comp.brand_model}</p>
								{/if}
							</td>
							<td class="px-4 py-3 text-gravel-600 hidden md:table-cell">{getBikeName(comp.bike_id)}</td>
							<td class="px-4 py-3 text-right">
								<p class="font-semibold text-gravel-800">{formatDistance(comp.current_distance, unit)}</p>
								{#if comp.lifespan_limit}
									<p class="text-xs text-gravel-400">/ {formatDistance(comp.lifespan_limit, unit)}</p>
								{/if}
							</td>
							<td class="px-4 py-3">
								<span class="badge {getBadgeClass(pct)}">{wearLabel(pct)}</span>
								<p class="text-xs text-gravel-400 mt-1">{pct.toFixed(0)}%</p>
							</td>
							<td class="px-4 py-3 hidden sm:table-cell">
								<div class="w-full bg-gravel-100 rounded-full h-2">
									<div
										class="h-2 rounded-full {pct >= 100 ? 'bg-red-500' : pct >= 75 ? 'bg-yellow-500' : 'bg-green-500'}"
										style="width: {Math.min(pct, 100)}%"
									></div>
								</div>
							</td>
							<td class="px-4 py-3">
								<div class="flex items-center gap-1">
									<a
										href="/service?component_id={comp.id}"
										class="btn-ghost px-1.5 py-1 text-xs"
										title="Service history"
									>
										Service
									</a>
									<button class="btn-ghost px-1.5 py-1" onclick={() => openEdit(comp)} title="Edit">
										<Pencil size={13} />
									</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<!-- Edit modal -->
{#if editComp}
	<div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" role="dialog" aria-modal="true">
		<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
			<h2 class="text-lg font-semibold text-gravel-900 mb-1">Edit Component</h2>
			<p class="text-sm text-gravel-500 mb-5">{editComp.part_type}</p>

			{#if editError}
				<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{editError}</div>
			{/if}

			<form onsubmit={handleEdit} class="space-y-4">
				<div>
					<label class="label" for="edit-brand">Brand / Model</label>
					<input id="edit-brand" class="input" bind:value={editBrand} placeholder="KMC X12" />
				</div>
				<div>
					<label class="label" for="edit-limit">Lifespan Limit ({unit})</label>
					<input id="edit-limit" type="number" min="0" class="input" bind:value={editLimit} />
				</div>
				<div class="flex items-center gap-2">
					<input id="edit-active" type="checkbox" bind:checked={editActive} class="rounded" />
					<label for="edit-active" class="text-sm text-gravel-700">Active</label>
				</div>
				<div class="flex gap-3 pt-2">
					<button type="button" class="btn-secondary flex-1 justify-center" onclick={() => (editComp = null)}>Cancel</button>
					<button type="submit" class="btn-primary flex-1 justify-center" disabled={editSaving}>
						{editSaving ? 'Saving…' : 'Save Changes'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
