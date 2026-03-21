<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { service as serviceApi, components as componentsApi, bikes as bikesApi } from '$lib/api';
	import { formatDate } from '$lib/utils';
	import type { ServiceRecord, Component, Bike } from '$lib/types';
	import { Wrench, Plus, Trash2 } from 'lucide-svelte';

	let records = $state<ServiceRecord[]>([]);
	let componentList = $state<Component[]>([]);
	let bikeList = $state<Bike[]>([]);
	let loading = $state(true);
	let showForm = $state(false);
	let error = $state('');
	let submitting = $state(false);

	// Filter by component from query param
	let filterComponentId = $state<number | ''>('');

	// Form
	let formComponentId = $state<number | ''>('');
	let formWork = $state('');
	let formDate = $state(new Date().toISOString().substring(0, 10));
	let formCost = $state<number | ''>('');

	const filteredRecords = $derived(
		filterComponentId === ''
			? records
			: records.filter((r) => r.component_id === Number(filterComponentId))
	);

	function getComponentName(id: number) {
		const c = componentList.find((c) => c.id === id);
		if (!c) return `Component #${id}`;
		return c.brand_model ? `${c.part_type} (${c.brand_model})` : c.part_type;
	}

	function getBikeName(componentId: number) {
		const c = componentList.find((c) => c.id === componentId);
		if (!c) return '';
		return bikeList.find((b) => b.id === c.bike_id)?.name ?? '';
	}

	async function loadRecords() {
		// Load all service records by fetching per component
		const all: ServiceRecord[] = [];
		await Promise.all(
			componentList.map(async (c) => {
				const recs = await serviceApi.list(c.id);
				all.push(...recs);
			})
		);
		return all.sort((a, b) => new Date(b.service_date).getTime() - new Date(a.service_date).getTime());
	}

	onMount(async () => {
		try {
			// Check query param
			const qCompId = $page.url.searchParams.get('component_id');
			if (qCompId) filterComponentId = Number(qCompId);

			bikeList = await bikesApi.list();
			// Get all components across all bikes
			const comps = await Promise.all(bikeList.map((b) => componentsApi.list(b.id)));
			componentList = comps.flat();
			records = await loadRecords();
		} finally {
			loading = false;
		}
	});

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (formComponentId === '') return;
		error = '';
		submitting = true;
		try {
			const created = await serviceApi.create({
				component_id: Number(formComponentId),
				work_performed: formWork,
				service_date: formDate ? new Date(formDate).toISOString() : undefined,
				cost: formCost !== '' ? Number(formCost) : undefined
			});
			records = [created, ...records];
			showForm = false;
			formWork = '';
			formCost = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to log service';
		} finally {
			submitting = false;
		}
	}

	async function handleDelete(rec: ServiceRecord) {
		if (!confirm('Delete this service record?')) return;
		await serviceApi.remove(rec.id);
		records = records.filter((r) => r.id !== rec.id);
	}
</script>

<svelte:head>
	<title>Service Records — GravelLog</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-gravel-900">Service Records</h1>
		<button class="btn-primary" onclick={() => (showForm = !showForm)}>
			<Plus size={16} /> Log Service
		</button>
	</div>

	<!-- Log service form -->
	{#if showForm}
		<div class="card border-gravel-200">
			<h2 class="font-semibold text-gravel-800 mb-4">Log Service Event</h2>
			{#if error}
				<div class="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
			{/if}
			<form onsubmit={handleSubmit} class="space-y-4">
				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label class="label" for="svc-comp">Component *</label>
						<select id="svc-comp" class="input" bind:value={formComponentId} required>
							<option value="">Select a component…</option>
							{#each bikeList as bike}
								{@const bikeComps = componentList.filter((c) => c.bike_id === bike.id)}
								{#if bikeComps.length > 0}
									<optgroup label={bike.name}>
										{#each bikeComps as comp}
											<option value={comp.id}>{comp.part_type}{comp.brand_model ? ` — ${comp.brand_model}` : ''}</option>
										{/each}
									</optgroup>
								{/if}
							{/each}
						</select>
					</div>
					<div>
						<label class="label" for="svc-date">Date</label>
						<input id="svc-date" type="date" class="input" bind:value={formDate} />
					</div>
					<div class="sm:col-span-2">
						<label class="label" for="svc-work">Work Performed *</label>
						<input
							id="svc-work"
							class="input"
							bind:value={formWork}
							required
							placeholder="Clean & Lube, Chain Replacement…"
						/>
					</div>
					<div>
						<label class="label" for="svc-cost">Cost (optional)</label>
						<input id="svc-cost" type="number" min="0" step="0.01" class="input" bind:value={formCost} placeholder="0.00" />
					</div>
				</div>
				<div class="flex gap-3">
					<button type="button" class="btn-secondary" onclick={() => (showForm = false)}>Cancel</button>
					<button type="submit" class="btn-primary" disabled={submitting}>
						{submitting ? 'Logging…' : 'Log Service'}
					</button>
				</div>
			</form>
		</div>
	{/if}

	<!-- Filter -->
	<div class="flex items-center gap-3">
		<select class="input max-w-xs" bind:value={filterComponentId}>
			<option value="">All components</option>
			{#each bikeList as bike}
				{@const bikeComps = componentList.filter((c) => c.bike_id === bike.id)}
				{#if bikeComps.length > 0}
					<optgroup label={bike.name}>
						{#each bikeComps as comp}
							<option value={comp.id}>{comp.part_type}{comp.brand_model ? ` — ${comp.brand_model}` : ''}</option>
						{/each}
					</optgroup>
				{/if}
			{/each}
		</select>
		<span class="text-sm text-gravel-400">{filteredRecords.length} records</span>
	</div>

	<!-- Records list -->
	{#if loading}
		<div class="text-center py-12 text-gravel-400">Loading…</div>
	{:else if filteredRecords.length === 0}
		<div class="card text-center py-12">
			<Wrench size={40} class="text-gravel-300 mx-auto mb-3" />
			<p class="text-gravel-500">No service records yet.</p>
		</div>
	{:else}
		<div class="card p-0 overflow-hidden">
			<table class="w-full text-sm">
				<thead class="bg-gravel-50 border-b border-gravel-100">
					<tr>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium">Date</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium">Component</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium hidden md:table-cell">Bike</th>
						<th class="text-left px-4 py-3 text-gravel-600 font-medium">Work Performed</th>
						<th class="text-right px-4 py-3 text-gravel-600 font-medium hidden sm:table-cell">Cost</th>
						<th class="px-4 py-3"></th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gravel-50">
					{#each filteredRecords as rec}
						<tr class="hover:bg-gravel-50 transition-colors">
							<td class="px-4 py-3 text-gravel-600 whitespace-nowrap">{formatDate(rec.service_date)}</td>
							<td class="px-4 py-3 text-gravel-800 font-medium">{getComponentName(rec.component_id)}</td>
							<td class="px-4 py-3 text-gravel-500 hidden md:table-cell">{getBikeName(rec.component_id)}</td>
							<td class="px-4 py-3 text-gravel-700">{rec.work_performed}</td>
							<td class="px-4 py-3 text-right text-gravel-600 hidden sm:table-cell">
								{rec.cost != null ? `$${rec.cost.toFixed(2)}` : '—'}
							</td>
							<td class="px-4 py-3">
								<button
									class="text-red-400 hover:text-red-600 p-1 rounded hover:bg-red-50 transition-colors"
									onclick={() => handleDelete(rec)}
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
