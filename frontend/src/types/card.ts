export interface CardBase {
  player_name: string;
  year?: number;
  brand?: string;
  card_number?: string;
  set_name?: string;
  sport?: string;
  condition?: string;
  notes?: string;
}

export interface CardCreate extends CardBase {}

export interface Card extends CardBase {
  id: number;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface CardPrice {
  card_id: number;
  average_price: number;
  low_price?: number;
  high_price?: number;
  last_updated: string;
  sources: string[];
}
