# Tela de resumo

**Ordem:** 3 de 3
**Depende de:** 08-historico-persistente, 09a-leitura-do-periodo
**Score:** 5
**Revisão:** pendente

## O que faz
Avisa que há resumo a cada N horas de uso e mostra o período numa tela que substitui os
cartões, com botão de voltar.

## Comportamento

### O aviso
- Quando a spec 09a diz que o resumo é devido **e houve pelo menos um episódio de alerta no
  período**, dispara uma notificação curta. Período calmo é silêncio.
- Devido sem nenhum episódio: o instante do último resumo é atualizado do mesmo jeito, para
  a contagem não acumular indefinidamente e disparar um aviso gigante depois.
- A notificação continua saindo pela biblioteca atual (`plyer`), e **não abre a tela ao ser
  clicada** — ela não detecta clique. O caminho é o ícone da bandeja, que já abre a janela
  desde a spec 5.

### Abrir o resumo
- O menu do ícone da bandeja ganha **"Ver resumo"**, entre "Abrir" e "Sair".
- Escolher "Ver resumo" mostra a janela (se estiver escondida) e troca o conteúdo para o
  resumo.
- Como qualquer ação vinda da thread do `pystray`, o pedido chega à interface por
  `after(0, ...)` — a regra do projeto para não tocar widget de fora da thread do Tkinter.

### A tela
- A janela é **uma só**: o resumo substitui os cartões na mesma janela, com um botão de
  voltar. Nada muda no ciclo de vida já resolvido — fechar esconde, bandeja, instância
  única.
- **A tela não volta sozinha para os cartões quando um recurso entra em Alerta.** Arrancar a
  tela de quem está lendo é pior que o problema; o ícone da bandeja fica vermelho e a
  notificação dispara igual. É a separação que o `_decisoes.md` chama de "o que a tela mostra
  e o que o app decide são coisas separadas".
- Enquanto o resumo está aberto, a atualização dos cartões continua rodando por baixo e não
  escreve em widget destruído — o laço agendado checa na entrada, como já faz hoje.
- O horário dos episódios sai **com a data junto quando o período atravessa mais de um dia**,
  e só com a hora quando cabe num dia. Sem isso "ficou pesado às 14h" fica ambíguo para quem
  usa o PC poucas horas por dia.
- Período com menos de N horas gravadas é exibido dizendo o tamanho real do período.
- Período sem nenhum episódio, aberto pelo menu, mostra as médias e diz que não houve nada
  grave. Quem foi olhar por conta própria merece resposta.
- Leitura ausente (banco indisponível) abre a tela e **explica que não há histórico**. Ação
  que a pessoa pediu nunca falha em silêncio — diferente de leitura que o app foi buscar
  sozinho, que esconde.

### O que a tela mostra
Poucas linhas, sem jargão, na ordem: o período coberto; quantas vezes ficou pesado e quando,
com o programa quando houver; a média de cada recurso; e, por unidade, quanto o disco encheu
no período e quanto resta. **Nunca previsão de quando enche.**

## Critérios verificáveis
- [ ] `uv run pytest -v` passa, e os testes anteriores continuam passando.
- [ ] Resumo devido com pelo menos um episódio dispara a notificação; devido sem episódio
      não dispara, mas atualiza o instante do último resumo.
- [ ] O menu da bandeja tem "Ver resumo", e escolhê-lo troca o conteúdo da janela.
- [ ] Com a janela escondida, "Ver resumo" mostra a janela **e** troca o conteúdo.
- [ ] O botão de voltar restaura os cartões, e os valores continuam atualizando depois.
- [ ] Com o resumo aberto, um recurso entrando em Alerta **não** troca a tela de volta.
- [ ] Período que atravessa duas datas exibe os horários com data; período de um dia, sem.
- [ ] Leitura ausente exibe a explicação, e a tela não fica em branco nem levanta erro.
- [ ] Período sem episódios exibe as médias mais a frase de que nada grave aconteceu.
- [ ] Nenhum teste cria um segundo root CTk — a fixture `raiz` de `conftest.py` é a única.

