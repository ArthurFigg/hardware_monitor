# Aviso de redução de velocidade por calor

**Ordem:** 3 de 7
**Depende de:** 01-notificacoes-por-recurso (tipo `Recurso`), 02-medicao-de-disco (linha extra
do `CartaoRecurso`)
**Score:** 5
**Revisão:** aprovada

## O que faz

Corrige o limiar de Temperatura Atenção de 60°C para 65°C, e o cartão de Temperatura passa a
avisar quando o processador reduz a própria velocidade para não esquentar.

## Comportamento

### Correção do limiar de Temperatura Atenção

- O limiar de Atenção passa de 60°C para **65°C**. O de Alerta continua em 80°C.
- Motivo, já registrado no CLAUDE.md: a temperatura é derivada do percentual de CPU, então
  cada valor corresponde a um percentual exato. Com 60°C, o cartão de Temperatura acendia em
  CPU 50% — **antes** do cartão de CPU, que acende em 60%. Toda carga entre 50% e 59% mostrava
  amarelo na Temperatura com a CPU em verde. 65°C corresponde exatamente a CPU 60%.
- O Alerta **não** é alinhado de propósito: a CPU fica vermelha em 85% e a temperatura só em
  90%. Temperatura atrasada em relação à carga é fisicamente correto — calor demora a subir.
  O defeito era estar adiantada.
- Os testes de limite existentes em `test_thresholds.py` que usam 60°C são ajustados para 65°C.

### Leitura da velocidade real do processador

- O app passa a ler o contador de desempenho do Windows `% Processor Performance` — o mesmo
  que o Gerenciador de Tarefas usa. Sem dependência nova: `ctypes` e `winreg`, ambos da
  biblioteca padrão.
- A consulta é aberta **uma vez** e reaproveitada a cada ciclo. Nunca chamar programa externo
  a cada leitura.
- O nome do contador é resolvido pelo **número**, que é igual em qualquer idioma
  (`Processor Information` = 2610, `% Processor Performance` = 2660, obtidos da chave 009 do
  Perflib). Quando a tradução vier vazia, usar o nome em inglês.
- Valores acima de 100% são normais e significam turbo. Medido nesta máquina em 25/08/2026:
  105–117% em repouso, 121% sob carga.

### Quando o aviso aparece

- O aviso aparece quando **as duas condições acontecem juntas**: carga de CPU **em 85% ou
  mais** e velocidade do processador **abaixo de 90%**. Fronteiras inclusivas no limite
  inferior, como o resto do projeto (`>= 85`, `< 90`).
- As duas juntas são obrigatórias. O contador sozinho também cai com o PC ocioso, e nesse
  caso a queda é proposital (economia de energia) — acusar ali seria alarme falso.
- O aviso só é confirmado depois de **5 segundos contínuos** nessa condição. Uma queda de um
  segundo não faz a linha piscar na tela. É a mesma regra dos 5 segundos que o
  `RastreadorAlerta` já aplica aos alertas.
- Quando a condição deixa de valer, a linha some.

### Onde o aviso aparece

- O aviso é uma **linha extra no cartão de Temperatura**, abaixo da descrição, usando a linha
  opcional criada pela spec 2.
- Texto: "Seu processador diminuiu a velocidade para não esquentar."
- A descrição do cartão **não é substituída** — ela continua verdadeira, a temperatura está
  mesmo alta.
- O **status do cartão não muda** por causa da redução. Frear por calor não é defeito: é o
  processador se protegendo e conseguindo. É informação, não emergência, e não há ação a
  tomar. Um app que grita quando não há o que fazer vira app que se ignora.
- Não dispara notificação.

### Quando a leitura não funciona

- Quando o contador não existe (Windows mais antigo, contador desativado, erro na abertura da
  consulta), a linha simplesmente **não aparece** e o cartão de Temperatura continua
  funcionando normalmente.
- Quando o valor lido é negativo ou absurdo, é tratado como leitura indisponível — mesma saída.
- Nunca exibe mensagem de erro, nunca impede o cartão de mostrar a temperatura estimada.

## Critérios verificáveis

- [ ] `uv run pytest -v` passa, incluindo os testes das specs anteriores
- [ ] Um teste comprova que 65,0°C classifica em Atenção e 64,9°C em Normal
- [ ] Um teste comprova que o Alerta de temperatura continua em 80°C
- [ ] Um teste comprova que carga 90% com velocidade 95% **não** aciona o aviso (velocidade
      alta demais)
- [ ] Um teste comprova que carga 50% com velocidade 70% **não** aciona o aviso (carga baixa —
      é economia de energia, não calor)
- [ ] Um teste comprova que carga 90% com velocidade 85% aciona o aviso
- [ ] Um teste comprova que o aviso só é confirmado após 5 segundos contínuos na condição
- [ ] Um teste comprova que falha na leitura do contador esconde a linha e mantém o cartão
      exibindo a temperatura (com a leitura mockada levantando erro)
