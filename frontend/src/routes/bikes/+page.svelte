<script lang="ts">
	import { onMount } from 'svelte';
	import { bikes as bikesApi } from '$lib/api';
	import { authStore } from '$lib/auth.svelte';
	import { formatDistance } from '$lib/utils';
	import type { Bike } from '$lib/types';
	import { Bike as BikeIcon, Plus, Pencil, Trash2, ArrowRight } from 'lucide-svelte';

	let bikeList = $state<Bike[]>([]);
	let loading = $state(true);
	let showForm = $state(false);
	let editBike = $state<Bike | null>(null);
	let error = $state('');

	// Form state
	let formName = $state('');
	let formBrand = $state('');
	let formOdometer = $state(0);
	let formActive = $state(true);
	let submitting = $state(false);

	const unit = $derived(authStore.user?.preferred_unit ?? 'KM');

	onMount(async () => {
		try {
			bikeList = await bikesApi.list();
		} finally {
			loading = false;
		}
	});

	function openCreate() {
		editBike = null;
		formName = '';
		formBrand = '';
		formOdometer = 0;
		formActive = true;
		showForm = true;
	}

	function openEdit(bike: Bike) {
		editBike = bike;
		formName = bike.name;
		formBrand = bike.brand ?? '';
		formOdometer = bike.total_odometer;
		formActive = bike.is_active;
		showForm = true;
	}

	function closeForm() {
		showForm = false;
		editBike = null;
		error = '';
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = '';
		submitting = true;
		try {
			if (editBike) {
				const updated = await bikesApi.update(editBike.id, {
					name: formName,
					brand: formBrand || undefined,
					is_active: formActive
				});
				bikeList = bikeList.map((b) => (b.id === updated.id ? updated : b));
			} else {
				const created = await bikesApi.create({
					name: formName,
					brand: formBrand || undefined,
					initial_odometer: formOdometer
				});
				bikeList = [...bikeList, created];
			}
			closeForm();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to save bike';
		} finally {
			submitting = false;
		}
	}

	async function handleDelete(bike: Bike) {
		if (!confirm(`Delete "${bike.name}"? This will also delete all rides and components.`)) return;
		try {
			await bikesApi.remove(bike.id);
			bikeList = bikeList.filter((b) => b.id !== bike.id);
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Delete failed');
		}
	}
</script>

<svelte:head>
	<title>Bikes — GravelLog</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-2xl font-bold text-gravel-900">My Bikes</h1>
		<button class="btn-primary" onclick={openCreate}>
			<Plus size={16} /> Add Bike
		</button>
	</div>

	{#if loading}
		<div class="text-center py-12 text-gravel-400">Loading…</div>
	{:else if bikeList.length === 0}
		<div class="card text-center py-12">
			<BikeIcon size={40} class="text-gravel-300 mx-auto mb-3" />
			<p class="text-gravel-500 mb-4">No bikes in your garage yet.</p>
			<button class="btn-primary" onclick={openCreate}><Plus size={16} /> Add your first bike</button>
		</div>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each bikeList as bike}
				<div class="card hover:shadow-md transition-shadow">
					<div class="flex items-start justify-between mb-3">
						<div class="flex items-center gap-2">
							<BikeIcon size={20} class="text-gravel-600 mt-0.5" />
							<div>
								<h3 class="font-semibold text-gravel-900">{bike.name}</h3>
								{#if bike.brand}
									<p class="text-xs text-gravel-400">{bike.brand}</p>
								{/if}
							</div>
						</div>
						<span class="badge {bike.is_active ? 'badge-green' : 'badge-gray'}">
							{bike.is_active ? 'Active' : 'Retired'}
						</span>
					</div>

					<p class="text-2xl font-bold text-gravel-800 mb-4">
						{formatDistance(bike.total_odometer, unit)}
					</p>

					<div class="flex items-center gap-2 pt-3 border-t border-gravel-100">
						<a href="/bikes/{bike.id}" class="btn-secondary flex-1 justify-center text-xs">
							Details <ArrowRight size={13} />
						</a>
						<button class="btn-ghost px-2" onclick={() => openEdit(bike)}>
							<Pencil size={15} />
						</button>
						<button class="btn-ghost px-2 text-red-500 hover:bg-red-50" onclick={() => handleDelete(bike)}>
							<Trash2 size={15} />
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Modal -->
{#if showForm}
	<div
		class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
		role="dialog"
		aria-modal="true"
	>
		<div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
			<h2 class="text-lg font-semibold text-gravel-900 mb-5">
				{editBike ? 'Edit Bike' : 'Add New Bike'}
			</h2>

			{#if error}
				<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
					{error}
				</div>
			{/if}

			<form onsubmit={handleSubmit} class="space-y-4">
				<div>
					<label class="label" for="bike-name">Name *</label>
					<input id="bike-name" class="input" bind:value={formName} required placeholder="Canyon Grizl" />
				</div>
				<div>
					<label class="label" for="bike-brand">Brand</label>
					<input id="bike-brand" class="input" bind:value={formBrand} placeholder="Canyon" />
				</div>
				{#if !editBike}
					<div>
						<label class="label" for="bike-odo">Initial Odometer ({unit})</label>
						<input
							id="bike-odo"
							type="number"
							min="0"
							step="0.1"
							class="input"
							bind:value={formOdometer}
						/>
					</div>
				{:else}
					<div class="flex items-center gap-2">
						<input id="bike-active" type="checkbox" bind:checked={formActive} class="rounded" />
						<label for="bike-active" class="text-sm text-gravel-700">Active</label>
					</div>
				{/if}

				<div class="flex gap-3 pt-2">
					<button type="button" class="btn-secondary flex-1 justify-center" onclick={closeForm}>
						Cancel
					</button>
					<button type="submit" class="btn-primary flex-1 justify-center" disabled={submitting}>
						{submitting ? 'Saving…' : editBike ? 'Save Changes' : 'Add Bike'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
