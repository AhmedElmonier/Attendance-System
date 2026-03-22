"use client";

import { useTranslations } from 'next-intl';
import Image from 'next/image';

interface DiffViewerProps {
  oldImageSrc: string | null;
  newImageSrc: string;
  entityName: string;
}

export default function DiffViewer({ oldImageSrc, newImageSrc, entityName }: DiffViewerProps) {
  const t = useTranslations('DiffViewer');

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">
        {t('biometricUpdate', { entityName })}
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="flex flex-col items-center">
          <span className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">
            {t('currentRecord')}
          </span>
          <div className="relative w-48 h-48 rounded-lg overflow-hidden border-2 border-slate-300 bg-slate-100 flex items-center justify-center">
            {oldImageSrc ? (
              <Image
                src={oldImageSrc}
                alt={`${entityName} current biometric image`}
                fill
                className="object-cover grayscale opacity-70"
              />
            ) : (
              <span className="text-slate-400">{t('noImage')}</span>
            )}
          </div>
        </div>

        <div className="flex flex-col items-center">
          <span className="text-sm font-medium text-blue-600 mb-2 uppercase tracking-wider">
            {t('newSubmission')}
          </span>
          <div className="relative w-48 h-48 rounded-lg overflow-hidden border-2 border-blue-400 shadow-md">
            <Image
              src={newImageSrc}
              alt={`${entityName} proposed biometric image`}
              fill
              className="object-cover"
            />
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800 text-sm">
        <strong>{t('securityNoticeLabel')}:</strong> {t('securityNotice')}
      </div>
    </div>
  );
}
