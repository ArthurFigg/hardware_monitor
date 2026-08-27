# Cartão de uso da placa de vídeo

**Ordem:** 6 de 7
**Depende de:** 01-notificacoes-por-recurso (tipo `Recurso`), 03-reducao-de-velocidade-por-calor
(mecanismo de leitura PDH)
**Score:** 4
**Revisão:** aprovada

## O que faz

Um quinto cartão mostra o quanto a placa de vídeo está sendo usada — medição real, o mesmo
número que o Gerenciador de Tarefas exibe, não estimativa.

## Comportamento

### A leitura

- O app lê o contador `\GPU Engine(*)\Utilization Percentage` do Windows, pelo mesmo mecanismo
  PDH que a spec 3 cria.
- O contador lista **muitos motores** (medido nesta máquina: 312), separados por processo e
  por tipo — 3D, cópia, decodificação e codificação de vídeo. Somar todos daria número acima
  de 100% sem sentido.
- O valor exibido é o **maior valor entre os tipos de motor**, que é o que o Gerenciador de
  Tarefas mostra — e portanto o número que a pessoa reconhece.
- Medido nesta máquina em repouso: 0,3% a 0,5%.

### Três armadilhas já verificadas, que a implementação precisa tratar

- **Este contador não é traduzido.** Ao contrário do de processador, ele fica em inglês mesmo
  num Windows em português: a busca por número devolve string vazia (os índices 5802 e 5806
  existem na chave 009, mas não há nome local). Regra: tentar o número e cair para o nome em
  inglês quando vier vazio — que é a regra geral do projeto, e aqui ela é obrigatória, não
  precaução.
- **A função que lê o vetor de valores devolve o código como número negativo** no `ctypes`.
  Comparar com `(rc & 0xFFFFFFFF)`, senão o código de "há mais dados" nunca casa e a leitura
  parece vazia mesmo funcionando.
- **O contador precisa de duas coletas** antes do primeiro valor válido, como todo contador
  de taxa.

### O semáforo

- Atenção quando o uso fica **acima de 95%** (`> 95`), sustentado por 5 segundos.
  **CORRIGIDO no `/spec-review`:** eu havia escrito "a mesma regra que o projeto já usa",
  mas os 5 segundos do `RastreadorAlerta` valem **só para Alerta** — não existe confirmação
  temporal de Atenção em nenhum recurso, e `classificar_placa_video()` não tem onde guardar
  esse estado. Esta spec **generaliza o `RastreadorAlerta`** para confirmar qualquer status
  após N segundos sustentados, preservando o comportamento atual para Alerta.
- **Nunca vai para Alerta.** Placa de vídeo no limite não é emergência e não tem ação urgente.
- Abaixo de 95%, Normal.
- Motivo dos limites, e é o ponto central desta spec: placa em 100% durante um jogo é o
  esperado — é para estar assim. Usar os 60% e 85% de CPU e RAM deixaria o cartão amarelo o
  jogo inteiro e vermelho sem que nada estivesse errado. O único caso em que o número
  significa algo para este público é a placa **no limite de forma sustentada**, que explica o
  jogo engasgando e tem ação clara: baixar a qualidade gráfica.

### Efeito no ícone da bandeja

- A placa **entra** no cálculo do pior status que colore o ícone da bandeja (spec 5). Como
  ela só chega a Atenção acima de 95% sustentado, o ícone fica amarelo durante um jogo
  pesado. Isso é coerente com o cartão, que também fica amarelo — e nunca vermelho, porque
  a placa nunca chega a Alerta.

### Quando não há placa dedicada

- O cartão **aparece do mesmo jeito**. O contador responde com a placa integrada, e o número é
  informação verdadeira — só que quase sempre baixo, então o cartão fica verde e discreto.
- O app **não tenta distinguir** placa integrada de dedicada: exigiria complicação para pouco
  ganho.

### Quando a leitura não funciona

- Quando o contador não existe (Windows mais antigo, contadores de GPU não registrados), o
  **cartão inteiro não aparece**. Os outros quatro continuam funcionando normalmente.
- Isso não contradiz "o cartão aparece mesmo sem placa dedicada": lá o contador responde e há
  número para mostrar; aqui não há leitura nenhuma.
- Nunca exibe erro, nunca impede o app de abrir.

### O que não muda

- A placa de vídeo **não dispara notificação** — ela nunca chega a Alerta, e notificação só
  existe em Alerta.
- Não varre processos: o cartão diz quanto a placa está sendo usada, não por quem.
- **Temperatura da placa continua fora do projeto** — exigiria programa do fabricante.

## Critérios verificáveis

- [ ] `uv run pytest -v` passa, incluindo os testes das specs anteriores
- [ ] Um teste comprova que o valor exibido é o maior entre os tipos de motor, não a soma
      (com um vetor de leituras simulado)
- [ ] Um teste comprova que a busca por número, ao devolver vazio, cai para o nome em inglês
- [ ] Um teste comprova que o código negativo do `ctypes` é comparado com máscara e a leitura
      não é descartada
- [ ] Um teste comprova que 96% sustentado por 5 segundos classifica em Atenção
- [ ] Um teste comprova que 96% por menos de 5 segundos ainda é Normal
- [ ] Um teste comprova que a placa de vídeo **nunca** classifica em Alerta, mesmo em 100%
- [ ] Um teste comprova que, com o contador indisponível (leitura mockada levantando erro), o
      cartão não aparece e os outros quatro continuam
