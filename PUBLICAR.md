# Portfolio Studio V4 — Cloudflare Workers

## Primeira publicação (Windows / PowerShell)
1. Extraia o ZIP. Instale Node.js 22 LTS ou superior, abra o terminal na pasta que contém package.json.
2. Execute `npm install` e `npx wrangler login`. Use `npx wrangler whoami` para conferir a conta.
3. Execute `npx wrangler d1 create portfolio-catalogo`. Copie o database_id retornado para o arquivo wrangler.jsonc, substituindo apenas o UUID de zeros. Se já existir um banco exclusivo deste portfólio, use `npx wrangler d1 list` e reaproveite o ID em vez de criar outro. Não use o banco da AMIRA.
4. Ative R2 no painel da Cloudflare (pode exigir cadastro de meio de pagamento), depois execute `npx wrangler r2 bucket create portfolio-videomaker-media`. Se o bucket já existir e for exclusivo deste portfólio, reutilize-o. Mantenha-o privado: os objetos são servidos pelo Worker em /uploads/.
5. Execute `npm run db:online` e confirme a migração.
6. Execute `npx wrangler secret put PORTFOLIO_ADMIN_PASSWORD` e digite uma senha exclusiva, forte, de 12 a 256 caracteres. Se o Wrangler pedir autorização para criar o Worker, confirme. Se não conseguir criar antes do deploy, execute npm run deploy e repita a configuração do Secret imediatamente. O painel não permite login sem Secret válido. Nunca use a senha da AMIRA.
7. Execute `npm run deploy`. O terminal exibirá o URL verdadeiro do Worker. Abra o URL e acrescente /admin para editar o portfólio.
8. Homologue com seu cliente: abrir site anônimo, entrar com senha, salvar nome/textos, publicar vídeo, criar álbum com fotos, alterar grade/lista, abrir galeria, sair e verificar que /admin exige login. Teste no celular e em janela anônima. Confira os logs com `npx wrangler tail` se houver falha.

## Rodar localmente (opcional)
Crie `.dev.vars` (não publique) com `PORTFOLIO_ADMIN_PASSWORD="uma-senha-local-forte"`. Execute `npm run db:local` e `npm run dev`; abra o endereço exibido. O D1/R2 local é separado dos dados online. `npm test` roda testes com SQLite nativo do Node 22 e R2 simulado; não substitui teste real no Cloudflare.

## Atualizações depois de publicar
Para atualizar código, mantenha o mesmo nome do Worker, database_id e bucket. Faça backup; execute npm install se package.json mudou, npm run db:online se houver novas migrations e npm run deploy. Não recrie o banco nem o bucket. Alterações de conteúdo no painel são imediatas e não exigem deploy. A senha é configurada uma única vez e permanece entre deploys, salvo troca pelo responsável. Para trocar: `npx wrangler secret put PORTFOLIO_ADMIN_PASSWORD` (encerra sessões antigas). Diferentemente da V3, não há alteração de senha pelo painel.

## Importar dados da versão Flask (V2/V3, opcional)
Use somente em um D1 NOVO, vazio de trabalhos/álbuns e sem conteúdo cadastrado. Não execute em um portfólio já preenchido. Pare o servidor Flask e faça backup integral de data/ antes de começar. Não é necessário importar se ainda não cadastrou conteúdo.
Na raiz da V4, com Python 3 instalado:
```
python scripts/preparar_importacao.py "C:\caminho\portfolio-v3\data"
node scripts/enviar_midias.mjs importacao
npx wrangler d1 execute portfolio-catalogo --remote --file=importacao/dados.sql
```
Execute após criar o banco, bucket, aplicar migrations e configurar a conta. O script copia apenas mídias referenciadas e gera SQL; não envia senhas nem modifica o original. Não execute o SQL novamente se já aplicado. Se houver erro parcial, inspecione o banco antes de repetir. Configure uma nova senha no Secret. Arquivos antigos podem ultrapassar os limites de novos uploads; o envio por CLI não usa o limite do painel. Confira cada mídia importada.

## Limites e manutenção
- Novos uploads: 8 MiB por foto, 40 MiB por vídeo, até 100 fotos por álbum; cada arquivo enviado separadamente. Para filmes maiores, use links de YouTube ou Vimeo; para o vídeo de fundo, URL HTTPS direta MP4/WebM. O R2 não transcodifica vídeo; prefira MP4 H.264/AAC para compatibilidade.
- Os registros de conteúdo e sessões ficam em D1; binários em R2. As mídias publicadas são públicas por URL. Exclusões/alterações no painel não apagam automaticamente objetos antigos; uploads interrompidos também podem deixar objetos órfãos. Remova objetos somente após verificar que nenhuma referência permanece e após backup.
- R2 Standard oferece franquia mensal, mas pode exigir habilitação de cobrança. Confira os preços e limites atuais de Workers, D1 e R2 antes de entregar ao cliente: https://developers.cloudflare.com/r2/pricing/ e https://developers.cloudflare.com/workers/platform/pricing/.
- Backup do D1: `npx wrangler d1 export portfolio-catalogo --remote --output=backup-portfolio.sql`. Guarde em local privado (inclui sessões). Faça também backup separado dos objetos R2 usando ferramenta S3 compatível, sem expor credenciais. A exportação D1 não contém os arquivos R2.
- Aplicação para um cliente e um administrador. Rate limit básico por IP e sessão de 12 horas; para produção, considere regras adicionais de proteção no Cloudflare. As mídias passam por checagem de assinatura básica, não antivírus nem validação completa do codec. Não envie conteúdo sensível.
- Não foi publicado automaticamente; a conta, o identificador D1, o bucket e o Secret reais devem ser configurados pelo responsável.