## Módulos afetados
- `ui/resumo.py` — **novo**. Monta o conteúdo do resumo a partir da leitura da spec 09a, e
  os textos da tela.
- `ui/app.py` — troca entre cartões e resumo, e o botão de voltar. Continua sem conhecer
  recurso por nome.
- `ui/bandeja.py` — o menu ganha "Ver resumo". A ação chega pronta de quem cria a bandeja,
  como já acontece com "Abrir" e "Sair"; `bandeja.py` segue sem conhecer widget.
- `notifications/manager.py` — ganha o disparo do aviso de resumo, que não é por recurso e
  por isso não passa por `Recurso`.
- `main.py` — liga a verificação periódica de "resumo devido" ao laço que já existe.
- `tests/ui/test_resumo.py` — **novo**.
- `tests/ui/test_app.py`, `tests/ui/test_bandeja.py`, `tests/notifications/test_manager.py` —
  ganham os testes da troca de conteúdo, do item de menu e do disparo.

## Não mexer
- `historico/` inteiro — criado pelas specs 08 e 09a. Esta spec **consome sem editar**.
- `hardware/` inteiro, `recursos.py`, `thresholds.py` — nada do que é medido ou
  classificado muda. Nenhum cartão novo, nenhum limite novo.
- `sistema/inicializacao.py`, `sistema/instancia_unica.py`, `sistema/caminhos.py` — o ciclo
  de vida da janela não muda.
- O rodapé (interruptor, botão de tema, linha de uptime) — o acesso ao resumo é pelo menu da
  bandeja, não por um quarto item ali.

## Decisões tomadas
- Janela nova ou troca de conteúdo? → **Troca o conteúdo.** Uma janela só para gerenciar, e
  nada muda no ciclo de vida já resolvido. Custo aceito: o estado atual da máquina sai da
  vista enquanto se lê o resumo.
- Quando a notificação dispara? → **A cada N horas de uso**, contadas desde o último resumo,
  não uma vez por dia. Cadência constante independente de calendário.
- Como abrir fora da notificação? → **Menu da bandeja.** Escolhido pelo assistente a pedido
  do usuário. Motivo: o rodapé já tem três elementos e é a área onde o CLAUDE.md registra a
  regra de empacotamento mais fácil de violar; o menu do ícone já é o lugar das ações
  secundárias, e a notificação aponta para o ícone — um lugar a aprender, não dois.
  Custo aceito: fica escondido de quem nunca clica com o botão direito no ícone.
- A tela volta sozinha quando entra um Alerta? → **Não.**
- Onde ficam os textos desta tela? → **Em `ui/resumo.py`.** A regra "origem única em
  `recursos.py`" trata de textos **de recurso**, e o resumo não fala de um recurso — fala
  de um período. **Isto resolve uma dívida aberta do CLAUDE.md**, que registrava a dúvida
  sobre se a regra passa a dizer "textos de recurso" ou se as frases soltas migram: passa a
  dizer textos de recurso. O teste que varre o projeto atrás de frase duplicada continua
  valendo para os textos de recurso.

## Impacto no CLAUDE.md
- **UI/UX** → acrescentar que a janela tem dois conteúdos (cartões e resumo) e que o acesso
  ao resumo é pelo menu da bandeja; registrar que a tela não volta sozinha em Alerta.
- **Ciclo de vida da janela** → acrescentar o item "Ver resumo" no menu do ícone.
- **Textos da interface** → a regra de origem única passa a dizer **textos de recurso**; os
  textos do resumo vivem em `ui/resumo.py`.
- **Qualidade — dívidas conhecidas** → marcar como resolvida a dívida "texto de interface
  mora em três lugares", que ficou pendente de decisão desde a v2.
- **Estrutura real do projeto** → acrescentar `ui/resumo.py` e `tests/ui/test_resumo.py`.
- **Melhorias — ver `aprovados.txt`** → marcar o `C3` como concluído.
- **Testes** → atualizar a contagem.
