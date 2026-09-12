# Histórico persistente

**Ordem:** 1 de 3
**Depende de:** nenhuma
**Score:** 5
**Revisão:** aprovada

## O que faz
Grava em disco, sem nada aparecer na tela, uma amostra por minuto de cada recurso, cada
episódio de alerta à parte, e as lacunas em que o PC esteve ligado sem o app rodando, para
a leitura da spec 09a ter o que ler.

## Comportamento

### Amostra por minuto
- Quando a coleta entrega uma leitura, o gravador acumula os valores do minuto em curso.
- Quando o minuto vira, grava a média do minuto: uma linha para CPU, uma para RAM, uma
  para a placa de vídeo, e **uma para cada unidade fixa de disco**.
- Cada linha guarda o recurso, o instante do minuto e o valor médio. A linha de disco
  guarda também **a unidade e os GB livres**, além do percentual: o alerta de espaço do
  projeto decide pelos dois critérios, e só o percentual não permitiria à 09a dizer quanto
  resta.
- **Quem é gravado sai de `recursos.py`, nunca de uma lista de nomes aqui.** `Recurso`
  ganha o campo `grava_historico`, verdadeiro por padrão e falso na Temperatura. Sem o
  campo, a única forma de pular a Temperatura seria comparar o nome do recurso — o oposto
  da decisão transversal "um lugar só descreve cada recurso".
- A **temperatura não é gravada**. Ela é o percentual de CPU convertido por
  `estimar_temperatura()`, e o `_dominio.md` já a classifica como leitura derivada —
  guardá-la é guardar o mesmo número duas vezes. Quem precisar dela recalcula.
- O status também não é gravado. Os limites são fixos e o status se recalcula a partir do
  valor; gravá-lo congelaria em disco uma decisão que pode mudar.
- Recurso indisponível no minuto (placa de vídeo que não responde, unidade que sumiu) não
  gera linha. Ausência de linha é a forma de dizer "não sei", e não vira zero.
- Quando o app é encerrado no meio de um minuto, a média parcial é **descartada**. Uma
  média de 12 segundos rotulada como "o minuto" mentiria sobre o período que representa.

### Episódio de alerta
- Quando o `RastreadorAlerta` confirma um alerta, grava o episódio **já no início**:
  recurso, instante de início, valor de pico até ali, e o programa que a varredura sob
  demanda devolveu. Sem instante de fim.
- Enquanto o episódio segue aberto, o valor de pico é atualizado quando superado.
- Quando o recurso sai do alerta, o instante de fim é escrito na mesma linha.
- **A varredura de processos não roda por causa do histórico.** O nome do programa é o que
  a varredura do alerta já produziu; se não houve nome, o episódio fica sem programa.
- Quando o app é encerrado no meio de um episódio, a linha fica sem instante de fim. **Um
  episódio sem fim é válido** e a spec 09a o trata como encerrado no último minuto que tem
  amostra.

### Lacuna: PC ligado sem o app
- O tempo contado pelo resumo é de **PC ligado, não de app aberto** (decisão de
  05/09/2026). O app só mede enquanto roda, então o tempo em que ele esteve fechado
  precisa ficar registrado como tal — senão o período de 10 horas vira "10 horas de app
  aberto" e a decisão não se cumpre.
- Ao abrir, o gravador grava uma **lacuna**: de quando até quando o PC esteve ligado sem o
  app. O começo é o mais recente entre o último minuto com amostra e o instante do boot; o
  fim é agora.
- **Boot mais recente que o último minuto gravado significa que o PC foi desligado no
  meio.** A lacuna então começa no boot, e o tempo de PC desligado não entra em nada — ele
  não existiu para ninguém.
- **Lacuna não tem valores.** Ela diz quanto tempo passou, nunca quanto a máquina
  consumiu. Inventar valor para minuto não medido é o mesmo erro que transformar recurso
  indisponível em zero.
- Lacuna menor que um minuto não é gravada — é a reabertura imediata do app, e uma linha
  por clique encheria o banco sem dizer nada.
- O instante do boot vem de `hardware/collector.py`, que já o expõe para a linha de uptime
  do rodapé. Esta spec lê sem editar.

### Retenção e falhas
- Ao abrir, apaga amostras, episódios e lacunas com mais de 90 dias.
- Quando o banco não pode ser aberto, criado ou escrito (pasta sem permissão, disco cheio,
  arquivo corrompido), o app **segue funcionando sem gravar**, não mostra erro e não
  registra nada na tela. É a regra de leitura que falha esconde a si mesma, aplicada à
  escrita.
