// Source: device/app/README.md, Codex template table. These are shortcut demonstrations,
// not an integration with Codex, a connected device, or an installed application.
export type Platform='windows'|'mac';
export const codexKeys=[
 {id:'K01',action:'定位待处理会话',windows:'Ctrl + Alt + A',mac:'Cmd + Option + A',description:'跳到下一个需要你处理的会话，查看等待确认的请求。'},
 {id:'K02',action:'新建会话',windows:'Ctrl + N',mac:'Cmd + N',description:'在 Codex 中开始一个新的对话。'},
 ...[1,2,3,4].map((n,index)=>({id:'K0'+(index+3),action:'切换会话 '+n,windows:'Ctrl + Alt + '+n,mac:'Cmd + Option + '+n,description:'切换到最近的第 '+n+' 个会话，不必用鼠标查找。'})),
 {id:'K07',action:'打开命令菜单',windows:'Ctrl + K',mac:'Cmd + K',description:'打开 Codex 的命令菜单，查找要执行的操作。'},
 {id:'K08',action:'确认当前请求',windows:'Enter',mac:'Enter',description:'有待确认请求时，按下回车确认。作用取决于当前窗口的焦点。'},
 {id:'K09',action:'拒绝当前请求',windows:'Esc',mac:'Esc',description:'拒绝当前请求或退出当前操作，具体作用取决于窗口状态。'},
 {id:'K10',action:'切换终端面板',windows:'Ctrl + '+String.fromCharCode(96),mac:'Ctrl + '+String.fromCharCode(96),description:'在当前 Codex 会话中展开或收起终端。'},
 {id:'K11',action:'打开听写输入',windows:'Ctrl + Shift + D',mac:'Ctrl + Shift + D',description:'调用 Codex 的听写入口；语音识别由目标应用与系统提供。'},
 {id:'K12',action:'切换侧边会话',windows:'Ctrl + Alt + S',mac:'Cmd + Option + S',description:'在 Codex 中打开或收起侧边会话。'},
 {id:'K13',action:'打开模型选择器',windows:'Ctrl + Shift + M',mac:'Ctrl + Shift + M',description:'打开 Codex 的模型选择器，可选项以目标应用当前界面为准。'},
];

// Source: device/app/src/behaviors.rs: VSCODE_SHORTCUTS, CHROME_SHORTCUTS,
// BLENDER_SHORTCUTS. The companion app translates Cmd to Ctrl on Windows/Linux.
export type ShortcutApp='vscode'|'chrome'|'blender';
export const shortcutApps:{id:ShortcutApp;name:string;icon:string}[]=[
 {id:'vscode',name:'VS Code',icon:'⌘'},{id:'chrome',name:'Google Chrome',icon:'◎'},{id:'blender',name:'Blender',icon:'◇'},
];
export const shortcutExamples=[
 {id:'vscode-command',app:'vscode',target:'Visual Studio Code',action:'打开命令面板',windows:'Ctrl + Shift + P',mac:'Cmd + Shift + P',result:'在 VS Code 中查找并执行编辑器命令。'},
 {id:'vscode-terminal',app:'vscode',target:'Visual Studio Code',action:'切换终端',windows:'Ctrl + '+String.fromCharCode(96),mac:'Ctrl + '+String.fromCharCode(96),result:'展开或收起 VS Code 的集成终端。'},
 {id:'chrome-tab',app:'chrome',target:'Google Chrome',action:'新建标签页',windows:'Ctrl + T',mac:'Cmd + T',result:'在当前 Chrome 窗口中新建一个标签页。'},
 {id:'chrome-address',app:'chrome',target:'Google Chrome',action:'定位地址栏',windows:'Ctrl + L',mac:'Cmd + L',result:'将输入焦点移到 Chrome 地址栏，准备输入网址。'},
 {id:'blender-edit',app:'blender',target:'Blender',action:'切换编辑模式',windows:'Tab',mac:'Tab',result:'在 Blender 的适用编辑区域切换物体模式与编辑模式。'},
 {id:'blender-play',app:'blender',target:'Blender',action:'播放或暂停动画',windows:'Space',mac:'Space',result:'在 Blender 中播放或暂停时间线动画（使用默认快捷键设置）。'},
];
export const demoSessions=[
 {name:'检查键盘装配',detail:'有一个请求等待确认',message:'检查各部件的装配位置，并说明下一步操作。'},
 {name:'整理制造资料',detail:'会话 02 · 示例',message:'核对 PCB 制造文件和元件清单。'},
 {name:'查看按键映射',detail:'会话 03 · 示例',message:'说明旋钮、摇杆与触摸板的默认映射。'},
 {name:'准备外壳打印',detail:'会话 04 · 示例',message:'整理外壳打印前需要检查的项目。'},
];
