import {test,expect,type Page} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

async function capture(page:Page,name:string){
 if(name==='flash')await page.locator('.boot-keyboard').evaluate(async element=>{await Promise.all(element.getAnimations().map(animation=>animation.finished));});
 if(['pcb','smt','assembly','flash'].includes(name)){
  const report=await new AxeBuilder({page}).include('#build').withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  expect(report.violations).toEqual([]);
 }
 if(process.env.BUILD_LAB_SCREENSHOTS)await page.locator('.lab-panel').screenshot({path:`${process.env.BUILD_LAB_SCREENSHOTS}/${name}-${test.info().project.name}.png`,animations:'disabled',style:'.site-header{visibility:hidden!important}'});
}

async function prepare(page:Page){
 await page.goto('/#build');
 const lab=page.locator('#build');
 await lab.getByRole('button',{name:'代码 ↓'}).click();
 await lab.getByRole('button',{name:'下载 ZIP ↓'}).click();
 await expect(lab.getByRole('button',{name:'下一步'})).toBeEnabled();
 await lab.getByRole('button',{name:'下一步'}).click();
 return lab;
}

// Catches submitting an unchecked order or carrying stale completion downstream.
test('PCB and SMT require review, matching and DFM before completion',async({page})=>{
 const lab=await prepare(page);
 await expect(lab.getByRole('button',{name:'提交模拟 PCB 订单'})).toBeDisabled();
 await lab.getByRole('button',{name:'使用预设'}).click();
 await lab.getByLabel('板子数量').selectOption('10');
 await lab.getByRole('button',{name:'检查 PCB 订单'}).click();
 await expect(lab.getByRole('button',{name:'提交模拟 PCB 订单'})).toBeEnabled();
 await lab.getByLabel('阻焊颜色').selectOption('purple');
 await expect(lab.getByRole('button',{name:'提交模拟 PCB 订单'})).toBeDisabled();
 await lab.getByRole('button',{name:'检查 PCB 订单'}).click();
 await capture(page,'pcb');
 await lab.getByRole('button',{name:'提交模拟 PCB 订单'}).click();
 await lab.getByRole('button',{name:'下一步'}).click();
 await lab.getByRole('button',{name:'使用预设'}).nth(0).click();
 await lab.getByRole('button',{name:'使用预设'}).nth(1).click();
 await lab.getByRole('button',{name:'解析并匹配元件'}).click();
 await expect(lab.getByText('STM32F072CBT6',{exact:true})).toBeVisible();
 await expect(lab.getByRole('button',{name:'提交模拟 SMT 订单'})).toBeDisabled();
 await lab.getByRole('button',{name:'确认物料匹配'}).click();
 await lab.getByRole('button',{name:'旋转选中元件'}).click();
 await expect(lab.locator('[data-part="U3"]')).toHaveAttribute('data-rotation','180');
 await expect(lab.getByRole('button',{name:'运行 DFM 检查'})).toBeEnabled();
 await lab.getByRole('button',{name:'运行 DFM 检查'}).click();
 await expect(lab.getByRole('alert')).toContainText('方向');
 await lab.getByRole('button',{name:'复位贴装方向'}).click();
 await lab.getByRole('button',{name:'运行 DFM 检查'}).click();
 await capture(page,'smt');
 await lab.getByRole('button',{name:'提交模拟 SMT 订单'}).click();
 await expect(lab.getByRole('button',{name:'下一步'})).toBeEnabled();
});

