// Cada arquivo é enviado separadamente; a página só é gravada após os uploads.
for(const form of document.querySelectorAll('form[data-confirm]')) form.addEventListener('submit',e=>{if(!confirm('Excluir este registro?'))e.preventDefault()});
for(const form of document.querySelectorAll('form[data-upload]')) form.addEventListener('submit',async e=>{
 e.preventDefault(); if(form.dataset.busy)return; const buttons=[...form.querySelectorAll('button')]; const feedback=document.querySelector('#feedback'); const data=new FormData(form); const files=[...form.querySelectorAll('input[type=file]')]; const total=files.reduce((n,f)=>n+f.files.length,0); let done=0;
 try{for(const input of files) for(const f of input.files){const max=input.dataset.kind==='image'?8:40;if(f.size>max*1024*1024)throw Error(`${f.name}: limite de ${max} MiB.`);}
 form.dataset.busy='1'; buttons.forEach(b=>b.disabled=true);
 for(const input of files){data.delete(input.name);for(const f of input.files){feedback.textContent=`Enviando mídia ${done+1} de ${total}: ${f.name}`;const r=await fetch('/admin/upload',{method:'POST',headers:{'Content-Type':f.type||'application/octet-stream','X-CSRF-Token':data.get('csrf'),'X-Media-Kind':input.dataset.kind},body:f});const j=await r.json();if(!r.ok)throw Error(j.error||'Falha no upload');data.append(input.name+'_uploaded',j.url);done++;}}
 feedback.textContent='Salvando alterações…';const r=await fetch(form.action,{method:'POST',body:new URLSearchParams(data)});if(!r.ok)throw Error(await r.text()); location.href=r.url;
 }catch(err){feedback.textContent=err.message;feedback.scrollIntoView({block:'center'});}finally{delete form.dataset.busy;buttons.forEach(b=>b.disabled=false);}
});
