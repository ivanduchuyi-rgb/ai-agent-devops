'use client';

import React, { useEffect, useState } from 'react';
import { fetchJSON, fmtNum, fmtDollar, Stats, SystemData, ServiceStatus, RecentTrade } from '@/lib/api';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [system, setSystem] = useState<SystemData | null>(null);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [trades, setTrades] = useState<RecentTrade[]>([]);
  const [lastUpdated, setLastUpdated] = useState('');

  const loadData = async () => {
    try {
      const [s, sys, svc, t] = await Promise.all([
        fetchJSON<Stats>('/api/stats'),
        fetchJSON<SystemData>('/api/system'),
        fetchJSON<ServiceStatus[]>('/api/services'),
        fetchJSON<RecentTrade[]>('/api/recent-trades?limit=10'),
      ]);
      setStats(s); setSystem(sys); setServices(svc); setTrades(t);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (e) { console.error(e); }
  };

  useEffect(() => { loadData(); const id = setInterval(loadData, 30000); return () => clearInterval(id); }, []);

  const plColor = stats && stats.total_pl >= 0 ? 'text-green-400' : 'text-red-400';
  const servicesUp = services.filter(s => s.status === 'up').length;

  return (
    <div className="space-y-6">
      {/* System strip */}
      <div className="flex flex-wrap gap-4 p-3 bg-[#141a23] border border-[#2a3344] rounded-xl text-sm">
        {system?.cpu != null && <span className="text-[#8899aa]">CPU <b className="text-white">{system.cpu}%</b></span>}
        {system?.memory && <span className="text-[#8899aa]">RAM <b className="text-white">{system.memory.used}/{system.memory.total}G</b></span>}
        {system?.disk && <span className="text-[#8899aa]">Disk <b className="text-white">{system.disk.percent}%</b></span>}
        {system?.uptime && <span className="text-[#8899aa]">Uptime <b className="text-white">{system.uptime.days}d {system.uptime.hours}h</b></span>}
        <span className="text-[#8899aa]">Services <b className={servicesUp === services.length ? 'text-green-400' : 'text-yellow-400'}>{servicesUp}/{services.length}</b></span>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">Total Trades</div>
          <div className="text-2xl font-bold">{fmtNum(stats?.total_trades ?? 0)}</div>
          <div className="text-xs text-[#667]">{stats?.closed_trades ?? 0} closed / {stats?.open_trades ?? 0} open</div>
        </div>
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">Win Rate</div>
          <div className={"text-2xl font-bold " + ((stats?.win_rate ?? 0) >= 50 ? 'text-green-400' : 'text-red-400')}>{stats?.win_rate ?? 0}%</div>
          <div className="text-xs text-[#667]">{stats?.wins ?? 0}W / {stats?.losses ?? 0}L</div>
        </div>
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">Total P&L</div>
          <div className={"text-2xl font-bold " + plColor}>{fmtDollar(stats?.total_pl ?? 0)}</div>
          <div className="text-xs text-[#667]">PF: {stats?.profit_factor ?? 0}</div>
        </div>
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">Bot Status</div>
          <div className="text-2xl font-bold text-green-400">Online</div>
          <div className="text-xs text-[#667]">{stats?.last_trade_time ? new Date(stats.last_trade_time).toLocaleTimeString() : 'No trades yet'}</div>
        </div>
      </div>

      {/* Recent Trades */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-sm font-semibold text-[#8899aa] uppercase">Recent Trades</h2>
          <a href="/trading" className="text-[#00d2ff] text-xs">View all →</a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[#8899aa] text-xs uppercase border-b border-[#2a3344]">
                <th className="pb-2 text-left">Time</th><th className="pb-2 text-left">Symbol</th>
                <th className="pb-2 text-left">Type</th><th className="pb-2 text-left">P&L</th>
                <th className="pb-2 text-left">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1d2533]">
              {trades.map((t, i) => (
                <tr key={i} className="hover:bg-[#1a2233]">
                  <td className="py-2">{t.time ? new Date(t.time).toLocaleString() : '—'}</td>
                  <td className="py-2 font-bold">{t.symbol}</td>
                  <td className="py-2"><span className={"px-2 py-0.5 rounded text-[10px] font-bold " + (t.type === 'BUY' ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400')}>{t.type}</span></td>
                  <td className={"py-2 font-semibold " + (t.profit != null ? (t.profit >= 0 ? 'text-green-400' : 'text-red-400') : '')}>{t.profit != null ? (t.profit >= 0 ? '+' : '') + fmtDollar(t.profit) : '—'}</td>
                  <td className="py-2 text-[#8899aa]">{t.score ?? '—'}</td>
                </tr>
              ))}
              {trades.length === 0 && <tr><td colSpan={5} className="py-8 text-center text-[#556]">No trades yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
      <div className="text-right text-xs text-[#556]">Updated: {lastUpdated}</div>
    </div>
  );
}