- Se o relógio do sistema andar para trás, as linhas ficam fora de ordem cronológica. As
  consultas ordenam por instante, e amostra com instante repetido não substitui a anterior.

## Critérios verificáveis
- [ ] `uv run pytest -v` passa, e os 392 testes que já existiam continuam passando.
- [ ] Com o relógio simulado, alimentar o gravador com leituras de 60 segundos e verificar
      que sai **uma** linha por recurso, com a média dos valores entregues.
- [ ] Uma máquina simulada com duas unidades fixas produz duas linhas de disco por minuto,
      identificadas pela unidade.
- [ ] A linha de disco traz os GB livres além do percentual.
- [ ] Nenhuma linha de temperatura é gravada, mesmo com a leitura de temperatura presente.
- [ ] Um recurso simulado com `grava_historico` falso não gera linha, e o mesmo recurso com
      o campo verdadeiro gera — sem que nenhum nome de recurso apareça no gravador.
- [ ] Com o último minuto gravado há 3 horas e o boot há 5, abrir registra uma lacuna de 3
      horas; com o boot há 1 hora, a lacuna é de 1 hora.
- [ ] A lacuna registrada não produz valor de recurso nenhum.
- [ ] Reabrir o app segundos depois de fechar não grava lacuna.
- [ ] Confirmar um alerta grava o episódio sem instante de fim; sair do alerta preenche o
      fim na mesma linha, sem criar uma segunda.
- [ ] Um episódio aberto que nunca é fechado continua legível e não impede a gravação dos
      seguintes.
- [ ] Com o caminho do banco apontando para um lugar impossível de escrever, o gravador não
      levanta erro e as chamadas seguintes continuam sendo aceitas.
- [ ] Amostra com mais de 90 dias é apagada na abertura; amostra de 89 dias permanece.
- [ ] Nenhum teste toca o disco real do projeto — o banco vive em pasta temporária de teste.

## Módulos afetados
- `historico/__init__.py` — **novo**. Só re-exportações.
- `historico/banco.py` — **novo**. Abre o SQLite em `%LOCALAPPDATA%`, cria as tabelas na
  primeira execução, aplica a retenção, e devolve indisponível em vez de levantar erro.
  **Todo SQL do projeto mora aqui**, inclusive a leitura por janela de tempo (amostras,
  episódios e lacunas) que a spec 09a consome sem editar — é a superfície que impede
  consulta de regra de negócio abrir banco por conta, como o CLAUDE.md proíbe.
- `historico/gravacao.py` — **novo**. Acumula o minuto em curso, fecha a média na virada,
  abre e fecha episódios de alerta, e registra a lacuna na abertura.
- `recursos.py` — ganha o campo `grava_historico` em `Recurso` (verdadeiro por padrão,
  falso na Temperatura). É uma entrada a mais na descrição do recurso, não uma lista nova.
- `ui/app.py` — **a costura, e só ela**: o laço de coleta entrega cada leitura e cada
  status confirmado a um gravador recebido de fora, nulo por padrão. Sem isso a spec é
  impossível — a leitura, a confirmação do alerta e o nome do programa só existem dentro
  deste módulo, e o `main.py` não os vê.
- `main.py` — cria o gravador, entrega à janela junto com a thread de coleta e o fecha na
  saída limpa. **Não** no construtor da janela: é a mesma regra que a v2.1.0 aplicou ao
  ícone da bandeja e à própria coleta.
- `tests/historico/__init__.py` — **novo**, junto com a pasta `tests/historico/`.
- `tests/historico/test_banco.py` — **novo**. Banco em pasta temporária.
- `tests/historico/test_gravacao.py` — **novo**. Relógio e leituras simulados.
- `tests/ui/test_app.py`, `tests/test_recursos.py` — ganham o teste da costura e o do campo
  novo.

## Não mexer
- `ui/` — exceto a costura em `ui/app.py` descrita acima. Esta spec não tem efeito visível
  na tela: nenhum cartão, nenhuma linha, nenhum botão.
- `notifications/manager.py`, `ui/bandeja.py` — a notificação de resumo é da spec 09b.
- `hardware/thresholds.py` e todos os módulos de leitura em `hardware/` — a gravação
  consome o que a coleta já produz e não muda como nada é medido nem classificado. O
  instante do boot, usado pela lacuna, é lido de `hardware/collector.py` sem editar.
