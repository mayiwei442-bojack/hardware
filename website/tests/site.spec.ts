import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {readFile} from 'node:fs/promises';
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
test('Codex template keys show supported chords without invented tools',async({page},testInfo)=>{
 const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto('/#try');const trial=page.locator('#try');const display=trial.locator('.computer-screen');
 await expect(display).toContainText('本页示例 · 未连接设备或应用');
 const chords=['Ctrl + Alt + A','Ctrl + N','Ctrl + Alt + 1','Ctrl + Alt + 2','Ctrl + Alt + 3','Ctrl + Alt + 4','Ctrl + K','Enter','Esc','Ctrl + `','Ctrl + Shift + D','Ctrl + Alt + S','Ctrl + Shift + M'];
 for(let index=0;index<13;index++){
  const id='K'+String(index+1).padStart(2,'0');await trial.getByRole('button',{name:new RegExp('^'+id+' ')}).click();
  await expect(display).toHaveAttribute('data-screen',id);await expect(display.locator('.binding-card .key-chord')).toHaveAttribute('aria-label',chords[index]);
 }
 await expect(display).toContainText('在 Codex 中选择模型');
 await expect(trial.locator('input[type=range],textarea,.voice-wave,.level-meter,.screen-model')).toHaveCount(0);
 await expect(trial.getByText(/音色|电平|推理强度|音频混音台|标准|深入|已连接/)).toHaveCount(0);
 await trial.getByRole('button',{name:'macOS',exact:true}).click();
 await trial.getByRole('button',{name:'K02 新建',exact:true}).click();await expect(display.locator('.binding-card .key-chord')).toHaveAttribute('aria-label','Cmd + N');await expect(display).toContainText('开始新的会话');
 await trial.getByRole('button',{name:'K05 会话 3',exact:true}).click();await expect(display).toContainText('查看按键映射');
 await trial.getByRole('button',{name:'K08 确认',exact:true}).click();await expect(display.locator('.demo-request')).toContainText('示例请求已确认');
 await trial.getByRole('button',{name:'K09 拒绝',exact:true}).click();await expect(display.locator('.demo-request')).toContainText('示例请求已拒绝');
 await trial.getByRole('button',{name:'K11 语音',exact:true}).click();await expect(display).toContainText('不调用麦克风或生成转写结果');
 await trial.getByRole('button',{name:'K07 命令',exact:true}).click();await expect(page.getByLabel('搜索命令')).toBeFocused();await page.getByLabel('搜索命令').fill('模型');await display.getByRole('button',{name:/打开模型选择器/}).click();await expect(display).toHaveAttribute('data-screen','K13');
 await expect(trial.locator('.monitor-view')).toHaveCSS('opacity','1');await trial.locator('.try-desk').screenshot({path:'artifacts/trial-cleanup-'+testInfo.project.name+'-codex.png',animations:'disabled',style:'.site-header,.skip-link{visibility:hidden!important}'});
 expect(errors).toEqual([]);
});

test('media touch scenes preserve playback state and reset to defaults',async({page},testInfo)=>{
 await page.goto('/#try');const trial=page.locator('#try');const display=trial.locator('.computer-screen');
 await trial.getByRole('tab',{name:/02\s*媒体/}).click();const media=display.locator('.media-demo');
 await expect(media).toHaveAttribute('data-playing','true');await expect(media).toHaveAttribute('data-scene','music');
 await trial.getByRole('button',{name:'轻触触摸板',exact:true}).click();await expect(display).toHaveAttribute('data-screen','touch');await expect(media).toHaveAttribute('data-playing','false');await expect(media).toContainText('已暂停，可以先处理手边的事');
 await trial.getByRole('button',{name:'轻触触摸板',exact:true}).click();await expect(media).toHaveAttribute('data-playing','true');
 await trial.getByRole('button',{name:'跟着教程操作',exact:true}).click();await trial.getByRole('button',{name:'轻触触摸板',exact:true}).click();await expect(media).toHaveAttribute('data-scene','lesson');await expect(media).toHaveAttribute('data-playing','false');await expect(media).toContainText('已暂停，照着当前步骤操作');
 await expect(trial.locator('.monitor-view')).toHaveCSS('opacity','1');await page.screenshot({path:'artifacts/trial-cleanup-'+testInfo.project.name+'-touch.png',animations:'disabled'});
 await trial.getByRole('tab',{name:/03\s*快捷键/}).click();await trial.getByRole('tab',{name:/02\s*媒体/}).click();await expect(media).toHaveAttribute('data-playing','false');await expect(media).toHaveAttribute('data-scene','lesson');
 await trial.getByRole('button',{name:'复位试用',exact:true}).click();await expect(display).toHaveAttribute('data-screen','ready');await trial.getByRole('tab',{name:/02\s*媒体/}).click();await expect(media).toHaveAttribute('data-scene','music');await expect(media).toHaveAttribute('data-playing','true');await expect(page.getByLabel('演示音量')).toHaveText('70%');
});

