import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import { statSync } from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const demoDir = path.join(__dirname, 'demo', 'screenshots');
const BASE = 'http://localhost:8501';

const pages = [
  { name: '00_home', label: null }, // Home page (default)
  { name: '01_chat', label: 'Chat' },
  { name: '02_upload', label: 'Upload' },
  { name: '03_comparison', label: 'Comparison' },
  { name: '04_compliance', label: 'Compliance' },
  { name: '05_knowledge_graph', label: 'Knowledge' },
  { name: '06_evaluation', label: 'Evaluation' },
];

async function waitForStreamlit(page) {
  // Wait for Streamlit to fully load (sidebar appears)
  await page.waitForSelector('[data-testid="stSidebar"]', { timeout: 30000 });
  await page.waitForTimeout(3000);
}

(async () => {
  const browser = await chromium.launch();

  for (const pg of pages) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

    if (!pg.label) {
      // Home page — navigate directly
      await page.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
      await waitForStreamlit(page);
    } else {
      // Navigate to home first, then click sidebar link
      await page.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
      await waitForStreamlit(page);

      // Click on the sidebar navigation link
      const navLink = page.locator('[data-testid="stSidebar"]')
        .locator('a', { hasText: new RegExp(pg.label, 'i') });

      if (await navLink.count() > 0) {
        await navLink.first().click();
        await page.waitForTimeout(4000);
      } else {
        console.log(`  WARN: Nav link "${pg.label}" not found, trying URL`);
        await page.goto(`${BASE}/${pg.label}`, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);
      }
    }

    const filePath = path.join(demoDir, `${pg.name}.png`);
    await page.screenshot({ path: filePath, fullPage: true });
    const size = statSync(filePath).size;
    const ok = size > 10240 ? 'OK' : 'SMALL';
    console.log(`Captured: ${pg.name}.png (${(size / 1024).toFixed(1)} KB) ${ok}`);
    await page.close();
  }

  await browser.close();
  console.log('\nAll screenshots saved to demo/screenshots/');
})();
