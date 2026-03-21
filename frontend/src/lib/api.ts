import type {
	Bike,
	Component,
	ComponentStatus,
	Ride,
	ServiceRecord,
	Token,
	User
} from './types';

const BASE = '/api';

function getToken(): string | null {
	if (typeof localStorage === 'undefined') return null;
	return localStorage.getItem('token');
}

function authHeaders(): Record<string, string> {
	const token = getToken();
	return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(
	method: string,
	path: string,
	body?: unknown,
	auth = true
): Promise<T> {
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(auth ? authHeaders() : {})
	};

	const res = await fetch(`${BASE}${path}`, {
		method,
		headers,
		body: body !== undefined ? JSON.stringify(body) : undefined
	});

	if (!res.ok) {
		const err = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(err.detail ?? 'Request failed');
	}

	if (res.status === 204) return undefined as T;
	return res.json();
}

// Auth
export const auth = {
	register: (data: { username: string; email: string; password: string; preferred_unit?: string }) =>
		request<User>('POST', '/auth/register', data, false),

	login: (email: string, password: string) =>
		request<Token>('POST', '/auth/login', { email, password }, false),

	me: () => request<User>('GET', '/auth/me')
};

// Bikes
export const bikes = {
	list: () => request<Bike[]>('GET', '/bikes'),
	get: (id: number) => request<Bike>('GET', `/bikes/${id}`),
	create: (data: { name: string; brand?: string; initial_odometer?: number }) =>
		request<Bike>('POST', '/bikes', data),
	update: (id: number, data: { name?: string; brand?: string; is_active?: boolean }) =>
		request<Bike>('PUT', `/bikes/${id}`, data),
	remove: (id: number) => request<void>('DELETE', `/bikes/${id}`)
};

// Rides
export const rides = {
	list: (bike_id?: number) =>
		request<Ride[]>('GET', bike_id ? `/rides?bike_id=${bike_id}` : '/rides'),
	get: (id: number) => request<Ride>('GET', `/rides/${id}`),
	create: (data: { bike_id: number; distance: number; date?: string; notes?: string }) =>
		request<Ride>('POST', '/rides', data),
	remove: (id: number) => request<void>('DELETE', `/rides/${id}`)
};

// Components
export const components = {
	list: (bike_id: number) => request<Component[]>('GET', `/components?bike_id=${bike_id}`),
	status: () => request<ComponentStatus[]>('GET', '/components/status'),
	create: (data: {
		bike_id: number;
		part_type: string;
		brand_model?: string;
		distance_at_install?: number;
		lifespan_limit?: number;
	}) => request<Component>('POST', '/components', data),
	patch: (
		id: number,
		data: { brand_model?: string; lifespan_limit?: number; is_active?: boolean }
	) => request<Component>('PATCH', `/components/${id}`, data),
	remove: (id: number) => request<void>('DELETE', `/components/${id}`)
};

// Service
export const service = {
	list: (component_id: number) => request<ServiceRecord[]>('GET', `/service/${component_id}`),
	create: (data: {
		component_id: number;
		work_performed: string;
		service_date?: string;
		cost?: number;
	}) => request<ServiceRecord>('POST', '/service', data),
	remove: (id: number) => request<void>('DELETE', `/service/${id}`)
};
