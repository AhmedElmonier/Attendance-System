"use client";

import { useState } from 'react';

const mockLogs = [
  {
    id: "log-1",
    timestamp: "2026-03-22 14:32:10",
    actor: "Admin User",
    action: "UPDATE",
    entity: "EMPLOYEE",
    ip: "192.168.1.100"
  },
  {
    id: "log-2",
    timestamp: "2026-03-22 10:15:00",
    actor: "Branch Manager",
    action: "LOGIN",
    entity: "SYSTEM",
    ip: "10.0.0.5"
  }
];

export default function AuditLogs() {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredLogs = mockLogs.filter(log => 
    log.actor.toLowerCase().includes(searchTerm.toLowerCase()) || 
    log.action.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Audit Trail</h1>
        <p className="text-slate-500 mt-2">Immutable system history and governance logs.</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <input 
            type="text" 
            placeholder="Search by actor or action..." 
            className="w-full max-w-sm px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button className="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm font-medium hover:bg-slate-700">
            Export CSV
          </button>
        </div>
        
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="text-xs uppercase bg-slate-100 text-slate-700 border-b border-slate-200">
            <tr>
              <th className="px-6 py-4">Timestamp</th>
              <th className="px-6 py-4">Actor</th>
              <th className="px-6 py-4">Action</th>
              <th className="px-6 py-4">Entity</th>
              <th className="px-6 py-4">IP Address</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.map(log => (
              <tr key={log.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-6 py-4 font-mono text-xs">{log.timestamp}</td>
                <td className="px-6 py-4 font-medium text-slate-800">{log.actor}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-slate-200 text-slate-700 rounded text-xs font-bold">
                    {log.action}
                  </span>
                </td>
                <td className="px-6 py-4">{log.entity}</td>
                <td className="px-6 py-4 font-mono text-xs text-slate-500">{log.ip}</td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredLogs.length === 0 && (
          <div className="p-8 text-center text-slate-500">No logs match your search criteria.</div>
        )}
      </div>
    </div>
  );
}
