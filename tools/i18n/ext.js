const fs=require('fs'),acorn=require('acorn');
const html=fs.readFileSync(process.argv[2],'utf8');
const re=/<script>([\s\S]*?)<\/script>/g;let m,out=[];
while((m=re.exec(html))){const code=m[1],base=m.index+8;
  const ast=acorn.parse(code,{ecmaVersion:2022,ranges:true});
  (function walk(n){if(!n||typeof n.type!=="string")return;
    if(n.type==="Literal"&&typeof n.value==="string"&&/[가-힣]/.test(n.value))out.push({k:"L",s:base+n.start,e:base+n.end,v:n.value,raw:code.slice(n.start,n.end)});
    if(n.type==="TemplateElement"&&/[가-힣]/.test(n.value.raw))out.push({k:"T",s:base+n.start,e:base+n.end,v:n.value.raw});
    for(const k in n){const c=n[k];if(Array.isArray(c))c.forEach(walk);else if(c&&typeof c.type==="string")walk(c);}})(ast);}
fs.writeFileSync('/tmp/segs.json',JSON.stringify(out));
const u=new Set(out.map(o=>o.v));let ch=0;u.forEach(x=>ch+=x.length);
console.log(out.length,u.size,ch);
