# Abrir com o Windows e uptime no rodapé

**Ordem:** 4 de 7
**Depende de:** nenhuma (independente das specs 1, 2 e 3 — toca outros arquivos)
**Score:** 5
**Revisão:** aprovada

## O que faz

O app passa a poder abrir junto com o Windows, minimizado, com um interruptor reversível na
própria janela; e o rodapé mostra há quanto tempo a máquina está ligada.

## Comportamento

### Abrir com o Windows

- Quando o interruptor é **marcado**, o app escreve uma entrada na chave `Run` do usuário
  (`HKCU`), que não exige administrador.
- Quando o interruptor é **desmarcado**, a entrada é removida. Sem passo extra, sem confirmação.
- Quando o app abre, ele **lê a chave** e marca ou desmarca o interruptor conforme o que
  encontrar. Não existe arquivo de configuração: a entrada no registro **é** o estado, e por
  isso o interruptor nunca discorda da realidade — inclusive se a pessoa remover a entrada por
  fora, pelo Gerenciador de Tarefas.
- Quando o app sobe por causa dessa entrada, ele abre **minimizado** e nunca rouba a tela.
  Todas as 10 entradas já presentes nesta máquina usam alguma variação de silencioso
  (`-silent`, `--minimized`, `--background`), e o app segue a convenção.
- Quando aberto normalmente pelo usuário, abre como hoje: janela visível.
- O argumento que a entrada do registro passa é **`--minimizado`** (português, como o resto
  do código). O `.exe` da spec 7 precisa aceitar exatamente esse.

### Quando escrever no registro falha

- Quando a escrita falha (antivírus bloqueando, política corporativa), o interruptor
  **volta sozinho para desmarcado** e aparece a linha: "Não foi possível ativar. Algum
  programa de segurança pode estar bloqueando."
- Isso é diferente da regra geral do projeto de "leitura que falha esconde a si mesma":
  aqui não é leitura, é uma **ação que a pessoa pediu**. Falhar em silêncio deixaria a caixa
  marcada e o app não abriria no boot seguinte — a pessoa só descobriria pela ausência.
- Só desmarcar, sem texto, pareceria defeito ("cliquei e não marcou").
- O app continua funcionando normalmente; só esse recurso fica indisponível.

### Caminho escrito no registro

- O caminho apontado pela entrada é resolvido **em tempo de execução**, a partir de como o
  app está rodando.
- Em desenvolvimento, aponta para o `pythonw.exe` do ambiente e o `main.py` —
  `pythonw`, não `python`, senão pisca uma janela preta de terminal a cada boot.
- Na versão distribuída, aponta para o `.exe` da spec 7.
- **Nunca** escrever caminho fixo da máquina de quem desenvolveu.

### Uptime no rodapé

- O rodapé mostra há quanto tempo a **máquina** está ligada, não há quanto tempo o app está
  aberto: "Ligado há 5h 23min".
- O texto fica ao lado do botão de tema, em tamanho menor e discreto. Não é cartão, não tem
  cor, não tem semáforo — não existe "uptime em alerta".
- O valor é atualizado a cada minuto. Atualizar a cada segundo faria o rodapé mudar sem
  motivo.
- Quando a leitura falha, a linha simplesmente não aparece.

## Critérios verificáveis

- [ ] `uv run pytest -v` passa, incluindo os testes das specs anteriores
- [ ] Um teste comprova que marcar o interruptor escreve a entrada na chave `Run` (registro
      mockado)
- [ ] Um teste comprova que desmarcar remove a entrada
- [ ] Um teste comprova que o app lê a chave ao abrir e reflete o estado no interruptor
- [ ] Um teste comprova que falha na escrita desmarca o interruptor e produz a linha de aviso
      (escrita mockada levantando erro)
- [ ] Um teste comprova que o caminho escrito usa `pythonw.exe` e nunca contém caminho fixo
      da máquina de desenvolvimento
- [ ] Um teste comprova que o uptime é formatado como "Ligado há 5h 23min" a partir de um
      instante de boot conhecido
- [ ] Um teste comprova que falha na leitura do uptime esconde a linha sem quebrar a janela

## Módulos afetados

- `sistema/inicializacao.py` — **novo, fora de `hardware/`**. Lê, escreve e remove a entrada
  da chave `Run` do `HKCU`; **resolve o caminho do executável em tempo de execução, cobrindo
  os dois modos** (desenvolvimento e empacotado); devolve falha em vez de levantar erro.
  **Fora de `hardware/` por decisão do `/spec-review`:** mexer no registro do Windows é
  integração com o sistema operacional, não coleta de hardware.