test('default encoder and joystick mappings do not change with the selected view',async({page})=>{
 await page.goto('/#try');const trial=page.locator('#try');const display=trial.locator('.computer-screen');
 await trial.getByRole('button',{name:'旋钮顺时针',exact:true}).click();await expect(page.getByLabel('演示音量')).toHaveText('75%');
 await trial.getByRole('button',{name:'按下旋钮，切换静音',exact:true}).click();await expect(page.getByLabel('演示音量')).toHaveText('静音');await expect(display.locator('.media-demo')).toHaveAttribute('data-playing','true');
 await trial.getByRole('button',{name:'按下旋钮，切换静音',exact:true}).click();await expect(page.getByLabel('演示音量')).toHaveText('75%');
 await trial.getByRole('button',{name:'摇杆右',exact:true}).click();await expect(display.locator('.navigation-grid .selected')).toContainText('06');
 await trial.getByRole('button',{name:'摇杆上',exact:true}).click();await expect(display.locator('.navigation-grid .selected')).toContainText('03');
 await trial.getByRole('button',{name:'摇杆左',exact:true}).click();await expect(display.locator('.navigation-grid .selected')).toContainText('02');
 await trial.getByRole('button',{name:'K13 模型',exact:true}).click();await trial.getByRole('button',{name:'旋钮顺时针',exact:true}).click();await expect(page.getByLabel('演示音量')).toHaveText('80%');await expect(trial.getByText('推理强度')).toHaveCount(0);
 await trial.getByRole('button',{name:'复位试用',exact:true}).click();await expect(display).toHaveAttribute('data-screen','ready');await trial.getByRole('button',{name:'摇杆上',exact:true}).click();await expect(display.locator('.navigation-grid .selected')).toContainText('02');
});

for(const platform of ['windows','mac'] as const)test('application shortcut examples identify targets and '+platform+' chords',async({page},testInfo)=>{
 const popups:string[]=[];page.on('popup',popup=>popups.push(popup.url()));await page.goto('/#try');const trial=page.locator('#try');await trial.evaluate(element=>element.scrollIntoView({block:'start',behavior:'instant'}));await expect(page.locator('#hardware canvas')).toHaveCount(0);
 await trial.getByRole('tab',{name:/03\s*快捷键/}).click();
 const groups=[{name:'VS Code',target:'Visual Studio Code',windows:['Ctrl + Shift + P','Ctrl + `'],mac:['Cmd + Shift + P','Ctrl + `']},{name:'Google Chrome',target:'Google Chrome',windows:['Ctrl + T','Ctrl + L'],mac:['Cmd + T','Cmd + L']},{name:'Blender',target:'Blender',windows:['Tab','Space'],mac:['Tab','Space']}];
  await trial.getByRole('button',{name:platform==='mac'?'macOS':'Windows / Linux',exact:true}).click();
  for(const group of groups){
   await trial.getByRole('group',{name:'选择目标软件示例'}).getByRole('button',{name:group.name,exact:true}).click();
   await expect(trial.locator('.shortcut-context')).toContainText(group.target);
   for(let index=0;index<2;index++){
    const button=trial.locator('.shortcut-examples>button').nth(index);await expect(button.locator('.key-chord')).toHaveAttribute('aria-label',group[platform][index]);await button.click();
    await expect(trial.locator('.shortcut-feedback h4')).toContainText(group.target);await expect(trial.locator('.shortcut-feedback .key-chord')).toHaveAttribute('aria-label',group[platform][index]);
   }
  }
 await expect(trial).toContainText('不启动或控制已安装的应用');expect(popups).toEqual([]);
 await expect(trial.locator('.monitor-view')).toHaveCSS('opacity','1');await trial.locator('.try-desk').screenshot({path:'artifacts/trial-cleanup-'+testInfo.project.name+'-shortcuts.png',animations:'disabled',style:'.site-header,.skip-link{visibility:hidden!important}'});
});

