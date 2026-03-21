<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { bikes as bikesApi, rides as ridesApi, components as componentsApi } from '$lib/api';
	import { authStore } from '$lib/auth.svelte';
	import { formatDistance, formatDate, wearColor, wearLabel } from '$lib/utils';
	import type { Bike, Ride, Component } from '$lib/types';
	import { ArrowLeft, Plus, Trash2, Settings } from 'lucide-svelte';

	const bikeId = $derived(Number($page.params.id));
	const unit = $derived(authStore.user?.preferred_unit ?? 'KM');

	let bike = $state<Bike | null>(null);
	let rideList = $state<Ride[]>([]);
	let componentList = $state<Component[]>([]);
	let loading = $state(true);

	// Ride form
	let showRideForm = $state(false);
	let rideDistance = $state(0);
	let rideDate = $state(new Date().toISOString().substring(0, 10));
	let rideNotes = $state('');
	let rideSaving = $state(false);
	let rideError = $state('');

	// Component form
	let showCompForm = $state(false);
	let compType = $state('');
	let compBrand = $state('');
	let compLimit = $state<number | ''>('');
	let compSaving = $state(false);
	let compError = $state('');

	onMount(async () => {
		try {
			[bike, rideList, componentList] = await Promise.all([
				bikesApi.get(bikeId),
				ridesApi.list(bikeId),
				componentsApi.list(bikeId)
			]);
		} finally {
			loading = false;
		}
	});

	async function logRide(e: SubmitEvent) {
		e.preventDefault();
		rideError = '';
		rideSaving = true;
		try {
			const created = await ridesApi.create({
				bike_id: bikeId,
				distance: rideDistance,
				date: rideDate ? new Date(rideDate).toISOString() : undefined,
				notes: rideNotes || undefined
			});
			rideList = [created, ...rideList];
			bike = await bikesApi.get(bikeId);
			componentList = await componentsApi.list(bikeId);
			showRideForm = false;
			rideDistance = 0;
			rideNotes = '';
		} catch (err) {
			rideError = err instanceof Error ? err.message : 'Failed to log ride';
		} finally {
			rideSaving = false;
		}
	}

	async function deleteRide(rid: Ride) {
		if (!confirm('Delete this ride? Odometer and component wear will be reverted.')) return;
		await ridesApi.remove(rid.id);
		rideList = rideList.filter((r) => r.id !== rid.id);
		bike = await bikesApi.get(bikeId);
		componentList = await componentsApi.list(bikeId);
	}

	async function addComponent(e: SubmitEvent) {
		e.preventDefault();
		compError = '';
		compSaving = true;
		try {
			const created = await componentsApi.create({
				bike_id: bikeId,
				part_type: compType,
				brand_model: compBrand || undefined,
				distance_at_install: bike?.total_odometer ?? 0,
				lifespan_limit: compLimit !== '' ? Number(compLimit) : undefined
			});
			componentList = [...componentList, created];
			showCompForm = false;
			compType = '';
			compBrand = '';
			compLimit = '';
		} catch (err) {
			compError = err instanceof Error ? err.message : 'Failed to add component';
		} finally {
			compSaving = false;
		}
	}

	async function toggleComponent(comp: Component) {
		const updated = await componentsApi.patch(comp.id, { is_active: !comp.is_active });
		componentList = componentList.map((c) => (c.id === updated.id ? updated : c));
	}

	function getBadgeClass(pct: number) {
		const c = wearColor(pct);
		if (c === 'red') return 'badge-red';
		if (c === 'yellow') return 'badge-yellow';
		return 'badge-green';
	}
</script>

