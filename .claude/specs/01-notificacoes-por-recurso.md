# Notificações por recurso, com o programa nomeado

**Ordem:** 1 de 7
**Depende de:** nenhuma
**Score:** 5
**Revisão:** aprovada

## O que faz

Cada recurso passa a ter título e corpo próprios na notificação, e em CPU e RAM o corpo
nomeia o programa que está consumindo. O tipo `Recurso` passa a existir no código, reunindo
num lugar só o que hoje está espalhado em três dicionários paralelos.

## Comportamento

### Textos por recurso

- Quando um recurso entra em episódio de alerta, a notificação usa **título curto e corpo
  separados** — não a frase única de hoje. O título passa a dizer o que aconteceu, no lugar
  de "Monitor de Hardware".
- Quando o recurso é **CPU**: título "CPU em sobrecarga", corpo
  "{programa} está usando {N}% da CPU. Feche programas que não estiver usando."
- Quando o recurso é **RAM**: título "Memória em sobrecarga", corpo
  "{programa} está usando {N}% da memória. Feche programas que não estiver usando."
- Quando o recurso é **Disco** por falta de espaço: título "Espaço em disco acabando", corpo
  "Apague arquivos grandes ou mova para outro lugar." Sem nomear disco nem quantidade —
  isso é medição, e medição de disco é da spec 2.
- Quando o recurso é **Disco** por desgaste do hardware: título "Disco com sinais de
  desgaste", corpo "Faça uma cópia dos seus arquivos importantes." O conselho é **copiar**,
  nunca apagar nem fechar programas — o disco pode estar com 20% de uso e morrendo.
  Quem detecta o desgaste é a spec 2; esta spec só define o que dizer.
- Quando o recurso é **Temperatura**: título "Temperatura crítica", corpo
  "O processador está muito quente. Feche programas pesados e verifique a ventilação."

### Textos do cartão do Disco

O Disco deixa de herdar os textos de CPU/RAM, que dão conselho errado (fechar programa não
libera espaço em disco):

- Normal: "Espaço em disco suficiente. Não há risco no momento."
- Atenção: "Espaço em disco diminuindo. Vale apagar arquivos que você não usa mais."
- Alerta por falta de espaço: "Espaço em disco acabando. Apague arquivos grandes ou mova
  para outro lugar."
- Alerta por desgaste do hardware: "Disco com sinais de desgaste. Faça uma cópia dos seus
  arquivos importantes." — a spec 2 acrescenta o nome do disco a essa linha.

### Nomear o programa

- Quando CPU ou RAM entram em episódio de alerta, o app varre os processos **naquele
  momento** e nomeia o que mais consome. Fora do episódio de alerta, não varre.
- Quando vários processos têm o mesmo nome, seus valores são **somados** antes da comparação
  (o Chrome roda como ~20 processos; sem somar, nenhum passa de 4%).
- Quando o processo é `System Idle Process`, ele é **ignorado** — é o processo do tempo
  ocioso e aparece com valores acima de 1000%.
- Quando o valor de CPU de um processo passa de 100%, ele é normalizado pelo número de
  núcleos antes de virar texto — `cpu_percent` por processo soma todos os núcleos.
- Quando a varredura não consegue identificar nenhum programa (acesso negado a todos, ou
  nenhum acima de 1%), a notificação sai **sem a parte do programa**: só o título e a
  segunda frase do corpo. Nunca deixa lacuna vazia no texto nem deixa de notificar.
- Disco e Temperatura **não** varrem processos — não há programa associado a disco cheio
  nem à temperatura.

### O tipo Recurso

**Redesenhado no `/spec-review` de 25/08/2026.** A primeira versão tinha só nome, rótulo,
textos, formato e "se varre processos" — e as specs 2, 3 e 6 pediam quatro coisas que ela não
comportava. Como os quatro consumidores já estão escritos, o formato abaixo atende todos.

`Recurso` reúne, para cada recurso:

- **Nome interno e rótulo exibido** — `"cpu"` e "CPU"; `"placa_video"` e "Placa de vídeo".
- **Função de classificação própria.** Cada recurso aponta para a sua: CPU e RAM usam
  `classificar()`, Temperatura usa `classificar_temperatura()`, Disco usará
  `classificar_disco()` (spec 2) e a placa de vídeo `classificar_placa_video()` (spec 6).
  Sem isso, `app.py` precisaria de um desvio por recurso — que é exatamente o que esta spec
  existe para eliminar.
- **Textos de cartão por status, com variantes por causa.** O par status→texto não basta:
  o Disco em Alerta tem **duas** redações, uma por falta de espaço e outra por desgaste do
  hardware. O campo é indexado por status **e** por causa, com uma causa padrão para os
  recursos que só têm uma.
