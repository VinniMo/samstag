const { defineConfig, devices } = require('@playwright/test');
const path = require('path');
module.exports = defineConfig({
  testDir: __dirname,
  testMatch: '**/*.spec.cjs',
  timeout: 25000,
  expect: { timeout: 7000 },
  workers: 2,
  retries: 0,
  outputDir: '../validation/playwright-2026-10-19/artifacts',
  reporter: [['list'], ['html', {outputFolder: '../validation/playwright-2026-10-19/report',open:'never'}], ['json',{outputFile:'../validation/playwright-2026-10-19/results.json'}]],
  use: { baseURL:'http://127.0.0.1:8768', trace:'retain-on-failure', screenshot:'only-on-failure', locale:'fr-CH', timezoneId:'Europe/Zurich' },
  webServer: {
    command: `${path.resolve(__dirname,'../.venv/bin/python')} ${path.resolve(__dirname,'server.py')}`,
    url:'http://127.0.0.1:8768',reuseExistingServer:false,timeout:60000,
    stdout:'pipe',stderr:'pipe',
  },
  projects:[
    {name:'chromium',use:{...devices['Desktop Chrome']}},
    {name:'firefox',use:{...devices['Desktop Firefox']}},
    {name:'webkit',use:{...devices['Desktop Safari']}},
    {name:'mobile-chromium',use:{...devices['Pixel 5']}},
    {name:'mobile-webkit',use:{...devices['iPhone 13']}},
  ],
});
