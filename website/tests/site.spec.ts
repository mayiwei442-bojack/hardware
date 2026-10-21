import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
test('five chapters, responsive navigation and no 3D requests',async({page},testInfo)=>{
 const errors:string[]=[];const modelRequests:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/\.(glb|gltf)(\?|$)/i.test(r.url()))modelRequests.push(r.url())});
 await page.goto('/');await page.waitForLoadState('networkidle');await expect(page.locator('main>section')).toHaveCount(5);await expect(page.locator('h1')).toHaveText('Key board');
 expect(await page.locator('body').innerText()).not.toMatch(/openmicro|开源/i);await expect(page.locator('.model-slot canvas')).toHaveCount(0);await expect(page.locator('#film')).toHaveCount(0);
 if(testInfo.project.name==='mobile')await page.getByRole('button',{name:'展开导航'}).click();
 await page.getByRole('navigation',{name:'主导航'}).getByRole('link',{name:/02\s*硬件/}).click();await expect(page).toHaveURL(/#hardware$/);await page.waitForTimeout(800);
 await page.getByRole('button',{name:/06\s*PCB/}).click();await expect(page.locator('.part-detail')).toContainText('STM32F072CBT6');
 const range=page.getByLabel('拆解阶段预览');await range.fill('80');await expect(page.locator('.assembly-control')).toContainText('PCB 显露');await page.getByRole('button',{name:'重置装配'}).click();await expect(range).toHaveValue('0');
 for(const id of ['overview','hardware','try','build','resources']){await page.locator(`#${id}`).scrollIntoViewIfNeeded();await page.waitForTimeout(100);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy()}
 await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));await page.waitForTimeout(1200);await page.screenshot({path:`artifacts/${testInfo.project.name}-overview.png`});
 expect(modelRequests).toEqual([]);expect(errors).toEqual([]);
});
test('virtual computer responds to all four input event types',async({page},testInfo)=>{
 await page.goto('/#try');await page.getByRole('button',{name:'K02 新建',exact:true}).click();await expect(page.getByLabel('代码编辑器')).toHaveValue(/New session/);await page.getByLabel('代码编辑器').fill('const edited = true;');
 await page.getByRole('button',{name:'旋钮顺时针'}).click();await expect(page.locator('.work-status')).toContainText('15px');await page.getByRole('button',{name:'摇杆右',exact:true}).click();await expect(page.locator('.editor-toolbar')).toContainText('input.ts');
 await page.getByRole('button',{name:'K07 命令',exact:true}).click();await expect(page.getByRole('dialog')).toBeVisible();await page.getByRole('button',{name:'整理代码空白'}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByRole('button',{name:'K10 终端',exact:true}).click();await expect(page.locator('.terminal')).toBeVisible();await page.getByRole('button',{name:'K12 侧栏',exact:true}).click();await page.getByLabel('侧边会话笔记').fill('Side session works.');
 await page.getByRole('tab',{name:/02\s*音频/}).click();await page.getByLabel('主音量').fill('45');await page.getByRole('button',{name:'旋钮顺时针'}).click();await expect(page.getByLabel('主音量')).toHaveValue('50');await page.getByRole('button',{name:'轻触触摸板'}).click();await expect(page.getByRole('button',{name:'暂停电平'})).toBeVisible();await page.getByRole('button',{name:'静音',exact:true}).click();await expect(page.locator('#try').getByRole('button',{name:'取消静音'})).toBeVisible();await page.getByLabel('延迟',{exact:true}).fill('70');await expect(page.getByLabel('延迟',{exact:true})).toHaveValue('70');
 await page.getByRole('tab',{name:/03\s*快捷键/}).click();await page.getByRole('button',{name:'摇杆右',exact:true}).click();await expect(page.locator('.shortcut-main h3')).toHaveText('音频参数');await page.getByRole('button',{name:'批准请求',exact:true}).click();await expect(page.locator('.action-history')).toContainText('已批准');await page.locator('#try').scrollIntoViewIfNeeded();await page.screenshot({path:`artifacts/${testInfo.project.name}-workstation.png`});
 await page.getByRole('button',{name:'复位试用'}).click();await expect(page.getByLabel('代码编辑器')).toHaveValue(/instrument/);
});
test('seven-step build completes, rejects invalid files and can be reconfigured',async({page},testInfo)=>{
 await page.goto('/#build');const lab=page.locator('#build');const next=lab.getByRole('button',{name:'下一步'});
 await expect(next).toBeDisabled();await lab.getByRole('button',{name:'代码 ↓'}).click();await lab.getByRole('button',{name:'下载 ZIP ↓'}).click();await expect(next).toBeEnabled();await next.click();
 await lab.getByLabel('选择Gerber / ZIP').setInputFiles({name:'bad.zip',mimeType:'application/zip',buffer:Buffer.from('not a zip')});await expect(lab.getByRole('alert')).toContainText('不是有效');await expect(lab.getByRole('button',{name:'确认打板配置'})).toBeDisabled();await lab.getByRole('button',{name:'使用预设'}).click();await lab.getByRole('button',{name:'确认打板配置'}).click();await expect(next).toBeEnabled();await next.click();
 await lab.getByRole('button',{name:'使用预设'}).nth(0).click();await lab.getByRole('button',{name:'使用预设'}).nth(1).click();await lab.getByRole('button',{name:'确认贴片订单'}).click();await expect(next).toBeEnabled();await next.click();
 await expect(lab.locator('.assembly-checklist input')).toHaveCount(3);for(const input of await lab.locator('.assembly-checklist input').all())await input.check();await lab.locator('.step-interaction').getByRole('button',{name:'确认手工装配'}).click();await next.click();
 await lab.getByRole('checkbox',{name:/旋钮/}).check();await lab.getByRole('button',{name:'启动打印演示'}).click();await expect(next).toBeEnabled();await next.click();
 await lab.getByRole('button',{name:'使用预设'}).click();await expect(lab.getByRole('button',{name:'写入'})).toBeDisabled();for(const label of ['连接','写入','校验']){const b=lab.getByRole('button',{name:new RegExp(label)});await expect(b).toBeEnabled();await b.click();await expect(lab.locator('.job-status')).toHaveCount(0)}await expect(next).toBeEnabled();await next.click();
 await expect(lab.getByRole('button',{name:'完成全部测试'})).toBeDisabled();for(let i=1;i<=13;i++)await lab.getByRole('button',{name:`测试按键 ${i}`,exact:true}).click();for(const v of ['−','+'])await lab.getByRole('button',{name:`测试旋钮 ${v}`,exact:true}).click();for(const v of ['←','↑','↓','→'])await lab.getByRole('button',{name:`测试摇杆 ${v}`,exact:true}).click();await lab.getByRole('button',{name:'测试触摸板'}).click();for(const c of ['红','绿','蓝'])await lab.locator('.rgb-test').getByRole('button',{name:c,exact:true}).click();await lab.getByRole('button',{name:'完成全部测试'}).click();await expect(lab.getByRole('progressbar')).toHaveAttribute('aria-valuenow','7');await expect(lab.locator('.build-complete')).toBeVisible();
 await lab.locator('.build-lab').scrollIntoViewIfNeeded();await page.screenshot({path:`artifacts/${testInfo.project.name}-build-complete.png`});
 await lab.getByRole('navigation',{name:'制作步骤'}).getByRole('button',{name:/配置电路板订单/}).click();await lab.getByRole('button',{name:'清除'}).click();await expect(lab.getByRole('progressbar')).toHaveAttribute('aria-valuenow','1');await expect(lab.locator('.build-complete')).toHaveCount(0);
});
test('reduced motion, keyboard navigation and accessibility',async({page})=>{
 const errors:string[]=[];page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text())});await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await page.waitForLoadState('networkidle');const animation=await page.locator('.overview-product-float').evaluate(el=>getComputedStyle(el).animationName);expect(animation).toBe('none');
 const report=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();expect(report.violations).toEqual([]);
 await page.getByRole('button',{name:'K07 命令',exact:true}).click();await expect(page.getByLabel('搜索命令')).toBeFocused();await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);expect(errors).toEqual([]);
});

test('all navigation anchors and narrow layouts',async({page})=>{
 await page.goto('/');
 for(const width of [320,768,1024]){await page.setViewportSize({width,height:900});await page.waitForTimeout(300);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy()}
 await page.setViewportSize({width:1440,height:1000});
 for(const id of ['overview','hardware','try','build','resources']){await page.locator(`nav[aria-label="主导航"] a[href="#${id}"]`).click();await expect(page).toHaveURL(new RegExp('#'+id+'$'));}
});
