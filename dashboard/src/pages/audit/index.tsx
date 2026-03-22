"use client";

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';

interface AuditLogEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  entity: string;
  ip: string;
}

export default function AuditLogs() {
  const [searchTerm, setSearchTerm] = useState('');
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const t = useTranslations('Audit');

  useEffect(() => {
    async function fetchLogs() {
      try {
        setIsLoading(true);
        const res = await fetch('/api/v1/governance/audit-logs');
        if (!res.ok) throw new Error(`Failed to load audit logs: ${res.status}`);
        const data = await res.json();
        setLogs(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    }
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter(
    (log) =>
      log.actor.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  function handleExportCsv() {
    const DANGEROUS_PREFIXES = ['=', '+', '-', '@'];
    function sanitizeCell(value: string): string {
      const prefix = DANGEROUS_PREFIXES.some((p) => value.startsWith(p))
        ? "'"
        : '';
      const escaped = value.replace(/"/g, '""');
      return `${prefix}"${escaped}"`;
    }

    const headerRow = ['Timestamp', 'Actor', 'Action', 'Entity', 'IP Address']
      .map(sanitizeCell)
      .join(',');
    const dataRows = filteredLogs.map((log) =>
      [log.timestamp, log.actor, log.action, log.entity, log.ip]
        .map(sanitizeCell)
        .join(','),
    );
    const csv = [headerRow, ...dataRows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'audit_logs.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">{t('title')}</h1>
        <p className="text-slate-500 mt-2">{t('description')}</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <input
            type="text"
            placeholder={t('searchPlaceholder')}
            className="w-full max-w-sm px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button
            onClick={handleExportCsv}
            className="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm font-medium hover:bg-slate-700"
          >
            {t('exportCsv')}
          </button>
        </div>

        {isLoading && (
          <div className="p-8 text-center text-slate-500">{t('loading')}</div>
        )}

        {error && (
          <div className="p-8 text-center text-red-600">{t('error', { message: error })}</div>
        )}

        {!isLoading && !error && (
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="text-xs uppercase bg-slate-100 text-slate-700 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-6 py-4">{t('colTimestamp')}</th>
                <th scope="col" className="px-6 py-4">{t('colActor')}</th>
                <th scope="col" className="px-6 py-4">{t('colAction')}</th>
                <th scope="col" className="px-6 py-4">{t('colEntity')}</th>
                <th scope="col" className="px-6 py-4">{t('colIpAddress')}</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => (
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
        )}

        {!isLoading && !error && filteredLogs.length === 0 && (
          <div className="p-8 text-center text-slate-500">{t('noLogs')}</div>
        )}
      </div>
    </div>
  );
}
