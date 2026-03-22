import { useLocale } from 'next-intl';
import { notFound } from 'next/navigation';

const locales = ['en', 'ar'];

export default function RootLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const locale = useLocale();

  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale)) notFound();

  // Determines the text direction (RTL for Arabic, LTR for English)
  const dir = locale === 'ar' ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={dir}>
      <head>
        <title>Attendance System | نظام الحضور</title>
      </head>
      <body className="bg-slate-50 text-slate-900 font-sans antialiased">
        <div className="min-h-screen flex flex-col items-center">
          <main className="w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-8 flex-grow">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
