"use client";

import Image from 'next/image';

interface DiffViewerProps {
  oldImageSrc: string | null;
  newImageSrc: string;
  entityName: string;
}

export default function DiffViewer({ oldImageSrc, newImageSrc, entityName }: DiffViewerProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">
        Biometric Update: {entityName}
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Old Reference */}
        <div className="flex flex-col items-center">
          <span className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">Current Record</span>
          <div className="relative w-48 h-48 rounded-lg overflow-hidden border-2 border-slate-300 bg-slate-100 flex items-center justify-center">
            {oldImageSrc ? (
              <Image src={oldImageSrc} alt="Old" fill className="object-cover grayscale opacity-70" />
            ) : (
              <span className="text-slate-400">No Image</span>
            )}
          </div>
        </div>

        {/* New Reference */}
        <div className="flex flex-col items-center">
          <span className="text-sm font-medium text-blue-600 mb-2 uppercase tracking-wider">New Submission</span>
          <div className="relative w-48 h-48 rounded-lg overflow-hidden border-2 border-blue-400 shadow-md">
            <Image src={newImageSrc} alt="New" fill className="object-cover" />
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800 text-sm">
        <strong>⚠️ Security Notice:</strong> Verify that the new submission matches the identity of the current record before approving.
      </div>
    </div>
  );
}
