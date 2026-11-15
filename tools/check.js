// 슬라이드 HTML을 열어 모든 슬라이드와 그림 단계를 넘기며 스크립트 오류가 있는지 확인합니다.
// 사용법: node tools/check.js bubble-sort-heap.html   (Playwright 필요)
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const file = path.resolve(process.argv[2] || 'bubble-sort-heap.html');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + file);
  await page.waitForTimeout(500);
  const n = await page.evaluate(() => document.querySelectorAll('.slide').length);
  for (let i = 0; i < n; i++) {
    for (let k = 0; k < 3; k++) await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(50);
  }
  console.log(`${path.basename(file)}: 슬라이드 ${n}장, ` + (errors.length ? `오류 ${errors.length}개\n` + errors.join('\n') : '오류 없음'));
  await browser.close();
  process.exit(errors.length ? 1 : 0);
})();
