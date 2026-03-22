"use client";

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import DiffViewer from '../../components/governance/DiffViewer';

const mockRequests = [
  {
    id: "req-1",
    entity_type: "BIOMETRIC",
    entity_name: "Ahmed Ali",
    status: "PENDING",
    maker: "Branch Manager (Giza)",
    old_img: "/mock/ahmed_old.jpg",
    new_img: "/mock/ahmed_new.jpg",
  },
];

export default function ApprovalsInbox() {
  const [filter, setFilter] = useState('PENDING');
  const [isProcessing, setIsProcessing] = useState(false);
  const t = useTranslations('Approvals');

  const filteredRequests = mockRequests.filter((req) => req.status === filter);

  async function handleApproveChange(changeId: string) {
    setIsProcessing(true);
    try {
      console.log(`Approving ${changeId}`);
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  }

  async function handleRejectChange(changeId: string) {
    setIsProcessing(true);
    try {
      console.log(`Rejecting ${changeId}`);
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900">{t('title')}</h1>
        <div className="space-x-2">
          {['PENDING', 'APPROVED', 'REJECTED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                filter === status ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-8">
        {filteredRequests.map((req) => (
          <div key={req.id} className="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-white">
              <div>
                <span className="text-xs font-bold px-2 py-1 bg-amber-100 text-amber-800 rounded uppercase">
                  {req.entity_type} {t('update')}
                </span>
                <p className="text-sm text-slate-500 mt-2">
                  {t('requestedBy')}: {req.maker}
                </p>
              </div>
              <div className="space-x-3">
                <button
                  className="px-4 py-2 bg-red-50 text-red-600 hover:bg-red-100 border border-red-200 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  onClick={() => handleRejectChange(req.id)}
                  disabled={isProcessing}
                >
                  {t('reject')}
                </button>
                <button
                  className="px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  onClick={() => handleApproveChange(req.id)}
                  disabled={isProcessing}
                >
                  {t('approveChange')}
                </button>
              </div>
            </div>

            <div className="p-6">
              {req.entity_type === 'BIOMETRIC' && (
                <DiffViewer
                  oldImageSrc={req.old_img}
                  newImageSrc={req.new_img}
                  entityName={req.entity_name}
                />
              )}
            </div>
          </div>
        ))}

        {filteredRequests.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            {t('noRequests', { status: filter.toLowerCase() })}
          </div>
        )}
      </div>
    </div>
  );
}
