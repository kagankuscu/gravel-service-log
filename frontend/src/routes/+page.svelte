<script lang="ts">
	import { onMount } from 'svelte';
	import { bikes as bikesApi, components as componentsApi } from '$lib/api';
	import { authStore } from '$lib/auth.svelte';
	import { formatDistance, wearColor, wearLabel } from '$lib/utils';
	import type { Bike, ComponentStatus } from '$lib/types';
	import { Bike as BikeIcon, AlertTriangle, CheckCircle, Activity, ArrowRight } from 'lucide-svelte';

	let bikeList = $state<Bike[]>([]);
	let statuses = $state<ComponentStatus[]>([]);
	let loadingBikes = $state(true);
	let loadingStatus = $state(true);

	const unit = $derived(authStore.user?.preferred_unit ?? 'KM');

	const criticalCount = $derived(statuses.filter((s) => (s.wear_percentage ?? 0) >= 100).length);
	const warningCount = $derived(
		statuses.filter((s) => {
			const pct = s.wear_percentage ?? 0;
			return pct >= 75 && pct < 100;
		}).length
	);

	onMount(async () => {
		[bikeList, statuses] = await Promise.all([
			bikesApi.list().finally(() => (loadingBikes = false)),
			componentsApi.status().finally(() => (loadingStatus = false))
		]);
	});

	function getBadgeClass(pct: number) {
		const c = wearColor(pct);
		if (c === 'red') return 'badge-red';
		if (c === 'yellow') return 'badge-yellow';
		return 'badge-green';
	}
</script>

<svelte:head>
	<title>Dashboard — GravelLog</title>
</svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-bold text-gravel-900">Dashboard</h1>
		<p class="text-sm text-gravel-500 mt-0.5">Welcome back, {authStore.user?.username}</p>
	</div>

	<!-- Summary cards -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		<div class="card flex items-center gap-4">
			<div class="w-10 h-10 bg-gravel-100 rounded-lg flex items-center justify-center shrink-0">
				<BikeIcon size={20} class="text-gravel-700" />
			</div>
			<div>
				<p class="text-2xl font-bold text-gravel-900">
					{loadingBikes ? '…' : bikeList.filter((b) => b.is_active).length}
				</p>
				<p class="text-sm text-gravel-500">Active Bikes</p>
			</div>
		</div>

		<div class="card flex items-center gap-4">
			<div class="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center shrink-0">
				<AlertTriangle size={20} class="text-red-600" />
			</div>
			<div>
				<p class="text-2xl font-bold text-gravel-900">{loadingStatus ? '…' : criticalCount}</p>
				<p class="text-sm text-gravel-500">Parts to Replace</p>
			</div>
		</div>

		<div class="card flex items-center gap-4">
			<div class="w-10 h-10 bg-yellow-50 rounded-lg flex items-center justify-center shrink-0">
				<Activity size={20} class="text-yellow-600" />
			</div>
			<div>
				<p class="text-2xl font-bold text-gravel-900">{loadingStatus ? '…' : warningCount}</p>
				<p class="text-sm text-gravel-500">Check Soon</p>
			</div>
		</div>
	</div>

	<!-- Bikes overview -->
	<div class="card">
		<div class="flex items-center justify-between mb-4">
			<h2 class="font-semibold text-gravel-800">Your Bikes</h2>
			<a href="/bikes" class="text-sm text-gravel-600 hover:text-gravel-800 flex items-center gap-1">
				View all <ArrowRight size={14} />
			</a>
		</div>

		{#if loadingBikes}
			<div class="text-sm text-gravel-400 py-4 text-center">Loading…</div>
		{:else if bikeList.length === 0}
			<div class="text-center py-8">
				<BikeIcon size={32} class="text-gravel-300 mx-auto mb-2" />
				<p class="text-sm text-gravel-500">No bikes yet.</p>
				<a href="/bikes" class="btn-primary mt-3 inline-flex">Add your first bike</a>
			</div>
		{:else}
			<div class="divide-y divide-gravel-100">
				{#each bikeList.slice(0, 5) as bike}
					<a
						href="/bikes/{bike.id}"
						class="flex items-center justify-between py-3 hover:bg-gravel-50 -mx-2 px-2 rounded-lg transition-colors"
					>
						<div class="flex items-center gap-3">
							<BikeIcon size={18} class="text-gravel-500" />
							<div>
								<p class="text-sm font-medium text-gravel-900">{bike.name}</p>
								{#if bike.brand}
									<p class="text-xs text-gravel-400">{bike.brand}</p>
								{/if}
							</div>
						</div>
						<div class="text-right">
							<p class="text-sm font-semibold text-gravel-700">
								{formatDistance(bike.total_odometer, unit)}
							</p>
							<span class="badge {bike.is_active ? 'badge-green' : 'badge-gray'}">
								{bike.is_active ? 'Active' : 'Retired'}
							</span>
						</div>
					</a>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Component wear alerts -->
	<div class="card">
		<div class="flex items-center justify-between mb-4">
			<h2 class="font-semibold text-gravel-800">Component Wear</h2>
			<a
				href="/components"
				class="text-sm text-gravel-600 hover:text-gravel-800 flex items-center gap-1"
			>
				Manage <ArrowRight size={14} />
			</a>
		</div>

		{#if loadingStatus}
			<div class="text-sm text-gravel-400 py-4 text-center">Loading…</div>
		{:else if statuses.length === 0}
			<div class="text-center py-8">
				<CheckCircle size={32} class="text-green-400 mx-auto mb-2" />
				<p class="text-sm text-gravel-500">No components tracked yet.</p>
			</div>
		{:else}
			<div class="space-y-3">
				{#each statuses.sort((a, b) => (b.wear_percentage ?? 0) - (a.wear_percentage ?? 0)) as comp}
					{@const pct = comp.wear_percentage ?? 0}
					<div class="flex items-center gap-3">
						<div class="flex-1 min-w-0">
							<div class="flex items-center justify-between mb-1">
								<p class="text-sm font-medium text-gravel-800 truncate">
									{comp.part_type}
									{#if comp.brand_model}
										<span class="text-gravel-400 font-normal">· {comp.brand_model}</span>
									{/if}
								</p>
								<span class="badge {getBadgeClass(pct)} ml-2 shrink-0">
									{wearLabel(pct)} · {pct.toFixed(0)}%
								</span>
							</div>
							<div class="w-full bg-gravel-100 rounded-full h-1.5">
								<div
									class="h-1.5 rounded-full transition-all {pct >= 100
										? 'bg-red-500'
										: pct >= 75
											? 'bg-yellow-500'
											: 'bg-green-500'}"
									style="width: {Math.min(pct, 100)}%"
								></div>
							</div>
							<p class="text-xs text-gravel-400 mt-1">
								{formatDistance(comp.current_distance, unit)} of {formatDistance(
									comp.lifespan_limit ?? 0,
									unit
								)}
							</p>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
