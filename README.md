# Axé Digital (CEUG) – PWA de pontos cantados

App web (PWA): abre por link no celular/tablet, funciona offline e pode ser "instalado" na tela inicial. Sem loja de apps.

## Publicar (GitHub Pages)
1. Suba esta pasta para um repositório. 2. Settings → Pages → branch `main`, pasta `/ (root)`. 3. Abra o link no celular → menu do navegador → "Adicionar à tela inicial".

## Fonte dos dados
`data/pontos.json` vem da **Apostila de Pontos Cantados do CEUG v2.0 (nov/2022)** – fonte oficial.
Regerar: `python3 tools/parse_ceug.py && python3 tools/build_data.py tools/raw_ceug.json`
(precisa de `tools/ceug.txt`, gerado com `pdftotext -layout apostila.pdf tools/ceug.txt`).

Ao atualizar os dados, aumente `V` em `sw.js` (ex.: `axe-v2`) para o cache renovar.

## Recursos
Busca sem acento (título, entidade, verso) · Categorias com filtro por tipo (chamada, louvação, subida…) · Gira de Hoje (abertura + linhas escolhidas, toque longo marca como cantado) · Favoritos · Leitor com fonte ajustável e tela sempre ligada · Modo escuro.
