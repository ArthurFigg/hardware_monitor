# Ícone na bandeja

**Ordem:** 5 de 7
**Depende de:** 04-abrir-com-o-windows-e-rodape (é ela que faz o app subir no boot; sem
bandeja, o app subiria minimizado na barra de tarefas e morreria ao ser fechado)
**Score:** 3
**Revisão:** pendente

## O que faz

O app ganha um ícone ao lado do relógio, colorido pelo pior status do momento, e fechar a
janela passa a esconder o app para lá em vez de encerrá-lo.

## Comportamento

### O ícone

- Quando o app abre, um ícone aparece na bandeja do sistema, ao lado do relógio.
- O ícone é colorido pelo **pior status** entre todos os recursos: verde quando todos estão
  em Normal, amarelo quando algum está em Atenção, vermelho quando algum está em Alerta.
  As cores são as mesmas do semáforo, sem inventar paleta nova.
- Quando o pior status muda, a cor do ícone acompanha.
- O texto que aparece ao passar o mouse mostra o estado resumido (ex: "Monitor de Hardware —
  CPU em Atenção").

### Esconder e mostrar

- Quando a pessoa **fecha a janela**, o app esconde a janela e continua rodando. A coleta não
  para, as notificações continuam funcionando.
- **Na primeira vez** que isso acontece, e só na primeira, aparece um aviso: "O monitor
  continua rodando. Clique no ícone ao lado do relógio para abrir de novo." Sem esse aviso a
  pessoa acha que fechou o app, e ele fica rodando invisível — comportamento que ela não pediu
  e não percebeu.
- Quando a pessoa **clica no ícone**, a janela reaparece. Se já estiver aberta, vem para a
  frente em vez de abrir outra.
- O menu do botão direito tem duas opções: **Abrir** e **Sair**.
- **Sair** encerra o app de verdade: para a thread de coleta, remove o ícone e fecha o
  processo. Sem essa opção a pessoa ficaria sem jeito de encerrar, já que fechar a janela
  agora só esconde.

### Regra de thread — nas duas direções

- Atualizar a **cor do ícone a partir da thread do Tkinter** é seguro e é assim que deve ser
  feito.
- O contrário **trava ou corrompe a interface em silêncio**: a thread do `pystray` nunca pode
  mexer em widget do Tkinter direto. O menu "Abrir" e o clique no ícone precisam passar por
  `widget.after(0, ...)` para serem executados na thread principal.
- Esta é a armadilha que o CLAUDE.md já documenta, aplicada aqui nas duas direções — e é o
  motivo de esta spec ter sido separada da spec 4.

### Quando a bandeja não está disponível

- Quando o `pystray` não carrega, ou o ambiente não tem bandeja, o app **volta ao
  comportamento de hoje**: fechar a janela encerra o app, e não há ícone.
- Nunca exibe erro, nunca impede o app de abrir. A janela e todos os cartões funcionam igual.

### O que não muda nesta spec

- A **notificação continua saindo do `plyer`**, como hoje. A migração para a bandeja fica
  para o projeto do histórico — ver "Decisões tomadas".
- Nenhum recurso, limite, texto ou leitura de hardware é tocado.

## Critérios verificáveis

- [ ] `uv run pytest -v` passa, incluindo os testes das specs anteriores
- [ ] Um teste comprova que o pior status entre os recursos determina a cor do ícone
      (todos Normal → verde; um em Atenção → amarelo; um em Alerta → vermelho)
- [ ] Um teste comprova que a cor usada é a mesma do semáforo, lida da mesma fonte
- [ ] Um teste comprova que fechar a janela não encerra o app e não para a coleta
- [ ] Um teste comprova que o aviso de "continua rodando" aparece na primeira vez e não na
      segunda
- [ ] Um teste comprova que "Sair" encerra a coleta e o processo
- [ ] Um teste comprova que o clique no ícone passa por `after(0, ...)` em vez de tocar o
      widget direto
- [ ] Um teste comprova que, com o `pystray` indisponível (import mockado levantando erro),
      o app abre normalmente e fechar a janela encerra
- [ ] `uv run main.py` abre o app, o ícone aparece na bandeja e muda de cor sob carga —
      verificação manual, já que o desenho do ícone não é testável automaticamente

## Módulos afetados

- `ui/bandeja.py` — **novo**. Cria e mantém o ícone, desenha a imagem colorida pelo status
  (com `Pillow`), monta o menu Abrir/Sair, e devolve indisponível em vez de levantar erro
  quando a bandeja não existe.
- `ui/app.py` — fechar a janela passa a esconder; ganha o aviso de primeira vez; informa o
  pior status à bandeja a cada atualização.
- `main.py` — sobe o ícone junto com a janela e encerra os dois no "Sair".
- `pyproject.toml` — acrescenta `pystray` e `Pillow`, com teto de versão conforme a regra do
  CLAUDE.md global.
- `tests/ui/test_bandeja.py` — **novo**. Cobre a lógica: qual cor para qual status, o que o
  menu faz, o que acontece quando a bandeja está indisponível. **Não** cobre o desenho do
  ícone nem a chamada real ao Windows.
- `tests/ui/test_app.py` — ganha os testes de fechar-esconde e do aviso de primeira vez.

## Não mexer

- `notifications/manager.py` e o `plyer` — a notificação **não** migra nesta spec.
- `hardware/recursos.py`, `processos.py`, `discos.py`, `desempenho.py` — specs 1, 2 e 3.
- `hardware/inicializacao.py` e o rodapé de uptime — spec 4.
- `hardware/thresholds.py` e qualquer limite.
- `ui/components/cards.py` e `ui/components/semaphore.py` — as **cores** do semáforo são lidas
  de lá, não redefinidas aqui.
- Leitura da placa de vídeo — spec 6.
- Empacotamento em `.exe` — spec 7. Vale saber que `pystray` e `Pillow` entram no que a spec 7
  terá de empacotar.

## Decisões tomadas

- **A notificação não migra nesta spec** → escolha do usuário. Motivo que sustenta: o clique
  na notificação só tem para onde levar quando existir a tela de resumo de uso, que é do
  projeto seguinte. Migrar agora entregaria uma capacidade que ninguém usa, dentro da spec
  mais arriscada do projeto. O custo aceito é mexer na notificação duas vezes — mas a segunda
  vez acontece já com a tela de destino definida.
- **O ícone colorido entra já** → escolha do usuário. É o que faz a bandeja valer a pena: sem
  cor, o app fica escondido e mudo. E entrega de graça o que o modo mini (C6) e a janela
  sempre por cima (A12) queriam — os dois descartados na triagem.
- **Menu com Abrir e Sair** → decidido sem perguntar. Sem "Sair", fechar a janela esconde e a
  pessoa fica sem jeito de encerrar o app.
- **Aviso de primeira vez ao fechar** → levantado na revisão de consequências de uso: fechar
  deixa de encerrar, e sem aviso a pessoa acha que fechou o app enquanto ele segue rodando
  invisível.
- **Sem bandeja, volta ao comportamento de hoje** → aplicação da regra "leitura que falha
  esconde a si mesma" a um recurso de interface: some o ícone, fechar volta a encerrar, e o
  resto do app continua igual.
- **Esta spec nasceu da divisão da spec 4 original** → a bandeja é a única parte do projeto
  com dependência nova **e** thread conversando com a interface. Separada para não prender o
  registro e o rodapé, que fecham rápido.

## Impacto no CLAUDE.md

- **Stack** → acrescentar `pystray` e `Pillow` como dependências, com as versões escolhidas.
- **Ciclo de vida da janela (a implementar na spec 4)** → a parte de fechar para a bandeja
  deixa de ser pendente; a seção passa a descrever o comportamento real e a apontar para o
  aviso de primeira vez.
- **Estrutura real do projeto** → acrescentar `ui/bandeja.py` e `tests/ui/test_bandeja.py`;
  atualizar a contagem de testes.
- **Decisões arquiteturais importantes** → acrescentar a regra de thread nas duas direções:
  atualizar o ícone a partir do Tkinter é seguro; a thread do `pystray` tocar widget não é, e
  precisa de `after(0, ...)`.
- **Testes — o que precisa estar coberto** → confirmar o item que já prevê o ícone da bandeja
  como não testável automaticamente; a lógica do módulo é coberta, o desenho não.
- **Melhorias — ver `aprovados.txt`** → marcar a spec 5 como especificada.
