import { setRequestLocale } from 'next-intl/server';
import { notFound } from 'next/navigation';

const locales = ['en', 'ar'];

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  if (!locales.includes(params.locale)) {
    notFound();
  }

  await setRequestLocale(params.locale);
  const locale = params.locale;
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
