'use client';

import React, { useEffect, useState } from 'react';
import { fetchJSON } from '@/lib/api';

interface SystemData {
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
  network: {
    rx_bytes: number;
    tx_bytes: number;
    rx_kbps: number;
    tx_kbps: number;
  } | null;
  processes: number | null;
}

interface ServiceStatus {
  name: string;
  status: 'up' | 'down';
  code?: number;
  error?: string;
}

export default function SystemPage() {
  const [system, setSystem] = useState<SystemData | null>(null);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [sys, svc] = await Promise.all([
          fetchJSON<SystemData>('/api/system'),
          fetchJSON<ServiceStatus[]>('/api/services')
        ]);
        setSystem(sys);
        setServices(svc);
      } catch (e) {
        console.error('Failed to load system data', e);
      } finally {
        setLoading(false);
      }
    };
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-8 text-center">Loading system status...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#c0d0e0]">System Monitor</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU Card */}
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">CPU Usage</div>
          <div className="text-2xl font-bold text-[#c0d0e0]">
            {system?.cpu ? `${system.cpu}%` : '--'}
          </div>
          {system?.load && (
            <div className="text-xs text-[#667] mt-2">
              Load: {system.load['1m']}m / {system.load['5m']}m / {system.load['15m']}m
            </div>
          )}
        </div>

        {/* Memory Card */}
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">Memory Usage</div>
          <div className="text-2xl font-bold text-[#c0d0e0]">
            {system?.memory ? `${system.memory.used}/${system.memory.total}G` : '--'}
          </div>
          {system?.memory && (
            <div className="text-xs text-[#667] mt-2">
              {system.memory.percent}% used
            </div>
          )}
        </div>

        {/* Disk Card */}
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">Disk Usage (/)</div>
          <div className="text-2xl font-bold text-[#c0d0e0]">
            {system?.disk ? `${system.disk.used}/${system.disk.total}G` : '--'}
          </div>
          {system?.disk && (
            <div className="text-xs text-[#667] mt-2">
              {system.disk.percent}% used
            </div>
          )}
        </div>

        {/* Uptime Card */}
        <div className="card">
          <div className="text-xs text-[#8899aa] uppercase">System Uptime</div>
          <div className="text-2xl font-bold text-[#c0d0e0]">
            {system?.uptime ? `${system.uptime.days}d ${system.uptime.hours}h` : '--'}
          </div>
          {system?.uptime && (
            <div className="text-xs text-[#667] mt-2">
              {Math.floor(system.uptime.seconds / 3600)}h total
            </div>
          )}
        </div>
      </div>

      {/* Services Status Card */}
      <div className="card">
        <h2 className="text-sm font-medium text-[#8899aa] uppercase mb-4">Services Status</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((svc, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-[#1a2233] rounded-lg">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${svc.status === 'up' ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-[#c0d0e0]">{svc.name}</span>
              </div>
              {svc.error && <span className="text-xs text-red-400" title={svc.error}>{svc.code || 'ERR'}</span>}
              {svc.status === 'up' && <span className="text-xs text-green-400">OK</span>}
              {svc.status === 'down' && <span className="text-xs text-red-400">DOWN</span>}
            </div>
          ))}
        </div>
      </div>

      {/* Network Card */}
      {system?.network && (
        <div className="card">
          <h2 className="text-sm font-medium text-[#8899aa] uppercase mb-4">Network Throughput</h2>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-xs text-[#667]">RX</div>
              <div className="text-lg font-semibold">{system.network.rx_kbps.toFixed(1)} KB/s</div>
            </div>
            <div>
              <div className="text-xs text-[#667]">TX</div>
              <div className="text-lg font-semibold">{system.network.tx_kbps.toFixed(1)} KB/s</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
