import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
test('five chapters, responsive navigation and the real hardware model',async({page},testInfo)=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await expect(page.locator('main>section')).toHaveCount(5);await expect(page.locator('h1')).toHaveText('Key board');
 await expect(page.locator('#film')).toHaveCount(0);
 if(testInfo.project.name==='mobile')await page.getByRole('button',{name:'展开导航'}).click();
 await page.getByRole('navigation',{name:'主导航'}).getByRole('link',{name:/02\s*硬件/}).click();await expect(page).toHaveURL(/#hardware$/);
 await expect(page.locator('#hardware')).toHaveAttribute('data-loaded','true',{timeout:45000});
 await expect(page.locator('#hardware canvas')).toHaveCount(1);
 await expect(page.getByLabel('拆解阶段预览')).toHaveCount(0);
 for(const id of ['overview','hardware','try','build','resources']){await page.locator(`#${id}`).scrollIntoViewIfNeeded();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy()}
 expect(errors).toEqual([]);
});
test('virtual computer responds to all four input event types',async({page},testInfo)=>{
 await page.goto('/#try');await expect(page.locator('#hardware canvas')).toHaveCount(0);const display=page.locator('.computer-screen');
 await page.getByRole('button',{name:'K02 新建',exact:true}).click();await expect(page.getByLabel('代码编辑器')).toHaveValue(/New session/);await page.getByLabel('代码编辑器').fill('const edited = true;');
 await page.getByRole('button',{name:'旋钮顺时针'}).click();await expect(display).toHaveAttribute('data-screen','encoder');await expect(page.locator('.work-status')).toContainText('15px');
 await page.getByRole('button',{name:'摇杆右',exact:true}).click();await expect(display).toHaveAttribute('data-screen','joystick');await expect(page.locator('.navigation-files .selected')).toHaveText('input.ts');
 await page.getByRole('button',{name:'K07 命令',exact:true}).click();await expect(page.getByRole('region',{name:'命令面板',exact:true})).toBeVisible();await page.getByRole('button',{name:'整理代码空白'}).click();await expect(page.getByLabel('代码编辑器')).toBeVisible();
 await page.getByRole('button',{name:'K10 终端',exact:true}).click();await expect(page.locator('.screen-terminal')).toBeVisible();await page.getByRole('button',{name:'K12 侧栏',exact:true}).click();await page.getByLabel('侧边会话笔记').fill('Side session works.');
 await page.getByRole('tab',{name:/02\s*音频/}).click();await page.getByLabel('主音量').fill('45');await page.getByRole('button',{name:'旋钮顺时针'}).click();await expect(page.locator('.screen-big-value strong')).toHaveText('50');await page.getByRole('button',{name:'轻触触摸板'}).click();await expect(display).toHaveAttribute('data-screen','touch');await expect(display).toContainText('音频电平已启动');
 await page.getByRole('tab',{name:/02\s*音频/}).click();await expect(page.getByRole('button',{name:'暂停电平'})).toBeVisible();await page.getByRole('button',{name:'静音',exact:true}).click();await expect(page.getByRole('button',{name:'取消静音'})).toBeVisible();await page.getByLabel('延迟',{exact:true}).fill('70');await expect(page.getByLabel('延迟',{exact:true})).toHaveValue('70');
 await page.getByRole('tab',{name:/03\s*快捷键/}).click();await page.getByRole('button',{name:'音频混音台',exact:false}).click();await expect(page.locator('.shortcut-main h4')).toHaveText('音频参数');await page.getByRole('button',{name:'批准请求',exact:true}).click();await expect(display).toHaveAttribute('data-screen','K08');await expect(page.locator('.action-history')).toContainText('已批准');
 await page.locator('.try-desk').scrollIntoViewIfNeeded();await page.screenshot({path:`artifacts/${testInfo.project.name}-workstation.png`});await page.getByRole('button',{name:'复位试用'}).click();await expect(display).toHaveAttribute('data-screen','ready');
});

