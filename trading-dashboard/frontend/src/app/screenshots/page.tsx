'use client';

import React, { useState, useEffect, useRef } from 'react';
import { fetchJSON } from '@/lib/api';

interface Screenshot { name: string; size: number; mtime: string; }

export default function ScreenshotsPage() {
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('');
  const [uploadKey, setUploadKey] = useState('');
  const [keyInput, setKeyInput] = useState('');
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { loadScreenshots(); }, []);

  const loadScreenshots = async () => {
    try { const d = await fetchJSON<Screenshot[]>('/api/uploads'); setScreenshots(d); }
    catch (e) { console.error(e); }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    if (!uploadKey) { setPendingFiles(files); setShowKeyModal(true); return; }
    doUpload(files, uploadKey);
    e.target.value = '';
  };

  const handleKeyConfirm = () => {
    if (!keyInput) return;
    setUploadKey(keyInput);
    setShowKeyModal(false);
    if (pendingFiles.length) { doUpload(pendingFiles, keyInput); setPendingFiles([]); }
  };

  const doUpload = async (files: File[], key: string) => {
    setUploading(true);
    let ok = 0;
    for (const file of files) {
      try {
        setStatus(`Uploading ${file.name}...`);
        const res = await fetch('/api/upload', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Key': key },
          body: JSON.stringify({ filename: file.name, contentType: file.type }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to get upload URL');
        const putRes = await fetch(data.uploadUrl, {
          method: 'PUT',
          headers: { 'Content-Type': file.type },
          body: file,
        });
        if (!putRes.ok) throw new Error('Upload to R2 failed');
        await fetch('/api/upload/confirm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Key': key },
          body: JSON.stringify({ filename: file.name }),
        });
        ok++;
      } catch (e: any) { setStatus(`Error: ${e.message}`); }
    }
    setStatus(`Uploaded ${ok}/${files.length} file(s)`);
    setUploading(false);
    loadScreenshots();
    setTimeout(() => setStatus(''), 4000);
  };

  const deleteScreenshot = async (name: string) => {
    if (!confirm(`Delete ${name}?`)) return;
    const key = uploadKey || prompt('Enter upload key:') || '';
    try {
      const res = await fetch(`/api/uploads/${name}`, { method: 'DELETE', headers: { 'X-Key': key } });
      if (!res.ok) throw new Error(await res.text());
      setScreenshots(p => p.filter(s => s.name !== name));
    } catch (e: any) { alert(`Delete failed: ${e.message}`); }
  };

  return (
    <div className="p-6 space-y-6">
      {showKeyModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-[#141a23] border border-[#2a3344] rounded-xl p-6 w-80 space-y-4">
            <div className="font-semibold text-[#c0d0e0]">Enter Upload Key</div>
            <input type="password" value={keyInput} onChange={e => setKeyInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleKeyConfirm()}
              className="w-full bg-[#1a2233] border border-[#2a3344] rounded px-3 py-2 text-sm outline-none focus:border-[#00d2ff] text-[#c0d0e0]"
              placeholder="Upload key" autoFocus />
            <div className="flex gap-2">
              <button onClick={handleKeyConfirm} className="flex-1 bg-[#00d2ff] text-[#0a0e1a] font-bold py-2 rounded">Confirm</button>
              <button onClick={() => { setShowKeyModal(false); setPendingFiles([]); }} className="flex-1 border border-[#2a3344] py-2 rounded text-[#8899aa]">Cancel</button>
            </div>
          </div>
        </div>
      )}
      <div className="flex items-center gap-4">
        <button onClick={() => fileRef.current?.click()} disabled={uploading}
          className="bg-[#00d2ff] text-[#0a0e1a] px-4 py-2 rounded font-bold disabled:opacity-50">
          {uploading ? 'Uploading...' : '📷 Upload Screenshots'}
        </button>
        <input ref={fileRef} type="file" className="hidden" multiple accept="image/*" onChange={handleFileChange} />
        {status && <span className="text-sm text-[#8899aa]">{status}</span>}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {screenshots.map(s => (
          <div key={s.name} className="card overflow-hidden">
            <img src={`/uploads/${s.name}`} alt={s.name} className="w-full h-48 object-cover cursor-pointer"
              onClick={() => window.open(`/uploads/${s.name}`, '_blank')} />
            <div className="p-2 flex justify-between items-center">
              <div className="text-xs truncate mr-2 text-[#8899aa]">{s.name}</div>
              <button onClick={() => deleteScreenshot(s.name)} className="text-red-500 hover:text-red-400">✖</button>
            </div>
          </div>
        ))}
        {screenshots.length === 0 && <div className="col-span-full py-20 text-center text-[#556]">No screenshots yet</div>}
      </div>
    </div>
  );
}
