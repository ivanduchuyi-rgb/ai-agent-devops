'use client';

import React, { useState, useEffect } from 'react';
import { fetchJSON } from '@/lib/api';

interface Config {
  symbols: string;
  max_risk: number;
  lot_size: number;
  strategy: string;
  max_spread: number;
  email: string;
  telegram_token: string;
  telegram_chat: string;
  alert_on_loss: number;
  alert_interval: number;
}

export default function SettingsPage() {
  const [config, setConfig] = useState<Partial<Config>>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    // In a real app, load config from API
    // setConfig(await fetchJSON('/api/settings'));
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (!res.ok) throw new Error(await res.text());
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (e: any) {
      setMessage({ type: 'error', text: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-[#c0d0e0]">Settings</h1>

      {message && (
        <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-[#8899aa] uppercase">Trading Configuration</h2>
          <div>
            <label className="block text-xs text-[#667] mb-1">Active Symbols</label>
            <input 
              type="text" 
              value={config.symbols || ''} 
              onChange={(e) => setConfig({...config, symbols: e.target.value})}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm text-[#c0d0e0] outline-none focus:border-[#00d2ff]"
              placeholder="BTCUSD,GOLD"
            />
          </div>
          <div>
            <label className="block text-xs text-[#667] mb-1">Max Risk (%)</label>
            <input 
              type="number" 
              step="0.1" 
              value={config.max_risk || 0} 
              onChange={(e) => setConfig({...config, max_risk: parseFloat(e.target.value)})}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm text-[#c0d0e0] outline-none focus:border-[#00d2ff]"
            />
          </div>
          <div>
            <label className="block text-xs text-[#667] mb-1">Lot Size</label>
            <input 
              type="number" 
              step="0.01" 
              value={config.lot_size || 0} 
              onChange={(e) => setConfig({...config, lot_size: parseFloat(e.target.value)})}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm text-[#c0d0e0] outline-none focus:border-[#00d2ff]"
            />
          </div>
          <div>
            <label className="block text-xs text-[#667] mb-1">Strategy</label>
            <select 
              value={config.strategy || ''} 
              onChange={(e) => setConfig({...config, strategy: e.target.value})}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm text-[#c0d0e0] outline-none focus:border-[#00d2ff]"
            >
              <option value="">Select...</option>
              <option value="Momentum">Momentum</option>
              <option value="Mean Reversion">Mean Reversion</option>
              <option value="Trend Following">Trend Following</option>
              <option value="Scalping">Scalping</option>
            </select>
          </div>
          <button 
            onClick={handleSave}
            disabled={loading}
            className="w-full bg-[#00d2ff] text-[#0a0e1a] font-bold py-2 rounded mt-4 hover:opacity-80 disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save Trading Settings'}
          </button>
        </div>

        <div className="card space-y-4">
          <h2 className="text-sm font-semibold text-[#8899aa] uppercase">Alert Configuration</h2>
          <div>
            <label className="block text-xs text-[#667] mb-1">Email Notifications</label>
            <input 
              type="email" 
              value={config.email || ''} 
              onChange={(e) => setConfig({...config, email: e.target.value})}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm text-[#c0d0e0] outline-none focus:border-[#00d2ff]"
              placeholder="admin@example.com"
            />
          </div>
          <div>
            <label className="block text-xs text-[#667] mb-1">Telegram Bot Token</label>
            <input 
              type="password" 
              value={config.telegram_token || ''} 
              onChange={(e) => setConfig({...config, telegram_token: e.target.value})}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm text-[#c0d0e0] outline-none focus:border-[#00d2ff]"
            />
          </div>
          <div>
            <label className="block text-xs text-[#667] mb-1">Telegram Chat ID</label>
            <input 
              type="text" 
              value={config.telegram_chat || ''} 
              onChange={(e) => setConfig({...config, telegram_chat: e.target.value})}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm text-[#c0d0e0] outline-none focus:border-[#00d2ff]"
            />
          </div>
          <button 
            onClick={handleSave}
            disabled={loading}
            className="w-full bg-[#00d2ff] text-[#0a0e1a] font-bold py-2 rounded mt-4 hover:opacity-80 disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save Alert Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}