test('seven-step build completes, rejects invalid files and can be reconfigured',async({page},testInfo)=>{
 await page.goto('/#build');const lab=page.locator('#build');const next=lab.getByRole('button',{name:'下一步'});
 await expect(next).toBeDisabled();await lab.getByRole('button',{name:'代码 ↓'}).click();await lab.getByRole('button',{name:'下载 ZIP ↓'}).click();await expect(next).toBeEnabled();await next.click();
 await lab.getByLabel('选择Gerber / ZIP').setInputFiles({name:'bad.zip',mimeType:'application/zip',buffer:Buffer.from('not a zip')});await expect(lab.getByRole('alert')).toContainText('不是有效');await expect(lab.getByRole('button',{name:'提交模拟 PCB 订单'})).toBeDisabled();await lab.getByRole('button',{name:'使用预设'}).click();await lab.getByRole('button',{name:'检查 PCB 订单'}).click();await lab.getByRole('button',{name:'提交模拟 PCB 订单'}).click();await expect(next).toBeEnabled();await next.click();
 await lab.getByRole('button',{name:'使用预设'}).nth(0).click();await lab.getByRole('button',{name:'使用预设'}).nth(1).click();await lab.getByRole('button',{name:'解析并匹配元件'}).click();await lab.getByRole('button',{name:'确认物料匹配'}).click();await lab.getByRole('button',{name:'运行 DFM 检查'}).click();await lab.getByRole('button',{name:'提交模拟 SMT 订单'}).click();await expect(next).toBeEnabled();await next.click();
 await lab.getByRole('button',{name:'选择机械轴'}).click();await lab.getByRole('button',{name:'安装 SW03',exact:true}).click();await lab.getByRole('button',{name:'自动安装剩余机械轴'}).click();await lab.getByRole('button',{name:'选择编码器'}).click();await lab.getByRole('button',{name:'安装 SW1',exact:true}).click();await lab.getByRole('button',{name:'选择摇杆'}).click();await lab.getByRole('button',{name:'安装 J1',exact:true}).click();await lab.getByRole('button',{name:'翻到背面'}).click();await lab.getByRole('button',{name:'演示焊接其余焊点'}).click();await lab.getByRole('button',{name:'确认手工装配'}).click();await next.click();
 await lab.getByRole('checkbox',{name:/旋钮/}).check();await lab.getByRole('button',{name:'启动打印演示'}).click();await expect(next).toBeEnabled();await next.click();
 await expect(lab.getByRole('button',{name:'开始烧录'})).toBeDisabled();await lab.getByRole('button',{name:'点击连接'}).click();await lab.getByRole('button',{name:'使用预设'}).click();await lab.getByRole('button',{name:'开始烧录'}).click();await expect(lab.getByRole('button',{name:'校验固件'})).toBeEnabled({timeout:15000});await lab.getByRole('button',{name:'校验固件'}).click();await lab.getByRole('button',{name:'重新启动'}).click();await expect(next).toBeEnabled();await next.click();
 await expect(lab.getByRole('button',{name:'完成全部测试'})).toBeDisabled();for(let i=1;i<=13;i++)await lab.getByRole('button',{name:`测试按键 ${i}`,exact:true}).click();for(const v of ['−','+'])await lab.getByRole('button',{name:`测试旋钮 ${v}`,exact:true}).click();for(const v of ['←','↑','↓','→'])await lab.getByRole('button',{name:`测试摇杆 ${v}`,exact:true}).click();await lab.getByRole('button',{name:'测试触摸板'}).click();for(const c of ['红','绿','蓝'])await lab.locator('.rgb-test').getByRole('button',{name:c,exact:true}).click();await lab.getByRole('button',{name:'完成全部测试'}).click();await expect(lab.getByRole('progressbar')).toHaveAttribute('aria-valuenow','7');await expect(lab.locator('.build-complete')).toBeVisible();
 await lab.locator('.build-lab').scrollIntoViewIfNeeded();await page.screenshot({path:`artifacts/${testInfo.project.name}-build-complete.png`});
 await lab.getByRole('navigation',{name:'制作步骤'}).getByRole('button',{name:/配置电路板订单/}).click();await lab.getByRole('button',{name:'清除'}).click();await expect(lab.getByRole('progressbar')).toHaveAttribute('aria-valuenow','1');await expect(lab.locator('.build-complete')).toHaveCount(0);
});
test('reduced motion, keyboard navigation and accessibility',async({page})=>{
 const errors:string[]=[];page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text())});await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await page.waitForLoadState('networkidle');const animation=await page.locator('.overview-product-float').evaluate(el=>getComputedStyle(el).animationName);expect(animation).toBe('none');
 const report=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();expect(report.violations).toEqual([]);
 await page.getByRole('button',{name:'K07 命令',exact:true}).click();await expect(page.getByLabel('搜索命令')).toBeFocused();await page.keyboard.press('Escape');await expect(page.getByRole('region',{name:'命令面板',exact:true})).toHaveCount(0);expect(errors).toEqual([]);
});

test('all navigation anchors and narrow layouts',async({page})=>{
 await page.goto('/');
 for(const width of [320,768,1024]){await page.setViewportSize({width,height:900});await page.waitForTimeout(300);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy()}
 await page.setViewportSize({width:1440,height:1000});
 for(const id of ['overview','hardware','try','build','resources']){await page.locator(`nav[aria-label="主导航"] a[href="#${id}"]`).click();await expect(page).toHaveURL(new RegExp('#'+id+'$'));}
});
