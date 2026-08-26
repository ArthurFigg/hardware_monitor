# O que o app mede no disco

**Ordem:** 2 de 7
**Depende de:** 01-notificacoes-por-recurso (usa os textos e o tipo `Recurso` definidos lá)
**Score:** 5
**Revisão:** pendente

## O que faz

O Disco passa a olhar todas as unidades fixas da máquina, classificar pelo pior entre
percentual ocupado e espaço livre, e avisar quando um disco físico dá sinais de desgaste.

## Comportamento

### Quais unidades entram na conta

- Quando a máquina tem várias unidades fixas (C:, D:, ...), **todas** entram na conta.
  Hoje só a raiz é olhada.
- Quando a unidade é removível (pendrive), de rede ou de CD/DVD, ela **fica de fora**.
- Quando a unidade tem menos de 10 GB de tamanho total, ela **fica de fora**. Isso exclui a
  partição de recuperação do Windows, que tem ~500 MB e vive praticamente cheia — sem esse
  filtro o app abriria em Alerta permanente apontando para algo sobre o que não há nada
  a fazer.
- Quando uma unidade some com o app aberto (pendrive retirado, disco desconectado), ela sai
  da conta na leitura seguinte, sem erro e sem travar a coleta.
- Quando nenhuma unidade sobra depois dos filtros, o cartão do Disco exibe o estado Normal
  e nenhum número. Não quebra.

### Como o status é decidido

- O status do Disco é o **pior** entre todas as unidades que passaram no filtro. Uma unidade
  em Alerta leva o cartão a Alerta, mesmo que as outras estejam em Normal.
- Cada unidade é classificada pelo **pior dos dois critérios**, o que acontecer primeiro:
  - por percentual ocupado: Atenção em 85%, Alerta em 95%
  - por espaço livre: Atenção abaixo de 20 GB, Alerta abaixo de 10 GB
- Exemplo do porquê da regra dupla, com os discos desta máquina: 95% de um SSD de 120 GB
  deixa 6 GB livres — o Windows já não instala uma atualização com isso, então o percentual
  sozinho avisaria tarde demais. 95% de um SSD de 1 TB deixa 50 GB, que é folga: o
  percentual sozinho avisaria cedo demais e viraria alarme falso.
- Quando o cartão exibe o valor numérico, ele mostra o da unidade **pior** — a mesma que
  decidiu o status — e diz qual é (ex: "C: — 91%").

### Saúde do disco

- Quando o app inicia, ele consulta a saúde dos discos físicos uma vez.
- Depois disso, reconsulta **a cada 6 horas**. Desgaste evolui em semanas, então reler mais
  vezes não antecipa nada; e o app passa a viver na bandeja por semanas sem reiniciar
  (spec 4), então "só na inicialização" viraria "uma vez por mês".
