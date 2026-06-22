# Avatar em PNG

Coloque aqui (nesta pasta `assets/avatar/`) os PNGs com **fundo transparente**:

- `base.png` — corpo/rosto do personagem (obrigatório p/ ativar o modo PNG)
- `mouth_closed.png` — boca fechada (opcional; se faltar, assume que o
  `base.png` já mostra a boca fechada por padrão)
- `mouth_open.png` — boca aberta, sobreposta na hora da fala (opcional;
  sem ela a boca não vai abrir visualmente)

Se `base.png` não existir, o programa usa automaticamente um rosto
desenhado em código (sem precisar de nenhum arquivo).

## Como funciona o lip-sync em PNG

A imagem `mouth_open.png` é desenhada por cima do `base.png` sempre que o
volume da voz passa de `AVATAR_MOUTH_OPEN_THRESHOLD` (em `config.py`).
A posição é definida por `AVATAR_MOUTH_ANCHOR = (x, y)` — porcentagem da
largura/altura do `base.png` onde fica o centro da boca. Ajuste esses
valores em `config.py` até a boca encaixar certinho no seu personagem.

## Dicas

- Gere os PNGs em ferramentas como Stable Diffusion, Canva, ou peça pra
  alguma IA de imagem gerar um personagem com a boca separada em camadas.
- Mantenha `base.png` e `mouth_open.png`/`mouth_closed.png` na MESMA
  escala/proporção (exportados do mesmo canvas), só recortando a região
  da boca — assim o anchor bate certo.
- `AVATAR_FLOAT_AMPLITUDE`/`AVATAR_FLOAT_SPEED` controlam a flutuação.
