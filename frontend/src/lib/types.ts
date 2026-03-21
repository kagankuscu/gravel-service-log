export type PreferredUnit = 'KM' | 'Miles';

export interface User {
	id: number;
	username: string;
	email: string;
	preferred_unit: PreferredUnit;
}

export interface Token {
	access_token: string;
	token_type: string;
}

export interface Bike {
	id: number;
	name: string;
	brand: string | null;
	total_odometer: number;
	is_active: boolean;
}

export interface Ride {
	id: number;
	bike_id: number;
	date: string;
	distance: number;
	notes: string | null;
}

export interface Component {
	id: number;
	bike_id: number;
	part_type: string;
	brand_model: string | null;
	distance_at_install: number;
	current_distance: number;
	lifespan_limit: number | null;
	is_active: boolean;
}

export interface ComponentStatus extends Component {
	wear_percentage: number | null;
}

export interface ServiceRecord {
	id: number;
	component_id: number;
	service_date: string;
	work_performed: string;
	cost: number | null;
}
