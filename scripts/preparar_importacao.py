"""Exporta banco V2/V3 e lista mídias referenciadas. Não modifica o original."""
import argparse, json, sqlite3, re, shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('data',type=Path,help='Pasta data antiga');p.add_argument('--saida',type=Path,default=Path('importacao'));a=p.parse_args()
source=a.data.resolve(); db=source/'portfolio.db'; out=a.saida.resolve()
if not db.is_file(): raise SystemExit('portfolio.db não encontrado')
if out.exists(): raise SystemExit('A pasta de saída já existe; escolha outra para evitar sobrescrever.')
if source==out or source in out.parents: raise SystemExit('Escolha saída fora da pasta data original.')
with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True) as c:
    tables={r[0] for r in c.execute('SELECT name FROM sqlite_master WHERE type="table"')}
    records={t:list(c.execute(f'SELECT id,content FROM {t} ORDER BY id')) for t in ('config','projects','albums') if t in tables}
if not records.get('config'): raise SystemExit('Banco não possui configuração.')
files=set(); sql=[]
def scan(o):
    if isinstance(o,dict):
        for v in o.values():scan(v)
    elif isinstance(o,list):
        for v in o:scan(v)
    elif isinstance(o,str) and o.startswith('/uploads/'):
        k=o[9:]
        if not re.fullmatch(r'[a-f0-9]{32,64}\.(jpg|jpeg|png|webp|mp4|webm)',k): raise ValueError('Nome de mídia não suportado: '+k)
        if not (source/'uploads'/k).is_file(): raise ValueError('Mídia ausente: '+k)
        files.add(k)
for t,rows in records.items():
    for id,content in rows:
        val=json.loads(content);scan(val);s=json.dumps(val,ensure_ascii=False).replace("'","''")
        if t=='config': sql.append(f"UPDATE config SET content='{s}' WHERE id=1;")
        else: sql.append(f"INSERT INTO {t}(id,content) VALUES({int(id)},'{s}');")
out.mkdir(parents=True);(out/'uploads').mkdir()
for k in files: shutil.copy2(source/'uploads'/k,out/'uploads'/k)
(out/'dados.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
(out/'midias.json').write_text(json.dumps(sorted(files),indent=2),encoding='utf-8')
print(f'Exportação pronta: {out}. {len(files)} mídias. Nenhuma senha foi exportada.')