<svelte:head>
	<title>{bike?.name ?? 'Bike'} — GravelLog</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center gap-3">
		<a href="/bikes" class="btn-ghost px-2"><ArrowLeft size={18} /></a>
		<div>
			<h1 class="text-2xl font-bold text-gravel-900">{loading ? '…' : bike?.name}</h1>
			{#if bike?.brand}
				<p class="text-sm text-gravel-500">{bike.brand}</p>
			{/if}
		</div>
	</div>

	{#if loading}
		<div class="text-center py-12 text-gravel-400">Loading…</div>
	{:else if bike}
		<!-- Stats row -->
		<div class="grid grid-cols-2 gap-4">
			<div class="card text-center">
				<p class="text-3xl font-bold text-gravel-900">{formatDistance(bike.total_odometer, unit)}</p>
				<p class="text-sm text-gravel-500 mt-1">Total Distance</p>
			</div>
			<div class="card text-center">
				<p class="text-3xl font-bold text-gravel-900">{rideList.length}</p>
				<p class="text-sm text-gravel-500 mt-1">Rides Logged</p>
			</div>
		</div>

		<!-- Components -->
		<div class="card">
			<div class="flex items-center justify-between mb-4">
				<h2 class="font-semibold text-gravel-800">Components</h2>
				<button class="btn-secondary text-xs" onclick={() => (showCompForm = !showCompForm)}>
					<Plus size={14} /> Add Part
				</button>
			</div>

			{#if showCompForm}
				<form onsubmit={addComponent} class="mb-4 p-4 bg-gravel-50 rounded-lg space-y-3 border border-gravel-200">
					{#if compError}
						<p class="text-sm text-red-600">{compError}</p>
					{/if}
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="label" for="comp-type">Part Type *</label>
							<input id="comp-type" class="input" bind:value={compType} required placeholder="Chain" />
						</div>
						<div>
							<label class="label" for="comp-brand">Brand / Model</label>
							<input id="comp-brand" class="input" bind:value={compBrand} placeholder="KMC X12" />
						</div>
					</div>
					<div>
						<label class="label" for="comp-limit">Lifespan Limit ({unit})</label>
						<input id="comp-limit" type="number" min="0" class="input" bind:value={compLimit} placeholder="3000" />
					</div>
					<div class="flex gap-2">
						<button type="button" class="btn-secondary flex-1 justify-center text-xs" onclick={() => (showCompForm = false)}>Cancel</button>
						<button type="submit" class="btn-primary flex-1 justify-center text-xs" disabled={compSaving}>
							{compSaving ? 'Adding…' : 'Add Component'}
						</button>
					</div>
				</form>
			{/if}

			{#if componentList.length === 0}
				<p class="text-sm text-gravel-400 text-center py-4">No components tracked yet.</p>
			{:else}
				<div class="space-y-3">
					{#each componentList as comp}
						{@const pct = comp.lifespan_limit ? (comp.current_distance / comp.lifespan_limit) * 100 : null}
						<div class="flex items-center gap-3 py-2 border-b border-gravel-50 last:border-0">
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-2 flex-wrap">
									<p class="text-sm font-medium text-gravel-900">{comp.part_type}</p>
									{#if comp.brand_model}
										<span class="text-xs text-gravel-400">{comp.brand_model}</span>
									{/if}
									{#if pct !== null}
										<span class="badge {getBadgeClass(pct)}">{wearLabel(pct)} · {pct.toFixed(0)}%</span>
									{/if}
									{#if !comp.is_active}
										<span class="badge badge-gray">Retired</span>
									{/if}
								</div>
								<p class="text-xs text-gravel-400 mt-0.5">
									{formatDistance(comp.current_distance, unit)}
									{#if comp.lifespan_limit} / {formatDistance(comp.lifespan_limit, unit)}{/if}
								</p>
								{#if pct !== null}
									<div class="w-full bg-gravel-100 rounded-full h-1.5 mt-1.5">
										<div
											class="h-1.5 rounded-full {pct >= 100 ? 'bg-red-500' : pct >= 75 ? 'bg-yellow-500' : 'bg-green-500'}"
											style="width: {Math.min(pct, 100)}%"
										></div>
									</div>
								{/if}
							</div>
							<div class="flex items-center gap-1 shrink-0">
								<a href="/service?component_id={comp.id}" class="btn-ghost px-1.5 py-1" title="Service history">
									<Settings size={14} />
								</a>
								<button
									class="btn-ghost px-1.5 py-1 text-xs"
									onclick={() => toggleComponent(comp)}
									title={comp.is_active ? 'Retire' : 'Reactivate'}
								>
									{comp.is_active ? '⏸' : '▶'}
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Rides -->
		<div class="card">
			<div class="flex items-center justify-between mb-4">
				<h2 class="font-semibold text-gravel-800">Ride Log</h2>
				<button class="btn-primary text-xs" onclick={() => (showRideForm = !showRideForm)}>
					<Plus size={14} /> Log Ride
				</button>
			</div>

			{#if showRideForm}
				<form onsubmit={logRide} class="mb-4 p-4 bg-gravel-50 rounded-lg space-y-3 border border-gravel-200">
					{#if rideError}
						<p class="text-sm text-red-600">{rideError}</p>
					{/if}
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="label" for="ride-dist">Distance ({unit}) *</label>
							<input id="ride-dist" type="number" min="0.1" step="0.1" class="input" bind:value={rideDistance} required />
						</div>
						<div>
							<label class="label" for="ride-date">Date</label>
							<input id="ride-date" type="date" class="input" bind:value={rideDate} />
						</div>
					</div>
					<div>
						<label class="label" for="ride-notes">Notes</label>
						<input id="ride-notes" class="input" bind:value={rideNotes} placeholder="Morning gravel grind…" />
					</div>
					<div class="flex gap-2">
						<button type="button" class="btn-secondary flex-1 justify-center text-xs" onclick={() => (showRideForm = false)}>Cancel</button>
						<button type="submit" class="btn-primary flex-1 justify-center text-xs" disabled={rideSaving}>
							{rideSaving ? 'Logging…' : 'Log Ride'}
						</button>
					</div>
				</form>
			{/if}

			{#if rideList.length === 0}
				<p class="text-sm text-gravel-400 text-center py-4">No rides logged yet.</p>
			{:else}
				<div class="divide-y divide-gravel-100">
					{#each rideList.slice().sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()) as ride}
						<div class="flex items-center justify-between py-3">
							<div>
								<p class="text-sm font-medium text-gravel-800">{formatDistance(ride.distance, unit)}</p>
								<p class="text-xs text-gravel-400">{formatDate(ride.date)}</p>
								{#if ride.notes}
									<p class="text-xs text-gravel-500 mt-0.5 italic">{ride.notes}</p>
								{/if}
							</div>
							<button
								class="btn-ghost px-2 text-red-400 hover:bg-red-50"
								onclick={() => deleteRide(ride)}
							>
								<Trash2 size={14} />
							</button>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
