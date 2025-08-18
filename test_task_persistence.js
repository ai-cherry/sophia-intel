const { test, expect } = require('@playwright/test');

test.describe('Task Persistence Tests', () => {
    test('Tasks persist after page reload', async ({ page }) => {
        // Navigate to the application
        await page.goto('https://sophia-intel.fly.dev');
        
        // Wait for the page to load and switch to dashboard tab
        await page.waitForLoadState('networkidle');
        await page.click('button:has-text("System Dashboard")');
        
        // Add a test task
        const taskInput = page.locator('#task-input');
        const addButton = page.locator('#add-task');
        
        await taskInput.fill('Test task for persistence');
        await addButton.click();
        
        // Verify task was added
        await expect(page.locator('#task-list li')).toContainText('Test task for persistence');
        
        // Reload the page
        await page.reload();
        await page.waitForLoadState('networkidle');
        await page.click('button:has-text("System Dashboard")');
        
        // Verify task persisted after reload
        await expect(page.locator('#task-list li')).toContainText('Test task for persistence');
    });

    test('Task completion status persists', async ({ page }) => {
        // Navigate to the application
        await page.goto('https://sophia-intel.fly.dev');
        await page.waitForLoadState('networkidle');
        await page.click('button:has-text("System Dashboard")');
        
        // Add a test task
        const taskInput = page.locator('#task-input');
        const addButton = page.locator('#add-task');
        
        await taskInput.fill('Task to complete');
        await addButton.click();
        
        // Mark task as completed
        const checkbox = page.locator('.task-checkbox').first();
        await checkbox.check();
        
        // Verify task is marked as completed
        await expect(page.locator('.task-text').first()).toHaveClass(/line-through/);
        
        // Reload the page
        await page.reload();
        await page.waitForLoadState('networkidle');
        await page.click('button:has-text("System Dashboard")');
        
        // Verify completion status persisted
        await expect(page.locator('.task-checkbox').first()).toBeChecked();
        await expect(page.locator('.task-text').first()).toHaveClass(/line-through/);
    });

    test('Task deletion works correctly', async ({ page }) => {
        // Navigate to the application
        await page.goto('https://sophia-intel.fly.dev');
        await page.waitForLoadState('networkidle');
        await page.click('button:has-text("System Dashboard")');
        
        // Add a test task
        const taskInput = page.locator('#task-input');
        const addButton = page.locator('#add-task');
        
        await taskInput.fill('Task to delete');
        await addButton.click();
        
        // Verify task was added
        await expect(page.locator('#task-list li')).toContainText('Task to delete');
        
        // Delete the task
        const deleteButton = page.locator('.delete-task').first();
        await deleteButton.click();
        
        // Verify task was deleted
        await expect(page.locator('#task-list li')).not.toContainText('Task to delete');
        
        // Reload the page to verify deletion persisted
        await page.reload();
        await page.waitForLoadState('networkidle');
        await page.click('button:has-text("System Dashboard")');
        
        // Verify task is still deleted after reload
        await expect(page.locator('#task-list li')).not.toContainText('Task to delete');
    });
});