// Catches premature assembly completion, unsafe write ordering and a dead disconnect control.
test('assembly is reversible and interrupted flashing can be retried',async({page},testInfo)=>{
 test.setTimeout(120000);
 const errors:string[]=[]; page.on('pageerror',error=>errors.push(error.message));
 page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
 const lab=await prepare(page);
 await lab.getByRole('button',{name:'使用预设'}).click();
 await lab.getByRole('button',{name:'检查 PCB 订单'}).click();
 await lab.getByRole('button',{name:'提交模拟 PCB 订单'}).click();
 await lab.getByRole('button',{name:'下一步'}).click();
 await expect(lab.getByRole('button',{name:'使用预设'})).toHaveCount(2);
 await lab.getByRole('button',{name:'使用预设'}).nth(0).click();
 await lab.getByRole('button',{name:'使用预设'}).nth(1).click();
 await lab.getByRole('button',{name:'解析并匹配元件'}).click();
 await lab.getByRole('button',{name:'确认物料匹配'}).click();
 await lab.getByRole('button',{name:'运行 DFM 检查'}).click();
 await lab.getByRole('button',{name:'提交模拟 SMT 订单'}).click();
 await lab.getByRole('button',{name:'下一步'}).click();
 await expect(lab.getByRole('button',{name:'确认手工装配'})).toBeDisabled();
 await lab.getByRole('button',{name:'选择编码器'}).click();
 await lab.getByRole('button',{name:'安装 SW03',exact:true}).click();
 await expect(lab.locator('.lab-message')).toContainText('不匹配');
 await lab.getByRole('button',{name:'选择机械轴'}).click();
 if(testInfo.project.name==='desktop'){
  await lab.getByRole('button',{name:'选择机械轴'}).dragTo(lab.locator('.board-drawing'));
  await expect(lab.locator('.lab-message')).toContainText('尚未对准');
 }
 await lab.getByRole('button',{name:'安装 SW03',exact:true}).click();
 await expect(lab.getByText('已安装 1 / 15',{exact:true})).toBeVisible();
 await lab.getByRole('button',{name:'取下 SW03',exact:true}).click();
 await expect(lab.getByText('已安装 0 / 15',{exact:true})).toBeVisible();
 await lab.getByRole('button',{name:'安装 SW03',exact:true}).click();
 await lab.getByRole('button',{name:'自动安装剩余机械轴'}).click();
 await lab.getByRole('button',{name:'选择编码器'}).click();
 await lab.getByRole('button',{name:'安装 SW1',exact:true}).click();
 await lab.getByRole('button',{name:'选择摇杆'}).click();
 await lab.getByRole('button',{name:'安装 J1',exact:true}).click();
 await capture(page,'assembly-front');
 await lab.getByRole('button',{name:'三维检查'}).click();
 await expect(lab.locator('.assembly-scene')).toHaveAttribute('data-loaded','true',{timeout:30000});
 await expect(lab.locator('.assembly-scene canvas')).toBeVisible();
 await capture(page,'assembly-model');
 await lab.getByRole('button',{name:'安装视图'}).click();
 await lab.getByRole('button',{name:'翻到背面'}).click();
 const joint=lab.getByRole('button',{name:'焊接 SW03',exact:true});
 await joint.focus(); await page.keyboard.down('Space'); await page.waitForTimeout(850); await page.keyboard.up('Space');
 await expect(lab.getByText('已固定 1 / 15',{exact:true})).toBeVisible();
 await lab.getByRole('button',{name:'演示焊接其余焊点'}).click();
 await capture(page,'assembly');
 await expect(lab.getByRole('button',{name:'确认手工装配'})).toBeEnabled();
 await lab.getByRole('button',{name:'确认手工装配'}).click();
 await lab.getByRole('button',{name:'下一步'}).click();
 await lab.getByRole('button',{name:'启动打印演示'}).click();
 await lab.getByRole('button',{name:'下一步'}).click();
 await expect(lab.getByRole('button',{name:'开始烧录'})).toBeDisabled();
 await lab.getByRole('button',{name:'点击连接'}).click();
 await lab.getByRole('button',{name:'使用预设'}).click();
 await lab.getByRole('button',{name:'开始烧录'}).click();
 await expect(lab.getByRole('progressbar',{name:'固件写入进度'})).toHaveAttribute('aria-valuenow',/[1-9]/);
 await capture(page,'flash-writing');
 await lab.getByRole('button',{name:'断开连接'}).click();
 await expect(lab.getByRole('alert')).toContainText('连接已断开');
 await expect(lab.getByRole('button',{name:'校验固件'})).toBeDisabled();
 await lab.getByRole('button',{name:'点击连接'}).click();
 await lab.getByRole('button',{name:'重新烧录'}).click();
 await expect(lab.getByRole('button',{name:'校验固件'})).toBeEnabled({timeout:15000});
 await lab.getByRole('button',{name:'校验固件'}).click();
 await lab.getByRole('button',{name:'重新启动'}).click();
 await expect(lab.getByText('键盘已启动',{exact:true})).toBeVisible();
 await capture(page,'flash');
 await expect(lab.getByRole('button',{name:'下一步'})).toBeEnabled();
 expect(errors).toEqual([]);
 for(const width of [320,390,1440]){
  await page.setViewportSize({width,height:1000});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
 }
});
