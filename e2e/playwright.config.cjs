const { defineConfig, devices } = require('@playwright/test');
const path = require('path');
const python = process.env.SAMSTAG_PYTHON || 'python3';
const port = process.env.SAMSTAG_E2E_PORT || '8768';
const output = process.env.SAMSTAG_E2E_OUTPUT || path.resolve(__dirname,'../.artifacts/playwright');
module.exports = defineConfig({
  testDir: __dirname,
  testMatch: '**/*.spec.cjs',
  timeout: 25000,
  expect: { timeout: 7000 },
  workers: 2,
  retries: 0,
  outputDir: path.join(output,'artifacts'),
  reporter: [['list'], ['html', {outputFolder:path.join(output,'report'),open:'never'}], ['json',{outputFile:path.join(output,'results.json')}]],
  use: { baseURL:`http://127.0.0.1:${port}`, trace:'retain-on-failure', screenshot:'only-on-failure', locale:'fr-CH', timezoneId:'Europe/Zurich' },
  webServer: {
    command: `"${python}" "${path.resolve(__dirname,'server.py')}"`,
    url:`http://127.0.0.1:${port}`,reuseExistingServer:false,timeout:60000,
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
