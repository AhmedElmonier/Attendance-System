"use client";

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next-intl/client';
import { ChangeEvent, useTransition } from 'react';

export default function LanguageSwitcher() {
  const [isPending, startTransition] = useTransition();
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  function onSelectChange(event: ChangeEvent<HTMLSelectElement>) {
    const nextLocale = event.target.value;
    startTransition(() => {
      router.replace(pathname, { locale: nextLocale });
    });
  }

  return (
    <div className="flex items-center space-x-2 ms-4">
      <select
        defaultValue={locale}
        onChange={onSelectChange}
        disabled={isPending}
        className="bg-transparent text-sm font-medium border border-slate-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="en">English</option>
        <option value="ar">العربية (Arabic)</option>
      </select>
    </div>
  );
}