- [ ] Um teste comprova que a placa de vídeo não dispara notificação em nenhum valor

## Módulos afetados

- `hardware/placa_video.py` — **novo**. Abre a consulta PDH do contador de placa de vídeo,
  resolve o nome com queda para o inglês, agrega pelo maior tipo de motor, trata o código
  negativo, e devolve indisponível em vez de levantar erro.
- `hardware/thresholds.py` — ganha `classificar_placa_video()` (Atenção acima de 95%, nunca
  Alerta) e **generaliza o `RastreadorAlerta`** para confirmar qualquer status após N
  segundos, mantendo o comportamento atual de Alerta intacto.
- `hardware/pdh.py` — **importado sem editar**. Criado pela spec 3.
- `hardware/collector.py` — `coletar()` passa a devolver também o uso da placa (ou
  indisponível).
- `recursos.py` (raiz) — ganha **uma entrada** para a placa de vídeo: rótulo "Placa de
  vídeo", classificador `classificar_placa_video()`, formato "23%", não varre processos,
  **não notifica**, cartão pode sumir. Todos esses campos existem no `Recurso` redesenhado
  pela spec 1.
  Textos do cartão (definidos aqui porque nascem nesta spec; a spec 1 é a dona da regra de
  tom): Normal — "Placa de vídeo tranquila. Há folga para jogos e vídeos.";
  Atenção — "Placa de vídeo no limite. Se um jogo estiver engasgando, diminua a qualidade
  gráfica." Não há texto de Alerta porque a placa nunca chega lá.
- `tests/hardware/test_placa_video.py` — **novo**, com a leitura PDH mockada.
- `tests/hardware/test_thresholds.py` — ganha os testes de `classificar_placa_video()`.
- `tests/hardware/test_collector.py` — ajustado para o novo campo.

## Não mexer

- `ui/app.py` — **não precisa mudar**. A spec 1 fez os cartões serem derivados de `Recurso`,
  então acrescentar um recurso é uma entrada, não três. Se esta spec precisar mexer em
  `app.py`, é sinal de que a refatoração da spec 1 não ficou completa.
- `ui/components/cards.py` e `semaphore.py`.
- `hardware/desempenho.py` — a spec 3 é dona. Esta spec não o toca.
- `hardware/pdh.py` — **importar, nunca editar**. A spec 3 cria o mecanismo compartilhado
  justamente para esta spec consumir sem extrair nada de lá.
- `notifications/manager.py` — a placa não notifica.
- Disco (spec 2), registro e rodapé (spec 4), bandeja (spec 5).
- Empacotamento em `.exe` — spec 7.
- `psutil` para placa de vídeo — **não existe**. Verificado em 25/08/2026: nenhuma função.

## Decisões tomadas

- **O valor é o maior entre os tipos de motor** → decidido sem perguntar, por ser questão de
  acerto e não de preferência: somar os 312 motores daria número acima de 100% sem sentido, e
  o maior por tipo é o que o Gerenciador de Tarefas mostra — o número que a pessoa reconhece.
- **Atenção acima de 95%, nunca Alerta** → o usuário não tinha base para escolher e delegou.
  O raciocínio, que vale registrar porque decorre de uma regra dele: pela regra "informação
  que não vira semáforo não vira cartão", a placa quase não mereceria cartão — valor alto
  significa "você está jogando", não "algo está errado". O que salva é o caso da placa **no
  limite sustentado**, que explica o jogo engasgando e tem ação clara (baixar a qualidade
  gráfica). Por isso existe cor, mas rara e nunca vermelha.
- **Descartado o cartão sem semáforo** → seria justamente o que a triagem passou o dia
  cortando. Se a placa não tivesse nenhuma cor com significado, o certo seria não ter o cartão.
- **Cartão aparece mesmo sem placa dedicada** → escolha do usuário. Distinguir integrada de
  dedicada seria complicação para pouco ganho, e com o limite em 95% a integrada fica verde e
  discreta.
- Aplicadas sem perguntar, por já estarem em `_decisoes.md`: contador resolvido por número com
  queda para o inglês; leitura que falha esconde a si mesma.

## Impacto no CLAUDE.md

- **UI/UX** → a tela passa a ter 5 cartões; a frase sobre valor numérico passa a incluir a
  placa de vídeo em percentual.
- **Thresholds (nunca alterar sem avisar)** → acrescentar os limites da placa de vídeo:
  Atenção acima de 95% sustentado, nunca Alerta — com o motivo, para ninguém "corrigir" para
  60/85 depois.
- **Estrutura real do projeto** → acrescentar `hardware/placa_video.py` e
  `tests/hardware/test_placa_video.py`; atualizar a contagem de testes.
- **Decisões arquiteturais importantes** → acrescentar as três armadilhas verificadas do
  contador de placa de vídeo (não é traduzido; código negativo no `ctypes`; precisa de duas
  coletas) e a agregação pelo maior tipo de motor.
- **Melhorias — ver `aprovados.txt`** → marcar a spec 6 como especificada.


---
**Status:** concluida em 2026-08-26
