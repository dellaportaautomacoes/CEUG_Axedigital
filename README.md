# Axé Digital (CEUG) – PWA de pontos cantados

App web (PWA): abre por link no celular/tablet, funciona offline e pode ser "instalado" na tela inicial. Sem loja de apps.

## Publicar (GitHub Pages)
1. Suba esta pasta para um repositório. 2. Settings → Pages → branch `main`, pasta `/ (root)`. 3. Abra o link no celular → menu do navegador → "Adicionar à tela inicial".

## Fontes dos dados (campo `fonte` em cada ponto)
- **ceug** – Apostila CEUG v2.0 (oficial, aparece por padrão)
- **terreiro** – pontos.pdf · **t1540** – 1.540 Pontos Cantados · **jurema** – Pontos de Jurema (Mestres) · **p3333** – 3333 Exu/Pomba-Gira (OCR)
- Botão "Só CEUG / Todas as fontes" no topo do app liga as fontes complementares. Pontos idênticos a outro já cadastrado não são duplicados.
- Pontos com `revisar: true` mostram aviso no leitor. Aba **Toques** = Guia Prático de Toques (OCR).

## Fonte oficial
`data/pontos.json` vem da **Apostila de Pontos Cantados do CEUG v2.0 (nov/2022)** – fonte oficial.
Regerar tudo: `python3 tools/build_all.py` (usa os `tools/raw_*.json` e `tools/pontos_ceug.json`).
(precisa de `tools/ceug.txt`, gerado com `pdftotext -layout apostila.pdf tools/ceug.txt`).

Ao atualizar os dados, aumente `V` em `sw.js` (ex.: `axe-v2`) para o cache renovar.

## Recursos
Busca sem acento (título, entidade, verso) · Categorias com filtro por tipo (chamada, louvação, subida…) · Gira de Hoje (abertura + linhas escolhidas, toque longo marca como cantado) · Favoritos · Leitor com fonte ajustável e tela sempre ligada · Modo escuro.

## Nuvem (Supabase) – envio e aprovação de pontos
1. No Supabase: SQL Editor → New query → cole `tools/supabase_setup.sql` → Run.
2. O responsável cria conta no app (aba ➕ Inserir). Depois rode no SQL Editor: `update perfis set papel='admin' where email='EMAIL_DO_RESPONSAVEL';`
3. `config.js` guarda só a chave pública (publishable). Nunca coloque a chave secret/service_role.
