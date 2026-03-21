import type { PreferredUnit } from './types';

export function formatDistance(km: number, unit: PreferredUnit): string {
	if (unit === 'Miles') {
		return `${(km * 0.621371).toFixed(1)} mi`;
	}
	return `${km.toFixed(1)} km`;
}

export function formatDate(iso: string): string {
	return new Date(iso).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

export function wearColor(pct: number): 'green' | 'yellow' | 'red' {
	if (pct >= 100) return 'red';
	if (pct >= 75) return 'yellow';
	return 'green';
}

export function wearLabel(pct: number): string {
	if (pct >= 100) return 'Replace';
	if (pct >= 75) return 'Check Soon';
	return 'Good';
}
