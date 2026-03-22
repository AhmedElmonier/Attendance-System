"use client";

import { useState } from 'react';
import { useTranslations } from 'next-intl';

function isValidCIDR(cidr: string): boolean {
  try {
    const parts = cidr.trim().split('/');
    if (parts.length !== 2) return false;
    const ip = parts[0];
    const prefixStr = parts[1];
    const prefix = parseInt(prefixStr, 10);
    if (Number.isNaN(prefix)) return false;
    const ipParts = ip.split('.');
    if (ipParts.length !== 4) return false;
    for (const part of ipParts) {
      if (part === '') return false;
      const num = parseInt(part, 10);
      if (Number.isNaN(num) || num < 0 || num > 255) return false;
    }
    if (prefix < 0 || prefix > 32) return false;
    return true;
  } catch {
    return false;
  }
}

function validateIpList(ipList: string): string[] {
  return ipList
    .split('\n')
    .filter((line) => line.trim() && !isValidCIDR(line.trim()));
}

export default function SecuritySettings() {
  const [ipEnabled, setIpEnabled] = useState(false);
  const [ipList, setIpList] = useState("192.168.1.0/24\n10.0.0.0/8");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const t = useTranslations('Security');

  function handleIpListChange(value: string) {
    setIpList(value);
    const invalid = validateIpList(value);
    setValidationError(invalid.length > 0 ? t('invalidCidr', { entries: invalid.join(', ') }) : null);
    setSaveError(null);
  }

  async function handleSave() {
    const invalid = validateIpList(ipList);
    if (invalid.length > 0) {
      setValidationError(t('invalidCidr', { entries: invalid.join(', ') }));
      return;
    }
    setValidationError(null);
    setIsSaving(true);
    setSaveError(null);
    try {
      const res = await fetch('/api/v1/settings/security/ip-allowlist', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body: JSON.stringify({ enabled: ipEnabled, allowed_cidrs: ipList.split('\n').map((l) => l.trim()).filter(Boolean) }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Save failed: ${res.status}`);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setSaveError(msg);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold text-slate-900 mb-8">{t('title')}</h1>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-6 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-800">{t('ipAllowlistTitle')}</h2>
            <p className="text-sm text-slate-500 mt-1">{t('ipAllowlistDescription')}</p>
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
            <span className="ms-3 text-sm font-medium text-slate-900">
              {ipEnabled ? t('enabled') : t('disabled')}
            </span>
          </div>
        </div>

        <div className={`transition-opacity ${ipEnabled ? 'opacity-100' : 'opacity-50 pointer-events-none'}`}>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            {t('cidrLabel')}
          </label>
          <textarea
            rows={5}
            className="w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono text-sm"
            value={ipList}
            onChange={(e) => handleIpListChange(e.target.value)}
            disabled={!ipEnabled}
          />
          {validationError && (
            <p className="text-xs text-red-600 mt-2">{validationError}</p>
          )}
          {saveError && (
            <p className="text-xs text-red-600 mt-2">{saveError}</p>
          )}
          <p className="text-xs text-slate-500 mt-2">{t('cidrHint')}</p>

          <div className="mt-6 flex justify-end">
            <button
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50"
              disabled={!ipEnabled || validationError !== null || isSaving}
              onClick={handleSave}
            >
              {isSaving ? t('saving') : t('save')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
