import {defineConfig} from '@playwright/test';
import base from './playwright.config';
export default defineConfig({...base,testMatch:'hardware.spec.ts',use:{...base.use,baseURL:'http://localhost:3101',actionTimeout:30000},webServer:{command:'npx next start -p 3101',url:'http://localhost:3101',reuseExistingServer:true,timeout:60000}});