- [ ] Um teste comprova que o status do cartão de Temperatura não muda por causa do aviso

## Módulos afetados

- `hardware/pdh.py` — **novo**. O mecanismo PDH compartilhado: abre e mantém consulta,
  resolve nome de contador por número com queda para o inglês, e devolve indisponível em
  vez de levantar erro. **Dono definido no `/spec-review`:** esta spec cria; a spec 6
  **importa sem editar**. Antes, as duas se empurravam — esta declarava intocável o que
  aquela precisava estender.
- `hardware/desempenho.py` — **novo**. Usa `pdh.py` para ler `% Processor Performance` e
  aplica a regra de redução por calor.
- `hardware/thresholds.py` — `LIMITE_TEMP_ATENCAO` passa de 60,0 para 65,0; ganha a regra que
  decide o aviso de redução a partir de carga e velocidade, com a confirmação de 5 segundos.
- `hardware/collector.py` — `coletar()` passa a devolver também a velocidade do processador
  (ou indisponível).
- `ui/app.py` — o cartão de Temperatura passa a receber a linha extra quando o aviso está
  ativo.
- `tests/hardware/test_pdh.py` — **novo**. Cobre a resolução de nome por número, a queda
  para o inglês e a devolução de indisponível.
- `tests/hardware/test_desempenho.py` — **novo**, com `pdh.py` mockado.
- `tests/hardware/test_thresholds.py` — testes de 60°C ajustados para 65°C; ganha os testes da
  regra de redução.
- `tests/hardware/test_collector.py` — ajustado para o novo campo.

## Não mexer

- `ui/components/cards.py` — a linha extra opcional é criada pela **spec 2**. Esta spec só a
  usa.
- **Os textos** — são da spec 1. A frase do aviso está definida aqui apenas porque nasce
  nesta spec; se conflitar com a spec 1, a spec 1 manda.
- O limiar de **Alerta** de temperatura (80°C) e a fórmula de `estimar_temperatura()`.
- Os limites de CPU e RAM.
- Tudo de disco — spec 2.
- Leitura da placa de vídeo — spec 6, embora use o mesmo mecanismo PDH criado aqui.
- Inicialização com o Windows e rodapé — spec 4. Bandeja — spec 5.
- `ui/components/semaphore.py`, `main.py`, `notifications/manager.py`.
- `psutil.cpu_freq()` — **não serve** e não deve ser usado: devolve 3701 MHz fixo nesta
  máquina, parado ou sob carga, porque lê a frequência nominal do registro e não o clock real.
  Verificado em 25/08/2026.

## Decisões tomadas

- **Onde o aviso aparece** → linha extra no cartão, sem mudar cor nem substituir a descrição.
  O usuário escolheu a linha extra. Motivo que sustenta a escolha: frear por calor é o
  processador se protegendo com sucesso, não um defeito — e não há ação a tomar. Contrasta
  com a saúde do disco (spec 2), onde o status muda justamente porque a pessoa precisa agir.
- **Os números da regra** → carga acima de 85% e velocidade abaixo de 90%. O usuário propôs
  85% e 100%; o 85% foi mantido pelo motivo dele — reaproveitar o limite de alerta que já
  existe em vez de criar constante nova. O 100% foi corrigido: esse contador passa de 100%
  quando há turbo (medido: 121% sob carga nesta máquina), então "abaixo de 100%" nunca
  dispararia aqui; e num PC sem turbo, que fica perto de 100% o tempo todo, qualquer
  oscilação viraria alarme. 90% funciona nos dois casos.
- **O 90% é fundamentado, não medido** → não há como provocar superaquecimento real para
  conferir. É o primeiro candidato a ajuste se, no uso, o aviso nunca aparecer ou aparecer
  demais. Manter o número fácil de trocar.
- **Confirmação de 5 segundos** → aplicada por consistência com a regra que o projeto já tem
  para alertas, não como decisão nova. Evita a linha piscar numa queda de um segundo.
- Aplicadas sem perguntar, por já estarem em `_decisoes.md`: leitura que falha esconde a si
  mesma; contador do Windows resolvido por número com queda para o inglês.

## Impacto no CLAUDE.md

- **Thresholds (nunca alterar sem avisar)** → o bloco que explica a mudança de 60°C para 65°C
  como pendente ("A implementar na spec 3") passa a descrever o estado atual; o limiar no
  código e no documento passam a coincidir.
- **Estrutura real do projeto** → acrescentar `hardware/desempenho.py` e
  `tests/hardware/test_desempenho.py`; atualizar a contagem de testes.
- **Decisões arquiteturais importantes** → acrescentar: leitura do contador de desempenho do
  Windows por consulta PDH persistente, resolvida por número; a regra de carga alta com
  velocidade baixa; e a observação de que `psutil.cpu_freq()` não serve no Windows.
- **Melhorias — ver `aprovados.txt`** → marcar a spec 3 como especificada.