- Quando **todos** os discos estão saudáveis, nada aparece. Silêncio é o estado normal.
- Quando **algum** disco não está saudável, o cartão do Disco vai para **Alerta** e exibe a
  linha de desgaste com o nome do disco (ex: "O disco CT120BX500SSD1 está dando sinais de
  desgaste."). Disco morrendo é mais grave que disco cheio, e não é estado passageiro como
  carga alta.
- Quando há desgaste **e** falta de espaço ao mesmo tempo, o desgaste manda: é o problema
  que a pessoa não resolve apagando arquivo.
- Quando a consulta de saúde falha (Windows mais antigo, comando ausente, permissão negada),
  a linha de desgaste **some** e o cartão continua funcionando normalmente pelo espaço
  livre. Nunca exibe erro, nunca deixa de mostrar o espaço.
- A saúde é do **disco físico**; o cartão mostra **unidades**. Esta spec não tenta mapear um
  no outro — um disco pode ter várias partições, e o mapeamento erra. A linha nomeia o disco.

### Acréscimo ao texto da notificação de espaço

- A spec 1 deixou a notificação de falta de espaço sem nomear disco nem quantidade. Como esta
  spec passa a conhecer os dois, o corpo pode citá-los (ex: "Restam 4,2 GB na unidade C:").
  Isso é acréscimo à frase da spec 1, não substituição — o texto dela continua correto sem.

## Critérios verificáveis

- [ ] `uv run pytest -v` passa, incluindo os testes das specs anteriores
- [ ] Um teste comprova que unidade removível, de rede e de CD/DVD ficam de fora
- [ ] Um teste comprova que unidade menor que 10 GB fica de fora (caso da partição de
      recuperação)
- [ ] Um teste comprova que o status do Disco é o pior entre as unidades
- [ ] Um teste comprova que 95% ocupado classifica em Alerta mesmo com muito espaço livre
- [ ] Um teste comprova que menos de 10 GB livres classifica em Alerta mesmo com percentual
      baixo (disco grande pouco usado mas quase cheio em GB)
- [ ] Um teste comprova que disco não saudável leva o cartão a Alerta
- [ ] Um teste comprova que desgaste tem precedência sobre falta de espaço
- [ ] Um teste comprova que falha na consulta de saúde esconde a linha e mantém o cartão
      funcionando pelo espaço (com o comando mockado levantando erro)
- [ ] Um teste comprova que, sem nenhuma unidade após os filtros, o cartão fica em Normal
      sem quebrar
- [ ] Um teste comprova que a linha extra do `CartaoRecurso` não aparece quando vazia — os
      cartões de CPU, RAM e Temperatura ficam idênticos aos de hoje

## Módulos afetados

- `hardware/discos.py` — **novo**. Lista as unidades fixas, aplica os filtros (removível,
  rede, menor que 10 GB), lê uso de cada uma, e consulta a saúde dos discos físicos com
  cache de 6 horas.
- `hardware/thresholds.py` — ganha `classificar_disco()` com a regra dupla (percentual e
  espaço livre) e a precedência do desgaste. `classificar()` de CPU/RAM não muda.
- `hardware/collector.py` — `coletar()` passa a devolver a lista de unidades e o estado de
  saúde, em vez do percentual único de `disk_usage("/")`.
- `ui/components/cards.py` — `CartaoRecurso` ganha uma **linha extra opcional**, abaixo da
  descrição, vazia por padrão. Quando vazia, o cartão fica idêntico ao de hoje. Esta spec é
  dona dessa mudança porque vem antes; a spec 3 reusa a mesma linha para o aviso de redução
  de velocidade por calor.
- `ui/app.py` — o cartão do Disco passa a exibir a unidade pior e, quando houver, a linha
  de desgaste.
- `tests/ui/test_cards.py` — ganha os testes da linha extra: ausente por padrão, exibida
  quando preenchida.
- `tests/hardware/test_discos.py` — **novo**, com `psutil` e a consulta de saúde mockados.
- `tests/hardware/test_thresholds.py` — ganha os testes de `classificar_disco()`.
- `tests/hardware/test_collector.py` — ajustado para o novo formato de retorno.

## Não mexer

- **Todos os textos** — são da spec 1, inclusive o de desgaste. Esta spec detecta o estado;
  a spec 1 diz o que se fala sobre ele.
- `hardware/recursos.py` e `hardware/processos.py` — criados pela spec 1.
- `notifications/manager.py` — a spec 1 já resolveu a notificação por recurso.
- Os limites de CPU, RAM e Temperatura — a correção de temperatura é da spec 3.
- Qualquer leitura via PDH (calor, placa de vídeo) — specs 3 e 6.
- Inicialização com o Windows e rodapé — spec 4. Bandeja — spec 5.
- `ui/components/semaphore.py` e `main.py`.
- Em `ui/components/cards.py`, mexer **só** na linha extra opcional. Semáforo, valor
  numérico e descrição ficam como estão.
- `wmic` — removido do Windows 11 recente. Usar `Get-PhysicalDisk` ou
  `Get-CimInstance Win32_DiskDrive`, ambos verificados sem admin nesta máquina.

## Decisões tomadas

- **Limite por percentual ou por espaço livre** → o pior dos dois, o que acontecer primeiro.
  O usuário escolheu percentual no primeiro momento; ao ver a conta — 95% de 120 GB deixa
  6 GB, e o Windows já não atualiza com isso, enquanto 95% de 1 TB deixa 50 GB de folga —
  mudou para a regra dupla. Percentual puro avisa tarde no disco pequeno e cedo no grande.
- **Quais unidades monitorar** → todas as fixas, ignorando as menores que 10 GB. O usuário
  escolheu "todas as fixas" no primeiro momento; a partição de recuperação do Windows (~500 MB,
  sempre quase cheia) faria o app abrir em Alerta permanente, e o filtro de tamanho resolve.
- **Desgaste muda o semáforo** → sim, vai direto para Alerta. Disco morrendo é a única coisa
  no app onde a pessoa precisa agir hoje, e não é estado passageiro como carga alta.
- **Frequência da consulta de saúde** → a cada 6 horas, escolha delegada. Desgaste evolui em
  semanas, então reler mais não antecipa nada; 6 horas custa 4 consultas por dia e pega o
  problema dentro do mesmo dia de trabalho.
- **Saúde não é mapeada em unidade** → a saúde é do disco físico e o cartão mostra unidades;
  um disco com várias partições faria o mapeamento errar. A linha nomeia o disco.
- **Texto de desgaste ficou na spec 1** → detectado durante esta entrevista que o texto de
  falta de espaço ("apague arquivos") mandaria apagar arquivo para resolver defeito de
  hardware. Como todo texto é da spec 1 e ela ainda não foi implementada, o texto novo foi
  acrescentado lá, mantendo a fronteira.
- **A linha extra do cartão nasce aqui** → detectado durante a entrevista da spec 3: as duas
  specs precisam de uma linha a mais no `CartaoRecurso` (desgaste do disco aqui, redução de
  velocidade por calor lá), e nenhuma das duas podia criá-la — esta listava `cards.py` como
  intocável. Como esta vem antes, ela passa a ser dona da mudança; a spec 3 reusa. Score
  subiu de 4 para 5.
- Aplicadas sem perguntar, por já estarem em `_decisoes.md`: leitura que falha esconde a si
  mesma; nada gravado na pasta do app.

## Impacto no CLAUDE.md

- **Thresholds (nunca alterar sem avisar)** → o parágrafo "Disco (a mudar na spec 2)" sai e
  vira a regra definitiva: Atenção em 85% ou abaixo de 20 GB livres; Alerta em 95% ou abaixo
  de 10 GB livres; desgaste vai direto para Alerta.
- **Estrutura real do projeto** → acrescentar `hardware/discos.py` e
  `tests/hardware/test_discos.py`; atualizar a contagem de testes.
- **Decisões arquiteturais importantes** → acrescentar: o status do Disco é o pior entre as
  unidades fixas; unidades menores que 10 GB ficam de fora; saúde relida a cada 6 horas e
  nunca mapeada em unidade.
- **Melhorias — ver `aprovados.txt`** → marcar a spec 2 como especificada.
