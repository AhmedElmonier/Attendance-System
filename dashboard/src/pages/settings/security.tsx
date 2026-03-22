"use client";

import { useState } from 'react';

export default function SecuritySettings() {
  const [ipEnabled, setIpEnabled] = useState(false);
  const [ipList, setIpList] = useState("192.168.1.0/24\n10.0.0.0/8");

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold text-slate-900 mb-8">Security Configuration</h1>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-800">Administrative IP Allow-listing</h2>
            <p className="text-sm text-slate-500 mt-1">
              Restrict dashboard access for Managers and Admins to specific networks.
            </p>
          </div>
          <div className="flex items-center">
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                className="sr-only peer" 
                checked={ipEnabled} 
                onChange={() => setIpEnabled(!ipEnabled)} 
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
            <span className="ms-3 text-sm font-medium text-slate-900">{ipEnabled ? 'Enabled' : 'Disabled'}</span>
          </div>
        </div>

        <div className={`transition-opacity ${ipEnabled ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Allowed CIDR Blocks (One per line)
          </label>
          <textarea
            rows={5}
            className="w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono text-sm"
            value={ipList}
            onChange={(e) => setIpList(e.target.value)}
            disabled={!ipEnabled}
          />
          <p className="text-xs text-slate-500 mt-2">Example: 192.168.1.0/24 (Allows 192.168.1.0 to 192.168.1.255)</p>

          <div className="mt-6 flex justify-end">
            <button className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50" disabled={!ipEnabled}>
              Save Allow-list
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
