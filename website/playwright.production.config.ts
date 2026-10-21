import {defineConfig} from '@playwright/test';
import base from './playwright.config';

export default defineConfig({
 ...base,
 use:{...base.use,baseURL:'http://localhost:3112',actionTimeout:30000},
 webServer:{command:'npx next start -p 3112',url:'http://localhost:3112',reuseExistingServer:false,timeout:60000},
});
