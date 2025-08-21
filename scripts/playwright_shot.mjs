import { chromium } from 'playwright';

async function takeScreenshot() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to dashboard...');
    await page.goto('https://sophia-dashboard.fly.dev', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    console.log('Taking screenshot...');
    await page.screenshot({ 
      path: 'shot.png', 
      fullPage: true 
    });
    
    console.log('Screenshot saved as shot.png');
    
    // Check for assets loading
    const jsAssets = await page.$$eval('script[src*="/assets/"]', scripts => 
      scripts.map(s => s.src)
    );
    const cssAssets = await page.$$eval('link[href*="/assets/"]', links => 
      links.map(l => l.href)
    );
    
    console.log('JS Assets:', jsAssets);
    console.log('CSS Assets:', cssAssets);
    
    // Check if assets are loading from correct paths
    const correctPaths = [...jsAssets, ...cssAssets].every(asset => 
      asset.includes('/assets/') && !asset.includes('/dashboard/assets/')
    );
    
    console.log('Assets loading from correct paths:', correctPaths);
    
  } catch (error) {
    console.error('Error:', error.message);
    // Still take a screenshot even if there's an error
    try {
      await page.screenshot({ path: 'shot.png', fullPage: true });
      console.log('Error screenshot saved');
    } catch (screenshotError) {
      console.error('Could not take screenshot:', screenshotError.message);
    }
  } finally {
    await browser.close();
  }
}

takeScreenshot();

