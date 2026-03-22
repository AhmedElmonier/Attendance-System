import { test, expect } from '@playwright/test';

test.describe('Bilingual Dashboard localized routing and layout', () => {
  test('should default to English and LTR', async ({ page }) => {
    await page.goto('/');
    
    // Expect the HTML lang to be English
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  });

  test('should switch to Arabic and mirror layout to RTL', async ({ page }) => {
    await page.goto('/');
    
    // Select Arabic from the dropdown
    await page.locator('select').selectOption('ar');
    
    // Expect URL context to update and layout to mirror
    await expect(page).toHaveURL(/\/ar/);
    await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  });
});
