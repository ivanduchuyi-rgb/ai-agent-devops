'use client';

import React, { useEffect, useState } from 'react';
import { fetchJSON, fmtNum, fmtDollar } from '@/lib/api';
import { Chart as ChartJS, registerables } from 'chart.js';
import { Chart } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';

ChartJS.register(...registerables);

interface Stats { total_trades: number; closed_trades: number; open_trades: number; last_trade_time: string | null; win_rate: number; total_pl: number; wins: number; losses: number; avg_win: number; avg_loss: number; best_trade: number; worst_trade: number; profit_factor: number; }
interface SymbolStats { symbol: string; count: number; }
interface SymbolWinRate { symbol: string; total: number; closed: number; win_rate: number; total_pl: number; }
interface ScoreDist { bucket: number; count: number; }
interface HourProfit { hour: number; profit: number; closed: number; }
interface CumProfit { time: string; profit: number; cumulative: number; }
interface RecentTrade { time: string | null; symbol: string; type: string; lot: number | null; open_price: number | null; close_price: number | null; profit: number | null; score: number | null; comment: string | null; }

export default function TradingPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [symbolCounts, setSymbolCounts] = useState<SymbolStats[]>([]);
  const [winRates, setWinRates] = useState<SymbolWinRate[]>([]);
  const [scores, setScores] = useState<ScoreDist[]>([]);
  const [hours, setHours] = useState<HourProfit[]>([]);
  const [cumProfit, setCumProfit] = useState<CumProfit[]>([]);
  const [trades, setTrades] = useState<RecentTrade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchJSON<Stats>('/api/stats'),
      fetchJSON<SymbolStats[]>('/api/trades-by-symbol'),
      fetchJSON<SymbolWinRate[]>('/api/win-rate-by-symbol'),
      fetchJSON<ScoreDist[]>('/api/score-distribution'),
      fetchJSON<HourProfit[]>('/api/profit-by-hour'),
      fetchJSON<CumProfit[]>('/api/cumulative-profit'),
      fetchJSON<RecentTrade[]>('/api/recent-trades?limit=20'),
    ]).then(([s, sc, wr, sd, hp, cp, rt]) => {
      setStats(s); setSymbolCounts(sc); setWinRates(wr);
      setScores(sd); setHours(hp); setCumProfit(cp); setTrades(rt);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-[#8899aa]">Loading...</div>;

  const COLORS = ['#22c55e','#3b82f6','#f59e0b','#ef4444','#8b5cf6','#ec4899'];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#c0d0e0]">Trading Analytics</h1>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Trades', value: fmtNum(stats?.total_trades ?? 0), sub: `${stats?.closed_trades ?? 0} closed / ${stats?.open_trades ?? 0} open` },
          { label: 'Win Rate', value: `${stats?.win_rate ?? 0}%`, color: (stats?.win_rate ?? 0) >= 50 ? 'text-green-400' : 'text-red-400', sub: `${stats?.wins ?? 0}W / ${stats?.losses ?? 0}L` },
          { label: 'Total P&L', value: fmtDollar(stats?.total_pl ?? 0), color: (stats?.total_pl ?? 0) >= 0 ? 'text-green-400' : 'text-red-400', sub: `PF: ${stats?.profit_factor ?? 0}` },
          { label: 'Best Trade', value: fmtDollar(stats?.best_trade ?? 0), color: 'text-green-400', sub: `Worst: ${fmtDollar(stats?.worst_trade ?? 0)}` },
        ].map((c, i) => (
          <div key={i} className="card">
            <div className="text-xs text-[#8899aa] uppercase">{c.label}</div>
            <div className={`text-2xl font-bold ${c.color || ''}`}>{c.value}</div>
            <div className="text-xs text-[#667]">{c.sub}</div>
          </div>
        ))}
      </div>

      {cumProfit.length > 0 && (
        <div className="card">
          <h2 className="text-sm font-semibold text-[#8899aa] uppercase mb-4">Cumulative Profit</h2>
          <div className="h-[280px]">
            <Chart type="line" data={{ labels: cumProfit.map(d => d.time), datasets: [{ label: 'P&L', data: cumProfit.map(d => d.cumulative), borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.08)', fill: true, tension: 0.3, pointRadius: 1 }] }}
              options={{ responsive: true, maintainAspectRatio: false, scales: { x: { type: 'time', time: { tooltipFormat: 'MMM d HH:mm' }, grid: { color: '#1d2533' }, ticks: { color: '#8899aa' } }, y: { grid: { color: '#1d2533' }, ticks: { color: '#8899aa', callback: (v: any) => '$'+v } } }, plugins: { legend: { display: false } } }} />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {symbolCounts.length > 0 && (
          <div className="card">
            <h2 className="text-sm font-semibold text-[#8899aa] uppercase mb-4">Trades by Symbol</h2>
            <div className="h-[220px]">
              <Chart type="pie" data={{ labels: symbolCounts.map(d => d.symbol), datasets: [{ data: symbolCounts.map(d => d.count), backgroundColor: COLORS, borderWidth: 0 }] }}
                options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#c0d0e0' } } } }} />
            </div>
          </div>
        )}
        {winRates.length > 0 && (
          <div className="card">
            <h2 className="text-sm font-semibold text-[#8899aa] uppercase mb-4">Win Rate by Symbol</h2>
            <div className="h-[220px]">
              <Chart type="bar" data={{ labels: winRates.map(d => d.symbol), datasets: [{ label: 'Win Rate %', data: winRates.map(d => d.closed > 0 ? d.win_rate : null), backgroundColor: winRates.map(d => d.win_rate >= 50 ? '#22c55e' : '#ef4444'), borderRadius: 4 }] }}
                options={{ responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100, grid: { color: '#1d2533' }, ticks: { color: '#8899aa' } }, x: { grid: { display: false }, ticks: { color: '#c0d0e0' } } }, plugins: { legend: { display: false } } }} />
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-sm font-semibold text-[#8899aa] uppercase mb-4">Recent Trades</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-[#8899aa] text-xs uppercase border-b border-[#2a3344]"><th className="pb-2 text-left">Time</th><th className="pb-2 text-left">Symbol</th><th className="pb-2 text-left">Type</th><th className="pb-2 text-left">P&L</th><th className="pb-2 text-left">Score</th></tr></thead>
            <tbody className="divide-y divide-[#1d2533]">
              {trades.map((t, i) => (
                <tr key={i} className="hover:bg-[#1a2233]">
                  <td className="py-2">{t.time ? new Date(t.time).toLocaleString() : '—'}</td>
                  <td className="py-2 font-bold">{t.symbol}</td>
                  <td className="py-2"><span className={`px-2 py-0.5 rounded text-[10px] font-bold ${t.type === 'BUY' ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'}`}>{t.type}</span></td>
                  <td className={`py-2 font-semibold ${t.profit != null ? (t.profit >= 0 ? 'text-green-400' : 'text-red-400') : ''}`}>{t.profit != null ? (t.profit >= 0 ? '+' : '') + fmtDollar(t.profit) : '—'}</td>
                  <td className="py-2 text-[#8899aa]">{t.score ?? '—'}</td>
                </tr>
              ))}
              {trades.length === 0 && <tr><td colSpan={5} className="py-8 text-center text-[#556]">No trades yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
