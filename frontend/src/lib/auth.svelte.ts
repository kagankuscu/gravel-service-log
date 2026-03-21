import type { User } from './types';
import { auth as authApi } from './api';

function createAuthStore() {
	let user = $state<User | null>(null);
	let loading = $state(true);
	let token = $state<string | null>(null);

	async function init() {
		if (typeof localStorage === 'undefined') {
			loading = false;
			return;
		}
		const stored = localStorage.getItem('token');
		if (!stored) {
			loading = false;
			return;
		}
		token = stored;
		try {
			user = await authApi.me();
		} catch {
			localStorage.removeItem('token');
			token = null;
		} finally {
			loading = false;
		}
	}

	async function login(email: string, password: string) {
		const res = await authApi.login(email, password);
		localStorage.setItem('token', res.access_token);
		token = res.access_token;
		user = await authApi.me();
	}

	function logout() {
		localStorage.removeItem('token');
		token = null;
		user = null;
	}

	return {
		get user() { return user; },
		get loading() { return loading; },
		get token() { return token; },
		get isAuthenticated() { return !!user; },
		init,
		login,
		logout
	};
}

export const authStore = createAuthStore();