- `sistema/estado.py` — o histórico tem arquivo próprio; não entra no `estado.json`.
- `pyproject.toml` — `sqlite3` é da biblioteca padrão. Nenhuma dependência nova.

## Decisões tomadas
- Uma spec ou duas (gravar e mostrar juntos)? → **Duas.** A primeira grava e não mostra
  nada; a segunda lê. Juntas, o score passa do limite da skill.
- Como o resumo sabe quantas vezes ficou pesado — episódio guardado à parte ou derivado das
  amostras? → **Guardado à parte.** Motivo do usuário: na média de minuto o episódio some.
  Confirmado com números: um alerta é confirmado com 5 segundos acima do limite, e 10
  segundos a 90% diluídos em 50 segundos a 20% dão uma média perto de 32% — longe do limite
  de 85%. A média de minuto é boa para "como estava a máquina no geral" e cega para "o que
  aconteceu de ruim".
- O disco é gravado como? → **Todas as unidades fixas, uma linha cada.** Só a pior unidade
  não permitiria dizer quanto cada uma encheu no período, porque a pior troca de unidade no
  meio. Custo: dobra o arquivo numa máquina de duas unidades — 10 MB em 90 dias, aceito.
- Episódio cortado pelo encerramento do app? → **Grava já no início e fecha depois.** Só
  gravar no fim perderia justamente o episódio mais grave, o que estava acontecendo quando a
  máquina travou.
- A temperatura é gravada? → **Não**, é derivada do percentual de CPU.
- O tempo contado é de PC ligado ou de app aberto? → **PC ligado**, escolha do usuário
  reafirmada em 12/09/2026 no `/spec-review`. Por isso a lacuna existe: sem ela o app só
  saberia falar de tempo de app aberto, e a decisão ficaria escrita sem ser cumprida.
- Por onde o gravador recebe os dados, já que o laço de coleta mora em `ui/app.py`? →
  **Costura mínima em `ui/app.py`**, com o gravador criado no `main.py` e entregue pronto.
  A alternativa era extrair o laço para fora de `ui/`, que é a arquitetura correta mas é
  refatoração sem entrega visível e mexeria nos 82 testes de `test_app.py`. Decidido pelo
  assistente a pedido do usuário em 12/09/2026.
- Como o gravador sabe o que não gravar? → **Campo `grava_historico` em `Recurso`.** A spec
  nascera proibindo mexer em `recursos.py`, o que obrigaria a comparar nome de recurso —
  exatamente o que o projeto decidiu não fazer em lugar nenhum.
- A temperatura de GPU entra junto? → **Não.** Sondado nesta máquina em 05/09/2026: a placa
  é AMD RDNA3, o caminho barato (`atiadlxx.dll`) recusa a leitura e o caminho que suporta
  (ADLX) é vtable estilo COM, cujo erro derruba o processo em vez de levantar exceção — o
  oposto da regra de falhar escondendo. Detalhe completo no `D2` do `ideias.txt`.
- Onde a pessoa fica sabendo que o app grava nome de programa? → **README apenas.** Custo
  aceito: quem recebe o `.exe` de um amigo e nunca abre o GitHub não lê. Mitigado por a
  tela do resumo exibir nomes de programa, o que torna o fato evidente para quem usa.

## Impacto no CLAUDE.md
- **Persistência de estado** → deixa de ser verdade que o único arquivo gravado é o
  `estado.json`; acrescentar o banco do histórico em `%LOCALAPPDATA%`, com a retenção de 90
  dias e a nota de que ele guarda nome de programa nos episódios.
- **Estrutura real do projeto** → acrescentar o pacote `historico/` (`banco.py`,
  `gravacao.py`) e `tests/historico/`.
- **Decisões arquiteturais importantes** → registrar que `Recurso` passa a dizer se o
  recurso é gravado, e que o laço de coleta entrega as leituras a um gravador recebido de
  fora — o gravador nasce no `main.py`, como a bandeja e a própria coleta.
- **Melhorias — ver `aprovados.txt`** → marcar o `C1` como concluído.
- **Testes** → atualizar a contagem (hoje 392).
- **Stack** → nenhuma mudança; `sqlite3` é da biblioteca padrão e não é dependência nova.
