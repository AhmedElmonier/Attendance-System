import { test, expect } from '@playwright/test';

test.describe('Bilingual Dashboard localized routing and layout', () => {
  test('should default to English and LTR', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  });

  test('should switch to Arabic and mirror layout to RTL', async ({ page }) => {
    await page.goto('/');

    await page.locator('select[data-testid="language-switcher"]').selectOption('ar');
    await page.waitForURL(/\/ar/);
    await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  });
});
