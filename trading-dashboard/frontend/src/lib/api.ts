const API_BASE = '/api';

export async function fetchJSON<T = any>(url: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP error! status: ${res.status}`);
  }
  return res.json();
}

export function fmtNum(n: any): string {
  if (n === null || n === undefined || isNaN(Number(n))) return '—';
  return Number(n).toLocaleString('en-US', { maximumFractionDigits: 2 });
}

export function fmtDollar(n: any): string {
  if (n === null || n === undefined || isNaN(Number(n))) return '—';
  return Number(n).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  });
}

export interface Stats {
  total_trades: number;
  closed_trades: number;
  open_trades: number;
  last_trade_time: string | null;
  win_rate: number;
  total_pl: number;
  wins: number;
  losses: number;
  avg_win: number;
  avg_loss: number;
  best_trade: number;
  worst_trade: number;
  profit_factor: number;
}

export interface TradeBySymbol {
  symbol: string;
  count: number;
}

export interface WinRateBySymbol {
  symbol: string;
  total: number;
  closed: number;
  win_rate: number;
  total_pl: number;
}

export interface RecentTrade {
  time: string | null;
  symbol: string;
  type: string;
  lot: number | null;
  open_price: number | null;
  close_price: number | null;
  profit: number | null;
  score: number | null;
  comment: string | null;
}

export interface SystemData {
  cpu: number | null;
  memory: {
    total: number;
    used: number;
    available: number;
    free: number;
    percent: number;
  } | null;
  load: {
    '1m': number;
    '5m': number;
    '15m': number;
  } | null;
  uptime: {
    seconds: number;
    days: number;
    hours: number;
  };
  disk: {
    total: number;
    free: number;
    used: number;
    percent: number;
  } | null;
  disk_data: {
    total: number;
    free: number;
    used: number;
    percent: number;
  } | null;
  network: {
    rx_bytes: number;
    tx_bytes: number;
    rx_kbps: number;
    tx_kbps: number;
  } | null;
  processes: number | null;
  note?: string;
}

export interface ServiceStatus {
  name: string;
  status: 'up' | 'down';
  code?: number;
  error?: string;
}

export interface UploadedFile {
  name: string;
  size: number;
  mtime: string;
  key: string;
}

export interface PresignedPutResponse {
  uploadUrl: string;
  fileKey: string;
  filename: string;
  expiresIn: number;
  method: string;
  headers: Record<string, string>;
}