test('build steps can be browsed in any order and changing steps cancels a running demo',async({page})=>{
 await page.goto('/#build');const lab=page.locator('#build');const nav=lab.getByRole('navigation',{name:'制作步骤'});const buttons=nav.getByRole('button');
 await expect(lab.locator('.build-tools,.build-asset-row')).toHaveCount(0);await expect(lab.getByRole('heading',{name:'打板和贴片交给嘉立创，手边准备这些。'})).toHaveCount(0);
 await expect(buttons).toHaveCount(7);for(const button of await buttons.all())await expect(button).toBeEnabled();
 const titles=['获取项目资料','配置电路板订单','配置 SMT 贴片','亲手完成装配','配置打印任务','体验固件烧录','检查全部输入'];
 for(const index of [6,3,5,1,4,2,0]){await buttons.nth(index).click();await expect(lab.locator('.step-heading h3')).toHaveText(titles[index]);await expect(buttons.nth(index)).toHaveAttribute('aria-current','step')}
 await expect(lab.getByRole('progressbar',{name:'制作完成进度'})).toHaveAttribute('aria-valuenow','0');await lab.getByRole('button',{name:'下一步',exact:false}).click();await expect(lab.locator('.step-heading h3')).toHaveText(titles[1]);
 await buttons.nth(2).click();await lab.getByRole('button',{name:'使用预设',exact:true}).nth(0).click();await lab.getByRole('button',{name:'使用预设',exact:true}).nth(1).click();await lab.getByRole('button',{name:'解析并匹配元件'}).click();await lab.getByRole('button',{name:'确认物料匹配'}).click();await lab.getByRole('button',{name:'运行 DFM 检查'}).click();await lab.getByRole('button',{name:'提交模拟 SMT 订单'}).click();await expect(lab.locator('.job-status')).toBeVisible();
 await buttons.nth(6).click();await expect(lab.locator('.step-heading h3')).toHaveText(titles[6]);await expect(lab.locator('.job-status')).toHaveCount(0);await expect(lab.locator('.step-feedback')).toContainText('上一项演示已取消');
 // Wait past the cancelled simulated job: it must not mark the old step complete later.
 await page.waitForTimeout(1400);await expect(lab.getByRole('progressbar',{name:'制作完成进度'})).toHaveAttribute('aria-valuenow','0');
 await buttons.nth(2).click();await expect(lab.locator('.file-name').nth(0)).toContainText('keyboard-bom.csv');await expect(lab.getByRole('button',{name:'提交模拟 SMT 订单'})).toBeEnabled();
 await buttons.nth(5).click();await expect(lab.getByRole('button',{name:'开始烧录'})).toBeDisabled();
});