- **Título e corpo de notificação, com as mesmas variantes por causa** — pelo mesmo motivo.
- **Se o recurso notifica.** Marcador próprio, não inferido de texto vazio. A placa de vídeo
  (spec 6) nunca notifica porque nunca chega a Alerta, e isso precisa ser declarado, não
  deduzido.
- **Se o recurso varre processos.** Só CPU e RAM.
- **Formato do valor numérico**, podendo incluir rótulo antes do número — "74%", "~66°C",
  "C: — 91%" (spec 2). O Disco precisa nomear a unidade pior; o formato é da entrada, não
  de código específico em `app.py`.
- **Se o cartão pode sumir.** Recurso cuja leitura falhou desaparece da tela em vez de exibir
  erro. Vale para a placa de vídeo (spec 6) quando o contador não existe. A montagem dos
  cartões passa a ser **condicional**, não fixa.

Consequências:

- Os três dicionários paralelos de `app.py` (rastreadores, notificadores, cartões) passam a
  ser derivados dessa fonte única. Acrescentar um recurso passa a ser **uma entrada**, não
  três — e `app.py` deixa de conhecer recurso por nome.
- O **pior status entre os recursos** (que a spec 5 consome para colorir o ícone da bandeja)
  é calculado percorrendo esta coleção, **não** em `app.py` — o CLAUDE.md proíbe lógica de
  negócio ali. Recurso indisponível (cartão sumido) fica **fora** da conta do pior status.

### Notificação de temperatura junto com a de CPU

- Quando a carga sobe o suficiente, **as duas notificações disparam**: primeiro "CPU em
  sobrecarga" (CPU em 85%) e depois "Temperatura crítica" (CPU em 90%). Isso é esperado e
  foi decidido — ver "Decisões tomadas".
- Não há supressão de uma pela outra nesta spec.

### O que não muda

- A notificação continua disparando **só** em episódio de alerta, nunca em Atenção
  (regra do CLAUDE.md).
- Continua uma notificação por episódio: enquanto o recurso permanece em alerta, não repete.
- Os textos de cartão de CPU, RAM e Temperatura continuam exatamente como estão no CLAUDE.md.

## Critérios verificáveis

- [ ] `uv run pytest -v` passa, incluindo os 61 testes que já existiam
- [ ] Um teste para cada recurso comprova que a notificação sai com o título esperado
      (4 testes: CPU, RAM, Disco, Temperatura)
- [ ] Um teste comprova que o corpo de CPU contém o nome do programa dominante, com o
      `plyer` mockado
- [ ] Um teste comprova que processos de mesmo nome são somados antes da escolha do dominante
- [ ] Um teste comprova que `System Idle Process` nunca é escolhido como dominante
- [ ] Um teste comprova que valor de processo acima de 100% é normalizado antes de virar texto
- [ ] Um teste comprova que, sem programa identificável, a notificação ainda dispara e o
      corpo não contém lacuna vazia
- [ ] Um teste comprova que Disco e Temperatura não disparam varredura de processos
- [ ] Um teste comprova que o Disco tem **duas** variantes de Alerta (falta de espaço e
      desgaste) e que cada causa seleciona o texto certo
- [ ] Um teste comprova que um recurso marcado como "não notifica" não dispara notificação
      em nenhum status
- [ ] Um teste comprova que a montagem dos cartões é condicional: recurso indisponível não
      gera cartão e fica fora do cálculo do pior status
- [ ] Um teste comprova que cada recurso usa a própria função de classificação
- [ ] Um teste comprova que o cartão do Disco usa os textos próprios, não os de CPU/RAM
- [ ] A frase de alerta de CPU/RAM existe em **um** lugar do código — busca por
      "Sobrecarga de memória/processamento" não retorna duas definições fora de teste

## Módulos afetados

- `recursos.py` — **novo, na raiz do projeto** (não em `hardware/`). O tipo `Recurso`, a
  coleção dos quatro recursos e o cálculo do pior status entre eles.
  **Fica fora de `hardware/` por decisão do `/spec-review`:** ele carrega textos de
  interface, e o CLAUDE.md proíbe misturar lógica de hardware com lógica de UI. `Recurso`
  é entidade de domínio (ver `_dominio.md`) e é consumido pelas duas camadas — a raiz é o
  lugar que não mente sobre isso.
- `hardware/processos.py` — **novo**. Varredura sob demanda: soma por nome, exclui
  `System Idle Process`, normaliza acima de 100%, devolve o dominante ou nada.
- `hardware/thresholds.py` — os textos de cartão saem dos dicionários soltos e passam a vir
  de `Recurso`; ganha os textos do Disco. `classificar()` e o `RastreadorAlerta` não mudam.
- `notifications/manager.py` — `processar()` passa a receber o recurso e o programa
  dominante; título e corpo saem de `Recurso` em vez da constante fixa. A duplicação da
  frase com `thresholds.py` acaba.
