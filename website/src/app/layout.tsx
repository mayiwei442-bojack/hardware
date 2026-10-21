import type { Metadata } from 'next';
import '@fontsource/barlow-condensed/600.css';
import '@fontsource/barlow-condensed/700.css';
import '@fontsource/manrope/400.css';
import '@fontsource/manrope/500.css';
import '@fontsource/manrope/600.css';
import '@fontsource/ibm-plex-mono/400.css';
import './globals.css';
export const metadata: Metadata = {title: 'ACID ALLOY — 酸性合金', description: '13 个机械按键。旋钮、摇杆与触摸输入。探索酸性合金的硬件、交互与制作流程。'};
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="zh-CN"><body>{children}</body></html>; }