test('seven-step build completes, rejects invalid files and can be reconfigured',async({page},testInfo)=>{
 await page.goto('/#build');const lab=page.locator('#build');const next=lab.getByRole('button',{name:'下一步'});
 await expect(next).toBeEnabled();await lab.getByRole('button',{name:'代码 ↓'}).click();await lab.getByRole('button',{name:'下载 ZIP ↓'}).click();await expect(lab.locator('.step-feedback')).toContainText(/已完成/);await next.click();
 await expect(lab.locator('.step-spec,.file-picker')).toHaveCount(0);await expect(lab.locator('.step-downloads a')).toHaveCount(0);const gerber=lab.getByRole('link',{name:'下载 Gerber 文件',exact:true});const [download]=await Promise.all([page.waitForEvent('download'),gerber.click()]);expect(download.suggestedFilename()).toBe('keyboard-gerbers.zip');expect(await download.failure()).toBeNull();expect(await readFile((await download.path())!)).toEqual(await readFile('public/downloads/keyboard-gerbers.zip'));await expect(lab.locator('.step-feedback')).toContainText('下载已开始');await expect(lab.locator('.fab-specs')).toContainText('95 × 95 毫米');await next.click();
 await lab.getByLabel('选择BOM / CSV').setInputFiles({name:'bad.csv',mimeType:'text/csv',buffer:Buffer.from('invalid,columns')});await expect(lab.getByRole('alert')).toContainText('BOM 缺少');await expect(lab.getByRole('button',{name:'解析并匹配元件'})).toBeDisabled();
 await lab.getByRole('button',{name:'使用预设'}).nth(0).click();await lab.getByRole('button',{name:'使用预设'}).nth(1).click();await lab.getByRole('button',{name:'解析并匹配元件'}).click();await lab.getByRole('button',{name:'确认物料匹配'}).click();await lab.getByRole('button',{name:'运行 DFM 检查'}).click();await lab.getByRole('button',{name:'提交模拟 SMT 订单'}).click();await expect(lab.locator('.step-feedback')).toContainText(/已完成/);await next.click();
 await lab.getByRole('button',{name:'选择机械轴'}).click();await lab.getByRole('button',{name:'安装 SW03',exact:true}).click();await lab.getByRole('button',{name:'自动安装剩余机械轴'}).click();await lab.getByRole('button',{name:'选择编码器'}).click();await lab.getByRole('button',{name:'安装 SW1',exact:true}).click();await lab.getByRole('button',{name:'选择摇杆'}).click();await lab.getByRole('button',{name:'安装 J1',exact:true}).click();await lab.getByRole('button',{name:'翻到背面'}).click();await lab.getByRole('button',{name:'演示焊接其余焊点'}).click();await lab.getByRole('button',{name:'确认手工装配'}).click();await next.click();
 await lab.getByRole('checkbox',{name:/旋钮/}).check();await lab.getByRole('button',{name:'启动打印演示'}).click();await expect(lab.locator('.step-feedback')).toContainText(/已完成/);await next.click();
 await expect(lab.getByRole('button',{name:'开始烧录'})).toBeDisabled();await lab.getByRole('button',{name:'点击连接'}).click();await lab.getByRole('button',{name:'使用预设'}).click();await lab.getByRole('button',{name:'开始烧录'}).click();await expect(lab.getByRole('button',{name:'校验固件'})).toBeEnabled({timeout:15000});await lab.getByRole('button',{name:'校验固件'}).click();await lab.getByRole('button',{name:'重新启动'}).click();await expect(lab.locator('.step-feedback')).toContainText(/已完成/);await next.click();
 await expect(lab.getByRole('button',{name:'完成全部测试'})).toBeDisabled();for(let i=1;i<=13;i++)await lab.getByRole('button',{name:`测试按键 ${i}`,exact:true}).click();for(const v of ['−','+'])await lab.getByRole('button',{name:`测试旋钮 ${v}`,exact:true}).click();for(const v of ['←','↑','↓','→'])await lab.getByRole('button',{name:`测试摇杆 ${v}`,exact:true}).click();await lab.getByRole('button',{name:'测试触摸板'}).click();for(const c of ['红','绿','蓝'])await lab.locator('.rgb-test').getByRole('button',{name:c,exact:true}).click();await lab.getByRole('button',{name:'完成全部测试'}).click();await expect(lab.getByRole('progressbar',{name:'制作完成进度'})).toHaveAttribute('aria-valuenow','7');await expect(lab.locator('.build-complete')).toBeVisible();
 await lab.locator('.build-lab').scrollIntoViewIfNeeded();await page.screenshot({path:`artifacts/build-free-${testInfo.project.name}-complete.png`});
 await lab.getByRole('navigation',{name:'制作步骤'}).getByRole('button',{name:/配置 SMT 贴片/}).click();await lab.getByRole('button',{name:'清除'}).nth(0).click();await expect(lab.getByRole('progressbar',{name:'制作完成进度'})).toHaveAttribute('aria-valuenow','2');await expect(lab.locator('.build-complete')).toHaveCount(0);
});
test('reduced motion, keyboard navigation and accessibility',async({page})=>{
 const errors:string[]=[];page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text())});await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await page.waitForLoadState('networkidle');const animation=await page.locator('.overview-product-float').evaluate(el=>getComputedStyle(el).animationName);expect(animation).toBe('none');
 const report=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();expect(report.violations).toEqual([]);
 await page.getByRole('button',{name:'K07 命令',exact:true}).click();await expect(page.getByLabel('搜索命令')).toBeFocused();await page.keyboard.press('Escape');await expect(page.getByRole('region',{name:'Codex 命令菜单示例',exact:true})).toHaveCount(0);expect(errors).toEqual([]);
});

test('all navigation anchors and narrow layouts',async({page})=>{
 await page.goto('/');
 for(const width of [320,768,1024]){await page.setViewportSize({width,height:900});await page.waitForTimeout(300);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy()}
 await page.setViewportSize({width:1440,height:1000});
 for(const id of ['overview','hardware','try','build','resources']){await page.locator(`nav[aria-label="主导航"] a[href="#${id}"]`).click();await expect(page).toHaveURL(new RegExp('#'+id+'$'));}
});
