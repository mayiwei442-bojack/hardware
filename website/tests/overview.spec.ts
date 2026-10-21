import {test, expect, type Page} from '@playwright/test';

async function pixelSignature(page: Page) {
  return page.locator('.overview-pixels').evaluate((canvas: HTMLCanvasElement) => {
    const ctx = canvas.getContext('2d')!;
    const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    let hash = 0;
    for (let i = 0; i < pixels.length; i += 192) hash = (Math.imul(hash, 31) + pixels[i] + pixels[i + 3]) | 0;
    return hash;
  });
}

test('opening reveals once, pixels keep moving behind a full-screen minimal overview', async ({page}, info) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.locator('#hardware canvas')).toHaveCount(0);
  const hero = page.locator('#overview');
  await expect(hero).toHaveAttribute('data-phase', 'ambient', {timeout: 6000});
  await expect(page.locator('.overview-opening')).toBeHidden();
  await expect(hero.getByRole('heading')).toHaveText('Key board');
  await expect(hero.locator('a,button')).toHaveCount(0);
  expect(await hero.innerText()).toBe('Key board');
  expect(await hero.evaluate(el => Math.abs(el.clientHeight - window.innerHeight) <= 1)).toBeTruthy();
  expect(await hero.getByRole('img').evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0)).toBeTruthy();
  const before = await pixelSignature(page);
  await page.waitForTimeout(450);
  expect(await pixelSignature(page)).not.toBe(before);
  await page.screenshot({path: `artifacts/${info.project.name}-pixel-overview.png`});
  await page.locator('#try').evaluate(el => el.scrollIntoView({behavior: 'instant'}));
  await page.waitForTimeout(250);
  const paused = await pixelSignature(page);
  await page.waitForTimeout(350);
  expect(await pixelSignature(page)).toBe(paused);
  await page.evaluate(() => window.scrollTo({top: 0, behavior: 'instant'}));
  await expect(page.locator('.overview-opening')).toBeHidden();
  await expect(page.getByRole('banner')).toBeVisible();
  expect(errors).toEqual([]);
});

test('reduced motion skips the wash and freezes the pixel field', async ({page}) => {
  await page.emulateMedia({reducedMotion: 'reduce'});
  await page.goto('/');
  await expect(page.locator('#overview')).toHaveAttribute('data-phase', 'ambient');
  await expect(page.locator('.overview-opening')).toBeHidden();
  const before = await pixelSignature(page);
  await page.waitForTimeout(400);
  expect(await pixelSignature(page)).toBe(before);
  expect(await page.locator('.overview-product-float').evaluate(el => getComputedStyle(el).animationName)).toBe('none');
});
