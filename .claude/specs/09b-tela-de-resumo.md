# Tela de resumo

**Ordem:** 3 de 3
**Depende de:** 08-historico-persistente, 09a-leitura-do-periodo
**Score:** 5
**Revisão:** aprovada

## O que faz
Notifica que há resumo a cada N horas de PC ligado e mostra o período numa tela que
substitui os cartões, com botão de voltar.

## Comportamento

### A notificação
- Quando a spec 09a diz que o resumo é devido **e houve pelo menos um episódio de alerta no
  período**, dispara uma notificação curta. Período calmo é silêncio.
- Devido sem nenhum episódio: o instante do último resumo é marcado como entregue do mesmo
  jeito, para a contagem não acumular indefinidamente e disparar uma notificação gigante
  depois. Quem marca é esta spec, chamando a função que a 09a criou em `sistema/estado.py`.
- **Esta é a única notificação do app que não sai de um recurso em Alerta.** A regra fixa
  "notificações só disparam no estado Alerta" passa a dizer **notificação de recurso**, e o
  motivo dela continua valendo: ela existe para 60% a 84% de CPU não virar ruído. O resumo
  não é um recurso pesado, é um relatório de tempo decorrido, e sai no máximo a cada 10
  horas de PC ligado.
- A notificação continua saindo pela biblioteca atual (`plyer`), e **não abre a tela ao ser
  clicada** — ela não detecta clique. O texto dela **não cita o ícone da bandeja**: manda
  abrir o monitor, e serve igual na máquina onde a bandeja não subiu.

### Abrir o resumo
- O menu do ícone da bandeja ganha **"Ver resumo"**, entre "Abrir" e "Sair".
- Escolher "Ver resumo" mostra a janela (se estiver escondida) e troca o conteúdo para o
  resumo.
- Como qualquer ação vinda da thread do `pystray`, o pedido chega à interface por
  `after(0, ...)` — a regra do projeto para não tocar widget de fora da thread do Tkinter.
- **Sem bandeja no ar, um botão "Ver resumo" aparece no rodapé** — e só nesse caso. O
  CLAUDE.md registra que a bandeja pode não subir, e ali o menu não existe: sem o botão, o
  recurso inteiro ficaria inalcançável numa máquina em que todo o resto funciona. O botão
  não aparece junto do menu porque caminho alternativo existe pela ausência do principal,
  nunca duplicado ao lado dele — a mesma razão que faz o contador "(2/2)" do Disco sumir
  quando há uma unidade só.
- O rodapé usa `grid`, então acrescentar um elemento ali não esbarra na regra de packing
  que motivou o "não mexer" original.

### A tela
- A janela é **uma só**: o resumo substitui os cartões na mesma janela, com um botão de
  voltar. Nada muda no ciclo de vida já resolvido — fechar esconde, bandeja, instância
  única.
- **A tela não volta sozinha para os cartões quando um recurso entra em Alerta.** Arrancar a
  tela de quem está lendo é pior que o problema; o ícone da bandeja fica vermelho e a
  notificação dispara igual. É a separação que o `_decisoes.md` chama de "o que a tela mostra
  e o que o app decide são coisas separadas".
- **Os cartões são escondidos, nunca destruídos.** A checagem que o laço agendado já faz na
  entrada é de app parado (`_rodando`), e ela não protege nada com o app rodando e o resumo
  na frente: widget destruído continuaria sendo escrito. Escondendo, o laço segue
  atualizando widget vivo e o botão de voltar não precisa reconstruir nada.
- O horário dos episódios sai **com a data junto quando o período atravessa mais de um dia**,
  e só com a hora quando cabe num dia. Sem isso "ficou pesado às 14h" fica ambíguo para quem
  usa o PC poucas horas por dia.
- Período com menos de N horas gravadas é exibido dizendo o tamanho real do período.
- **Quando parte do período é lacuna, a tela diz quanto foi medido.** "10 horas de PC
  ligado, 4 delas com o monitor aberto" é honesto; exibir médias de 4 horas sob o rótulo de
  10 não é.
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
- [ ] Resumo devido com pelo menos um episódio dispara a notificação.
- [ ] Resumo devido sem nenhum episódio não dispara notificação.
- [ ] Resumo devido sem nenhum episódio marca o instante do último resumo como entregue.
- [ ] O texto da notificação não cita o ícone da bandeja.
- [ ] Nenhuma frase da notificação de resumo é escrita em `notifications/manager.py`.
- [ ] O menu da bandeja tem "Ver resumo", e escolhê-lo troca o conteúdo da janela.
- [ ] Com a janela escondida, "Ver resumo" mostra a janela.
- [ ] Com a bandeja no ar, o rodapé **não** tem botão de resumo.
- [ ] Sem bandeja no ar, o rodapé tem o botão, e ele abre o resumo.
- [ ] O botão de voltar restaura os cartões, e os valores continuam atualizando depois.
- [ ] Os cartões continuam existindo enquanto o resumo está na frente — nenhum é destruído.
- [ ] Com o resumo aberto, um recurso entrando em Alerta **não** troca a tela de volta.
- [ ] Período que atravessa duas datas exibe os horários com data; período de um dia, sem.
- [ ] Período com lacuna exibe quantos minutos foram medidos, além do tamanho do período.
- [ ] Leitura ausente exibe a explicação, e a tela não fica em branco nem levanta erro.
- [ ] Período sem episódios exibe as médias mais a frase de que nada grave aconteceu.
- [ ] Recurso sem amostra no período não aparece como 0% na tela.
- [ ] Nenhum teste cria um segundo root CTk — a fixture `raiz` de `conftest.py` é a única.