- `sistema/estado.py` — **novo**. Guarda em `%LOCALAPPDATA%` o pouco estado que o app
  precisa lembrar entre execuções. Nesta spec ele nasce vazio de conteúdo próprio (o
  interruptor é lido do registro), mas a spec 5 precisa dele para a mensagem de primeira
  vez — criar aqui evita que a spec 5 invente persistência por conta.
- `hardware/collector.py` — passa a expor o instante de boot da máquina (`psutil.boot_time()`).
- `ui/app.py` — ganha o interruptor "Abrir junto com o Windows" no cabeçalho, ao lado do botão
  de tema; ganha a linha de uptime no rodapé; ganha a linha de aviso quando a escrita falha.
- `main.py` — passa a aceitar abrir minimizado quando iniciado pela entrada do registro.
- `tests/sistema/test_inicializacao.py` — **novo**, com `winreg` mockado. Cobre os **dois**
  ramos de resolução de caminho: desenvolvimento e empacotado.
- `tests/sistema/test_estado.py` — **novo**.
- `tests/ui/test_app.py` — ganha os testes do interruptor e do rodapé.

## Não mexer

- **Bandeja e minimizar para a bandeja** — spec 5. Aqui, "minimizado" quer dizer na barra de
  tarefas. Fechar a janela continua encerrando o app até a spec 5 mudar isso.
- `recursos.py` (raiz), `hardware/processos.py` — spec 1.
- `hardware/discos.py` e a medição de disco — spec 2.
- `hardware/desempenho.py` e o aviso de calor — spec 3.
- Leitura da placa de vídeo — spec 6.
- Empacotamento em `.exe` — spec 7. Esta spec só precisa resolver o caminho em tempo de
  execução; o `.exe` ainda não existe.
- `ui/components/cards.py`, `ui/components/semaphore.py`.
- Textos de recurso e notificações — spec 1.
- Os limites de qualquer recurso.

## Decisões tomadas

- **Esta spec foi separada da bandeja** → o usuário preferiu dividir a spec 4 original em
  duas. Motivo que sustenta: a bandeja é a única parte do projeto com dependência nova **e**
  thread conversando com a interface; juntá-la com o registro e o rodapé — que fecham rápido e
  são testáveis com mock — prenderia os dois se a bandeja desse trabalho. O `aprovados.txt` já
  apontava nessa direção ao escrever "A11 primeiro, A13 depois". Total de specs foi de 6 para 7.
- **O interruptor não guarda estado próprio** → a entrada no registro é o estado. Decidido sem
  perguntar, por eliminar uma fonte de divergência: não há como o interruptor discordar da
  realidade, nem se a pessoa remover a entrada por fora.
- **Falha na escrita desmarca e explica** → escolha do usuário. É ação pedida pela pessoa, não
  leitura de hardware — falhar calado faria a caixa mentir, e só desmarcar pareceria defeito.
- **Uptime exato, com horas e minutos** → escolha do usuário. Alternativa registrada, se o
  rodapé incomodar: precisão variável (minutos na primeira hora, horas depois, dias depois),
  que é o que Windows e macOS fazem — o minuto vira ruído depois de algumas horas, e
  "há 73h 12min" é pior que "há 3 dias".
- **Uptime é da máquina, não do app** → é o que interessa a quem quer saber como a máquina se
  comportou; já registrado no `aprovados.txt`.
- Aplicadas sem perguntar, por já estarem no CLAUDE.md: subir minimizado sem roubar a tela;
  chave `Run` do `HKCU` sem admin; `pythonw.exe` e nunca caminho fixo da máquina do autor;
  interruptor reversível pela própria interface.

## Impacto no CLAUDE.md

- **Persistência de estado** → a seção diz que o estado do interruptor vai para
  `%LOCALAPPDATA%`; na verdade o interruptor **não tem estado próprio** (a entrada no
  registro é o estado). Corrigir a redação e citar o que de fato vai para `%LOCALAPPDATA%`:
  o `sistema/estado.py`, que a spec 5 usa para a mensagem de primeira vez.
- **Ciclo de vida da janela (a implementar na spec 4)** → deixa de ser "a implementar" na parte
  de abrir com o Windows e subir minimizado. A parte de fechar para a bandeja continua
  pendente, agora apontando para a spec 5.
- **Estrutura real do projeto** → acrescentar o pacote `sistema/` (`inicializacao.py`, `estado.py`) e
  `tests/sistema/`; atualizar a contagem de testes.
- **Melhorias — ver `aprovados.txt`** → a lista passa de 6 para 7 specs (a 4 foi dividida em
  registro/rodapé e bandeja); marcar a spec 4 como especificada.
- **UI/UX** → acrescentar o interruptor de inicialização e a linha de uptime como elementos da
  janela, junto do botão de tema.
- **Qualidade — dívidas conhecidas** → o construtor de `ui/app.py` ganha mais elementos;
  reavaliar o item das funções acima de 20 linhas ao fechar a spec.
