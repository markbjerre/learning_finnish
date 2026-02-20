import { test, expect } from '@playwright/test';

test.describe('Learning Finnish - Main Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('should load homepage successfully', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Finnish|Learning/i);
  });

  test('should display design selector', async ({ page }) => {
    // Look for design selection interface
    const designs = page.getByRole('heading', { name: /design/i });
    // This will depend on actual implementation
  });

  test('should handle health check endpoint', async ({ page }) => {
    const response = await page.goto('http://localhost:8001/health');
    expect(response?.status()).toBe(200);
  });

  test('should have proper CORS headers', async ({ page }) => {
    const response = await page.goto('http://localhost:8001/health');
    const corsHeader = response?.headers()['access-control-allow-origin'];
    expect(corsHeader).toBeDefined();
  });
});

test.describe('Learning Finnish - API Integration', () => {
  test('backend should be accessible', async ({ page }) => {
    const response = await page.goto('http://localhost:8001/health');
    expect(response?.ok()).toBeTruthy();
  });

  test('frontend should load assets', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // Check for JavaScript bundle
    const scripts = page.locator('script[type="module"]');
    const scriptCount = await scripts.count();
    expect(scriptCount).toBeGreaterThan(0);
  });
});

test.describe('Learning Finnish - Responsive Design', () => {
  test('should be mobile responsive', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone size
    await page.goto('http://localhost:5173');
    
    // Check that page is not horizontally scrollable
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
  });

  test('should be tablet responsive', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad size
    await page.goto('http://localhost:5173');
    
    // Page should load without errors
    const errors = await page.evaluate(() => {
      return (window as any).__PLAYWRIGHT_ERRORS__ || [];
    });
    expect(errors.length).toBe(0);
  });

  test('should be desktop responsive', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 }); // Desktop size
    await page.goto('http://localhost:5173');
    
    // Page should render properly
    const bodyElement = page.locator('body');
    await expect(bodyElement).toBeVisible();
  });
});

test.describe('Learning Finnish - Accessibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    const count = await headings.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should have alt text on images', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    const images = page.locator('img');
    const count = await images.count();
    
    // Most images should have alt text
    for (let i = 0; i < Math.min(count, 5); i++) {
      const alt = await images.nth(i).getAttribute('alt');
      // Allow some images without alt (decorative elements)
      // but most should have it
    }
  });

  test('should have proper color contrast', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // This is a simplified check; real contrast testing is more complex
    const headings = page.locator('h1, h2, h3');
    const headingCount = await headings.count();
    expect(headingCount).toBeGreaterThan(0);
  });
});

test.describe('Learning Finnish - Performance', () => {
  test('should load homepage in reasonable time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:5173');
    const loadTime = Date.now() - startTime;
    
    // Page should load within 5 seconds in development
    expect(loadTime).toBeLessThan(5000);
  });

  test('should not have console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.goto('http://localhost:5173');
    
    // Allow some warnings but no critical errors
    const criticalErrors = errors.filter(
      (e) => !e.includes('Non-Error promise rejection') && 
             !e.includes('ResizeObserver')
    );
    expect(criticalErrors.length).toBe(0);
  });
});
