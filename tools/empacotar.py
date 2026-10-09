"""Empacota a pasta docs/ num único worker da Cloudflare (dist/worker.js).

O worker leva todos os arquivos do app embutidos, então não depende do GitHub para responder.
"""
import base64
import gzip
import json
import pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent
docs = raiz / 'docs'
TIPOS = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.webmanifest': 'application/manifest+json',
    '.png': 'image/png',
    '.woff2': 'font/woff2',
    '.txt': 'text/plain; charset=utf-8',
}
TEXTO = {'.html', '.js', '.webmanifest', '.txt'}
SEM_CACHE = {'.html', '.js', '.webmanifest'}

arquivos = {}
for f in sorted(docs.rglob('*')):
    if f.is_dir() or f.suffix.lower() not in TIPOS:
        continue
    ext = f.suffix.lower()
    caminho = '/' + f.relative_to(docs).as_posix()
    if caminho == '/index.html':
        caminho = '/'
    dados = f.read_bytes()
    comprimido = ext in TEXTO
    corpo = base64.b64encode(gzip.compress(dados, 9, mtime=0) if comprimido else dados).decode()
    cache = 'no-cache' if ext in SEM_CACHE else 'public, max-age=86400'
    arquivos[caminho] = [TIPOS[ext], corpo, 1 if comprimido else 0, cache]

worker = 'const F=' + json.dumps(arquivos, separators=(',', ':')) + ''';
const bytes=b=>Uint8Array.from(atob(b),c=>c.charCodeAt(0));
export default{async fetch(req){
  const u=new URL(req.url); let p=u.pathname; if(p==='/index.html')p='/';
  const f=F[p]; if(!f)return new Response('Não encontrado',{status:404,headers:{'content-type':'text/plain; charset=utf-8'}});
  const [tipo,b64,gz,cache]=f; let corpo=new Blob([bytes(b64)]).stream();
  if(gz)corpo=corpo.pipeThrough(new DecompressionStream('gzip'));
  return new Response(corpo,{headers:{'content-type':tipo,'cache-control':cache,'x-content-type-options':'nosniff'}});
}};
'''
saida = raiz / 'dist' / 'worker.js'
saida.parent.mkdir(exist_ok=True)
saida.write_text(worker)
print(f'{saida.relative_to(raiz)}: {len(worker)} caracteres, {len(arquivos)} arquivos')