- `ui/app.py` — os três dicionários paralelos passam a ser montados a partir de `Recurso`.
- `tests/test_recursos.py` — **novo**.
- `tests/hardware/test_processos.py` — **novo**, com `psutil` mockado.
- `tests/hardware/test_thresholds.py` — ganha os testes dos textos do Disco.
- `tests/notifications/test_manager.py` — ganha os testes de título e corpo por recurso.

## Não mexer

- `ui/components/semaphore.py` e `ui/components/cards.py` — a aparência não muda nesta spec.
- `main.py`.
- A coleta de disco (`disk_usage`) — quantos discos, quanto espaço livre e os limites do
  Disco são da **spec 2**. Esta spec só escreve o texto.
- Os limites de temperatura — a correção de 60°C para 65°C é da **spec 3**.
- Qualquer leitura via PDH (calor, placa de vídeo) — specs 3 e 6.
- Inicialização com o Windows e rodapé — spec 4. Bandeja — spec 5.
- O `RastreadorAlerta` e a regra dos 5 segundos.

## Decisões tomadas

- **Fronteira entre spec 1 e spec 2** → a spec 1 é dona de **tudo que o app diz** (textos de
  cartão e de notificação, de todos os recursos, Disco incluído); a spec 2 é dona de **tudo
  que o app mede no disco** (limites, múltiplos discos, saúde). Motivo do usuário: cada spec
  precisa de responsabilidade própria, e o corte anterior — por mecanismo — deixava a spec 1
  devendo à spec 2. Funciona porque o texto não depende do limite: "Espaço em disco acabando"
  é a frase certa seja o limite 60% ou 85%.
- **Formato da notificação** → título curto e corpo separados, não linha única. O aviso do
  Windows mostra o título em negrito e maior, e é a única parte lida de relance; hoje essa
  linha diz "Monitor de Hardware", que o ícone já informa.
- **Criar o tipo `Recurso` agora** → três dicionários paralelos já são frágeis, e as specs 3
  e 5 acrescentariam mais. O erro típico — acrescentar em dois lugares e esquecer o terceiro
  — não quebra teste, só some da tela. Fazer agora custa uma vez; fazer depois custa quatro.
  Os 61 testes existentes cobrem o comportamento que a troca não pode quebrar.
- **Temperatura e CPU notificam as duas** → escolha do usuário. Registrado o efeito: como a
  temperatura é derivada da CPU, não é "às vezes as duas" — toda carga que passa de 90% de
  CPU produz exatamente duas notificações, nessa ordem. A defesa da escolha é que, depois da
  spec 3, a temperatura ganha sinal próprio (redução de velocidade por calor) e deixa de ser
  reflexo da CPU; suprimir agora seria construir algo para desmontar depois.
- **Sem programa identificável** → notifica mesmo assim, sem a parte do programa. Não deixar
  de avisar por não saber quem causou.
- **Texto de desgaste de disco acrescentado durante a entrevista da spec 2** → a spec 2
  decidiu que desgaste leva o Disco a Alerta, e o texto de "falta de espaço" mandaria apagar
  arquivos para resolver defeito de hardware. Como todo texto é desta spec, o texto novo
  entrou aqui em vez de vazar para a spec 2. Feito antes de qualquer implementação, custo
  zero.
- **`Recurso` redesenhado no `/spec-review`** → a primeira versão não comportava o que as
  specs 2, 3 e 6 pediam: classificador próprio, variantes de texto por causa, marcador de
  "não notifica" e cartão que some. O usuário escolheu redesenhar agora em vez de deixar
  cada spec seguinte mexer em `app.py`, pelo critério dele: escolher o que impede
  retrabalho. Paga-se uma vez em vez de quatro — e é raro poder desenhar a abstração com
  todos os consumidores já escritos, em vez de adivinhar.
- Aplicadas sem perguntar, por já estarem em `_decisoes.md`: varredura sob demanda e não por
  ciclo; nomear quem consome sem acusar; notificação só em alerta.

## Impacto no CLAUDE.md

- **Textos da interface** → a seção "CPU / RAM (e Disco, até a spec 2 dar textos próprios a
  ele)" passa a ser só "CPU / RAM"; ganha bloco próprio do Disco com os três textos; ganha a
  tabela de títulos e corpos de notificação.
- **Estrutura real do projeto** → acrescentar `recursos.py` (raiz) e `hardware/processos.py`,
  mais os dois arquivos de teste novos; atualizar a contagem de testes.
- **Decisões arquiteturais importantes** → remover o "DEFEITO CONHECIDO, conserta na spec 1"
  sobre a notificação única, que deixa de existir; acrescentar a decisão do tipo `Recurso`
  como fonte única.
- **Melhorias — ver `aprovados.txt`** → marcar a spec 1 como especificada.
- **Qualidade — dívidas conhecidas** → o construtor de `ui/app.py` deve encolher com a troca
  dos três dicionários; reavaliar o item ao fechar a spec.
