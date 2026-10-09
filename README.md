# calculadoras-uti
Uma ferramenta para ajudar médicos intensivistas a beira leito.

App: https://calculadoras-uti.ntg-trabalho.workers.dev

Drogas em bomba de infusão (vasoativas, sedação e analgesia, bloqueio neuromuscular), ventilação mecânica, assincronias e escala de coma de Glasgow. Depois de aberto uma vez, funciona sem internet e pode ser adicionado à tela inicial do celular.

## Publicação

1. Cada mudança na `main` roda o teste automático (`tests/autoteste.py`) num navegador com tela de celular.
2. Se passar, `tools/empacotar.py` monta o app num único worker da Cloudflare e guarda o pacote na branch `publicado`.
3. O pacote da branch `publicado` é o que vai para a Cloudflare.

Ao abrir, o próprio app refaz as contas e mostra no rodapé quantas conferiram.

## Estrutura

- `docs/` — o app (um único `index.html`, ícones, fonte e o service worker que faz funcionar offline)
- `tests/` — teste automático
- `tools/` — empacotador para a Cloudflare
- `.github/workflows/` — teste e empacotamento

## Fontes

- Apresentações, diluições padrão e tetos: planilha "Calculadoras para UTI". Onde um limite clínico é mais restritivo, vale o clínico.
- Dose inicial e faixa: bulas, diretriz SCCM 2013 e protocolos de UTI publicados. A fonte de cada número está no botão (i) de cada droga.
- Assincronias: Holanda MA et al., J Bras Pneumol 2018;44(4):321-333, e tabela de livro-texto de terapia intensiva.
- Fonte tipográfica: Atkinson Hyperlegible (Braille Institute), licença SIL OFL 1.1 em `docs/fonts/OFL.txt`.

Ferramenta de apoio à conferência; não substitui a prescrição nem a checagem à beira-leito.
