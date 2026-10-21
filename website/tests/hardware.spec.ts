import {test,expect,type Page} from '@playwright/test';
import {readFile} from 'node:fs/promises';

async function scrollHardware(page:Page,viewports:number){
 await page.locator('#hardware').evaluate((element,offset)=>{
  const height=element.querySelector('.hardware-viewport')!.clientHeight;
  window.scrollTo({top:(element as HTMLElement).offsetTop+height*offset,behavior:'instant'});
 },viewports);
}

test('scroll starts at a full viewport, reverses, focuses parts and downloads real files',async({page},info)=>{
 test.setTimeout(180000);
 page.setDefaultTimeout(30000);
 const errors:string[]=[];
 const failed:string[]=[];
 page.on('pageerror',error=>errors.push(error.message));
 page.on('requestfailed',request=>failed.push(request.url()));
 await page.goto('/');
 const hardware=page.locator('#hardware');
 await scrollHardware(page,-.35);
 await expect(hardware).toHaveAttribute('data-loaded','true',{timeout:60000});
 await expect(hardware).toHaveAttribute('data-progress','0.000');
 await expect(page.locator('.hardware-part-label')).toHaveCount(0);
 await scrollHardware(page,0);
 await expect(page.locator('.hardware-viewport')).toHaveCSS('position','sticky');
 expect(Math.abs((await page.locator('.hardware-viewport').boundingBox())!.y)).toBeLessThan(2);
 await page.screenshot({path:`artifacts/hardware-${info.project.name}-assembled.png`});
 await scrollHardware(page,1.1);
 await expect.poll(async()=>Number(await hardware.getAttribute('data-progress'))).toBeGreaterThan(.4);
 await expect(page.locator('.hardware-part-label')).toHaveCount(0);
 await page.screenshot({path:`artifacts/hardware-${info.project.name}-midway.png`});
 await scrollHardware(page,2.5);
 await expect(hardware).toHaveAttribute('data-phase','exploded',{timeout:45000});
 await expect(page.getByRole('group',{name:'选择硬件部件'})).toBeVisible();
 await expect(page.locator('.hardware-part-label')).toHaveCount(8);
 await page.screenshot({path:`artifacts/hardware-${info.project.name}-exploded.png`});
 await page.getByRole('button',{name:'键帽',exact:true}).click();
 await expect(hardware).toHaveAttribute('data-focus-ready','true',{timeout:30000});
 await expect(page.getByRole('complementary',{name:'键帽下载'})).toBeVisible();
 const downloadEvent=page.waitForEvent('download');
 await page.getByRole('link',{name:/下载此键帽/}).click();
 const download=await downloadEvent;
 expect(download.suggestedFilename()).toBe('acid-alloy-keycap-SW03.stl');
 const stl=await readFile((await download.path())!);
 expect(stl.length).toBe(84+50*stl.readUInt32LE(80));
 expect(stl.readUInt32LE(80)).toBeGreaterThan(100);
 await page.screenshot({path:`artifacts/hardware-${info.project.name}-keycap.png`});
 const before=await page.locator('#hardware canvas').screenshot();
 const canvas=await page.locator('#hardware canvas').boundingBox();
 if(info.project.name==='mobile'){
  const session=await page.context().newCDPSession(page);
  await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:canvas!.width*.45,y:canvas!.height*.37}]});
  for(let step=1;step<=8;step++)await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:canvas!.width*(.45+step*.025),y:canvas!.height*.37}]});
  await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 }else{
  await page.mouse.move(canvas!.width*.45,canvas!.height*.42);
  await page.mouse.down();await page.mouse.move(canvas!.width*.67,canvas!.height*.48,{steps:12});await page.mouse.up();
 }
 await page.waitForTimeout(600);
 const after=await page.locator('#hardware canvas').screenshot();
 expect(after.equals(before)).toBe(false);
 await page.screenshot({path:`artifacts/hardware-${info.project.name}-keycap-rotated.png`});
 await page.getByRole('button',{name:/返回解构总览/}).click();
 await expect(hardware).toHaveAttribute('data-phase','exploded');
 await page.getByRole('button',{name:'PCB',exact:true}).click();
 await expect(hardware).toHaveAttribute('data-focus-ready','true',{timeout:30000});
 await expect(page.getByRole('complementary',{name:'PCB下载'})).toContainText('95 × 95 mm');
 for(const link of await page.locator('.hardware-downloads a').all()){
  const response=await page.request.get((await link.getAttribute('href'))!);
  expect(response.ok()).toBeTruthy();expect((await response.body()).length).toBeGreaterThan(100);
 }
 const pcbEvent=page.waitForEvent('download');
 await page.getByRole('link',{name:/下载打板材料包/}).click();
 const pcb=await pcbEvent;
 expect(pcb.suggestedFilename()).toBe('keyboard-pcb-fabrication.zip');
 expect((await readFile((await pcb.path())!)).subarray(0,2).toString()).toBe('PK');
 await page.screenshot({path:`artifacts/hardware-${info.project.name}-pcb.png`});
 await page.keyboard.press('Escape');
 await expect(hardware).toHaveAttribute('data-phase','exploded');
 await page.waitForTimeout(1600);
 await page.locator('#hardware canvas').click({position:{x:canvas!.width*.49,y:canvas!.height*(info.project.name==='mobile'?.32:.32)}});
 await expect(hardware).toHaveAttribute('data-phase','inspecting',{timeout:15000});
 await page.keyboard.press('Escape');
 await scrollHardware(page,0);
 await expect(hardware).toHaveAttribute('data-progress','0.000');
 await expect(page.locator('.hardware-part-label')).toHaveCount(0,{timeout:30000});
 await scrollHardware(page,3.6);
 expect((await page.locator('.hardware-viewport').boundingBox())!.y).toBeLessThan(0);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 expect(errors).toEqual([]);
 expect(failed.filter(url=>!url.includes('__nextjs'))).toEqual([]);
});

test('model load failure offers a working retry',async({page})=>{
 test.setTimeout(90000);
 let first=true;
 await page.route('**/assets/keyboard-exploded.glb*',route=>{
  if(first){first=false;return route.fulfill({status:503,body:'Unavailable'});}
  return route.continue();
 });
 await page.goto('/');
 await scrollHardware(page,0);
 await expect(page.locator('#hardware').getByRole('alert')).toContainText('模型暂时无法加载',{timeout:45000});
 await page.getByRole('button',{name:'重新加载',exact:true}).click();
 await expect(page.locator('#hardware')).toHaveAttribute('data-loaded','true',{timeout:45000});
 await expect(page.locator('#hardware').getByRole('alert')).toHaveCount(0);
});
