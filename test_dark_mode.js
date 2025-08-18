const { test, expect } = require('@playwright/test');

test.describe('SOPHIA Intel Dark Mode Toggle', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('https://sophia-intel.fly.dev');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('Dark mode toggle button exists and is clickable', async ({ page }) => {
    // Check if the toggle button exists
    const toggleButton = page.locator('button:has-text("Toggle")');
    await expect(toggleButton).toBeVisible();
    
    // Check if button contains either "Dark" or "Light" mode text
    const buttonText = await toggleButton.textContent();
    expect(buttonText).toMatch(/(Dark|Light) Mode/);
  });

  test('Dark mode toggle changes theme and persists', async ({ page }) => {
    // Get initial theme state
    const initialBodyClass = await page.evaluate(() => document.body.className);
    const initialIsDark = initialBodyClass.includes('dark-mode');
    
    // Click the toggle button
    await page.click('button:has-text("Toggle")');
    
    // Wait for theme change
    await page.waitForTimeout(500);
    
    // Check if theme changed
    const newBodyClass = await page.evaluate(() => document.body.className);
    const newIsDark = newBodyClass.includes('dark-mode');
    
    expect(newIsDark).toBe(!initialIsDark);
    
    // Check localStorage
    const storedTheme = await page.evaluate(() => localStorage.getItem('sophia_theme'));
    expect(storedTheme).toBe(newIsDark ? 'dark' : 'light');
  });

  test('Dark mode persists after page reload', async ({ page }) => {
    // Set dark mode
    await page.evaluate(() => {
      localStorage.setItem('sophia_theme', 'dark');
    });
    
    // Reload the page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check if dark mode is applied
    const bodyClass = await page.evaluate(() => document.body.className);
    expect(bodyClass).toContain('dark-mode');
    
    // Check if toggle button shows correct state
    const toggleButton = page.locator('button:has-text("Toggle")');
    const buttonText = await toggleButton.textContent();
    expect(buttonText).toContain('Light Mode');
    expect(buttonText).toContain('🌞');
  });

  test('Light mode persists after page reload', async ({ page }) => {
    // Set light mode
    await page.evaluate(() => {
      localStorage.setItem('sophia_theme', 'light');
    });
    
    // Reload the page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check if light mode is applied
    const bodyClass = await page.evaluate(() => document.body.className);
    expect(bodyClass).not.toContain('dark-mode');
    
    // Check if toggle button shows correct state
    const toggleButton = page.locator('button:has-text("Toggle")');
    const buttonText = await toggleButton.textContent();
    expect(buttonText).toContain('Dark Mode');
    expect(buttonText).toContain('🌙');
  });

  test('Dark mode styles are applied correctly', async ({ page }) => {
    // Enable dark mode
    await page.click('button:has-text("Toggle Dark Mode")');
    await page.waitForTimeout(500);
    
    // Check if dark mode class is applied to body
    const bodyClass = await page.evaluate(() => document.body.className);
    expect(bodyClass).toContain('dark-mode');
    
    // Check if main container has dark background
    const containerBg = await page.locator('.min-h-screen').evaluate(el => 
      window.getComputedStyle(el).backgroundColor
    );
    
    // Should have a dark background (not the light gradient)
    expect(containerBg).not.toBe('rgb(255, 255, 255)');
  });

  test('Toggle button icon changes correctly', async ({ page }) => {
    // Get initial button text
    const toggleButton = page.locator('button:has-text("Toggle")');
    const initialText = await toggleButton.textContent();
    
    // Click toggle
    await toggleButton.click();
    await page.waitForTimeout(500);
    
    // Get new button text
    const newText = await toggleButton.textContent();
    
    // Text should have changed
    expect(newText).not.toBe(initialText);
    
    // Should contain appropriate icon and text
    if (initialText.includes('Dark Mode')) {
      expect(newText).toContain('Light Mode');
      expect(newText).toContain('🌞');
    } else {
      expect(newText).toContain('Dark Mode');
      expect(newText).toContain('🌙');
    }
  });

  test('Dashboard components work in both light and dark modes', async ({ page }) => {
    // Test in light mode
    await page.click('button:has-text("System Dashboard")');
    await page.waitForTimeout(1000);
    
    // Check if dashboard loads
    const dashboardContent = page.locator('.status-card');
    await expect(dashboardContent.first()).toBeVisible();
    
    // Switch to dark mode
    await page.click('button:has-text("Toggle Dark Mode")');
    await page.waitForTimeout(500);
    
    // Dashboard should still be visible and functional
    await expect(dashboardContent.first()).toBeVisible();
    
    // Switch back to chat tab
    await page.click('button:has-text("Chat Interface")');
    await page.waitForTimeout(500);
    
    // Chat interface should be visible
    const chatTextarea = page.locator('textarea[placeholder*="Ask SOPHIA"]');
    await expect(chatTextarea).toBeVisible();
  });
});

