import fs from 'node:fs';
const data=fs.readFileSync('src/data/product.ts','utf8');const urls=[...new Set(data.match(/https:\/\/[^'\s]+/g))];
const results=await Promise.all(urls.map(async url=>{try{const response=await fetch(url,{method:'HEAD',redirect:'follow',signal:AbortSignal.timeout(30000)});return {url,status:response.status,finalUrl:new URL(response.url).origin+new URL(response.url).pathname,ok:response.ok}}catch(error){return{url,ok:false,error:error.message}}}));
fs.mkdirSync('artifacts',{recursive:true});fs.writeFileSync('artifacts/resource-links.json',JSON.stringify({checkedAt:new Date().toISOString(),results},null,2));console.log(JSON.stringify(results,null,2));
if(results.some(r=>!r.ok))process.exitCode=1;