## Módulos afetados
- `ui/resumo.py` — **novo**. Monta o conteúdo do resumo a partir da leitura da spec 09a, os
  textos da tela **e o título e o corpo da notificação de resumo**. O `manager.py` recebe
  texto pronto, como já recebe dos recursos — o CLAUDE.md proíbe frase escrita lá dentro.
- `ui/app.py` — troca entre cartões e resumo, o botão de voltar, e o botão de reserva no
  rodapé quando não há bandeja. Continua sem conhecer recurso por nome.
- `ui/bandeja.py` — o menu ganha "Ver resumo". A ação chega pronta de quem cria a bandeja,
  como já acontece com "Abrir" e "Sair"; `bandeja.py` segue sem conhecer widget.
- `notifications/manager.py` — ganha o disparo da notificação de resumo, que não é por
  recurso e por isso não passa por `Recurso`, e recebe título e corpo já resolvidos.
- `sistema/estado.py` — **chamado, não criado**: marca o resumo como entregue pela função
  que a spec 09a escreveu.
- `main.py` — liga a verificação periódica de "resumo devido" ao laço que já existe.
- `tests/ui/test_resumo.py` — **novo**.
- `tests/ui/test_app.py`, `tests/ui/test_bandeja.py`, `tests/notifications/test_manager.py`,
  `tests/test_recursos.py` — ganham os testes da troca de conteúdo, do item de menu, do
  disparo e da origem das frases.

## Não mexer
- `historico/` inteiro — criado pelas specs 08 e 09a. Esta spec **consome sem editar**.
- `hardware/` inteiro, `recursos.py`, `thresholds.py` — nada do que é medido ou
  classificado muda. Nenhum cartão novo, nenhum limite novo.
- `sistema/inicializacao.py`, `sistema/instancia_unica.py`, `sistema/caminhos.py` — o ciclo
  de vida da janela não muda.
- O rodapé (interruptor, botão de tema, linha de uptime) — nenhum deles muda, e o acesso ao
  resumo continua sendo o menu da bandeja. O botão de reserva é a única adição ali, e só
  existe quando a bandeja não subiu.

## Decisões tomadas
- Janela nova ou troca de conteúdo? → **Troca o conteúdo.** Uma janela só para gerenciar, e
  nada muda no ciclo de vida já resolvido. Custo aceito: o estado atual da máquina sai da
  vista enquanto se lê o resumo.
- Quando a notificação dispara? → **A cada N horas de PC ligado**, contadas desde o último
  resumo, não uma vez por dia. Cadência constante independente de calendário.
- Como abrir fora da notificação? → **Menu da bandeja.** Escolhido pelo assistente a pedido
  do usuário. Motivo: o rodapé já tem três elementos e é a área onde o CLAUDE.md registra a
  regra de empacotamento mais fácil de violar; o menu do ícone já é o lugar das ações
  secundárias, e a notificação aponta para o ícone — um lugar a aprender, não dois.
  Custo aceito: fica escondido de quem nunca clica com o botão direito no ícone.
- E na máquina onde a bandeja não sobe? → **Botão de reserva no rodapé, só nesse caso.**
  Decidido pelo assistente a pedido do usuário em 12/09/2026. As outras saídas eram deixar
  o recurso inalcançável ou não tratar nada — a segunda faria a notificação apontar para um
  ícone inexistente, que é o comportamento que o projeto proíbe em "ação que a pessoa pediu
  nunca falha em silêncio". Custo aceito: um elemento condicional na tela.
- A tela volta sozinha quando entra um Alerta? → **Não.**
- Onde ficam os textos desta tela? → **Em `ui/resumo.py`.** A regra "origem única em
  `recursos.py`" trata de textos **de recurso**, e o resumo não fala de um recurso — fala
  de um período. **Isto resolve uma dívida aberta do CLAUDE.md**, que registrava a dúvida
  sobre se a regra passa a dizer "textos de recurso" ou se as frases soltas migram: passa a
  dizer textos de recurso. O teste que varre o projeto atrás de frase duplicada continua
  valendo para os textos de recurso.

## Impacto no CLAUDE.md
- **Regras fixas** e **Não fazer** → a regra "notificações só disparam no estado Alerta"
  passa a dizer **notificação de recurso**; a notificação de resumo é por tempo decorrido.
  O que a regra proibia — avisar em Atenção — continua proibido.
- **UI/UX** → acrescentar que a janela tem dois conteúdos (cartões e resumo), que o acesso
  ao resumo é pelo menu da bandeja, com botão no rodapé só quando a bandeja não sobe; e
  registrar que a tela não volta sozinha em Alerta.
- **Ciclo de vida da janela** → acrescentar o item "Ver resumo" no menu do ícone.
- **Textos da interface** → a regra de origem única passa a dizer **textos de recurso**; os
  textos do resumo vivem em `ui/resumo.py`.
- **Qualidade — dívidas conhecidas** → marcar como resolvida a dívida "texto de interface
  mora em três lugares", que ficou pendente de decisão desde a v2.
- **Estrutura real do projeto** → acrescentar `ui/resumo.py` e `tests/ui/test_resumo.py`.
- **Melhorias — ver `aprovados.txt`** → marcar o `C3` como concluído.
- **Testes** → atualizar a contagem.
