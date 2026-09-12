# Leitura do período de uso

**Ordem:** 2 de 3
**Depende de:** 08-historico-persistente
**Score:** 4
**Revisão:** aprovada

## O que faz
Lê o histórico gravado e responde duas perguntas, sem nada aparecer na tela: o que aconteceu
nas últimas N horas de PC ligado, e se já é hora de avisar sobre isso.

## Comportamento

### O que é "N horas de PC ligado"
- **N = 10 horas.** Fixo, não ajustável — a seção Configuração do CLAUDE.md vale aqui: para
  escolher um bom N a pessoa precisaria saber o que é um bom N.
- O período são os **600 minutos mais recentes de PC ligado**: os minutos com amostra mais
  os minutos de lacuna que a spec 08 gravou. Tempo de PC desligado não entra — ele não
  existiu para ninguém.
- **A leitura sempre diz quantos dos 600 minutos foram medidos.** O período pode ser de 10
  horas de PC ligado com 4 horas medidas, e o resumo precisa poder dizer isso em vez de
  fingir que mediu tudo. Média e pico saem só do que foi medido.
- Consequência aceita: quem usa o PC duas horas por dia recebe um período que atravessa
  vários dias. Por isso a leitura **informa se o período cruza mais de uma data** — a spec
  09b precisa disso para escrever a data junto do horário, senão "ficou pesado às 14h" fica
  ambíguo.

### O que a leitura devolve
- O período de fato coberto: primeiro e último instante, quantos minutos tem ao todo e
  **quantos deles foram medidos**.
- A média de cada recurso no período, e o maior valor atingido.
- **Recurso sem nenhuma amostra no período devolve ausência, não zero.** O caso é real — a
  placa de vídeo pode não existir na máquina, como o teste no Windows Sandbox mostrou — e
  zero diria "ficou parada" onde o certo é "não sei".
- A lista de episódios de alerta do período: recurso, quando começou, quanto durou, o valor
  de pico e o programa, quando houver.
- Por unidade de disco: quanto estava ocupado no começo do período, quanto está agora, e
  quanto resta livre em GB. **Fato, nunca previsão** — em nenhum caso se estima quando
  enche.
- Episódio **sem instante de fim** (o app foi encerrado durante o alerta) é lido como
  encerrado no último minuto que tem amostra.
- Episódio que começou antes do período e invade a janela entra, recortado ao período.

### Quando o resumo é devido
- Conta os minutos de PC ligado desde o último resumo entregue — medidos e de lacuna. **Ao
  completar 600, é devido** (`>= 600`), como toda fronteira deste projeto, que é inclusiva
  no limite inferior.
- O instante do último resumo vive no `estado.json` em `%LOCALAPPDATA%`, que já existe.
  Esta spec cria **as duas funções**: a que lê esse instante e a que o marca como entregue.
  Ela mesma só usa a primeira; quem marca é a spec 09b, quando o resumo sai.
- Enquanto nunca houve resumo, a contagem começa do minuto mais antigo que existir.
- A regra só responde **se é devido**. Se a notificação sai ou não sai, e o que ela diz, é
  da spec 09b.

### Quando não há o que ler
- Banco indisponível ou ilegível devolve **ausência de leitura**, não um resumo vazio.
  Tupla vazia é informação ("li, não houve nada"); ausência é a falta dela. É a mesma
  distinção que a consulta de saúde de disco já faz na spec 2, e confundir as duas viraria
  "nenhum alerta no período" onde o certo é "não sei".
- Menos de 600 minutos gravados devolve o que existe, **dizendo quanto é**. Não espera
  completar para responder.

## Critérios verificáveis
- [ ] `uv run pytest -v` passa, e os testes anteriores continuam passando.
- [ ] Com um banco de teste de 700 minutos, a leitura cobre os 600 mais recentes e ignora os
      100 mais antigos.
- [ ] Com 200 minutos gravados, a leitura devolve os 200 e informa que o período é de 200
      minutos, sem erro.
- [ ] Um período de 600 minutos de PC ligado com 400 medidos e 200 de lacuna informa os dois
      números.
- [ ] A média de um recurso sai só dos minutos medidos — a lacuna não puxa a média para
      baixo.
- [ ] A média e o maior valor de cada recurso batem com os valores gravados no período.
- [ ] Recurso sem nenhuma amostra no período devolve ausência, e não zero.
- [ ] Cada unidade de disco devolve o ocupado no começo, o ocupado agora e os GB livres, e
      nenhum campo da leitura projeta quando o disco enche.
- [ ] Um banco cujos 600 minutos atravessam duas datas é sinalizado como período de mais de
      um dia; um que cabe numa data, não.
- [ ] Episódio sem instante de fim é devolvido com duração até o último minuto com amostra.
- [ ] Episódio iniciado antes do período aparece recortado, com a duração dentro da janela.
- [ ] Com 599 minutos de PC ligado desde o último resumo, não é devido; com 600, é.
- [ ] Sem nenhum resumo anterior registrado, a contagem parte do minuto mais antigo.
- [ ] Marcar o resumo como entregue zera a contagem: logo depois, não é devido.
- [ ] Banco inexistente ou corrompido devolve ausência, distinguível de período sem
      episódios, e não levanta erro.
- [ ] Nenhuma instrução SQL aparece fora de `historico/banco.py`.

## Módulos afetados
- `historico/consulta.py` — **novo**. Monta o período a partir das linhas que
  `historico/banco.py` devolve: recorta a janela, calcula médias e picos, fecha episódios
  abertos. **Nenhuma instrução SQL mora aqui** — regra de negócio e acesso a dados não se
  misturam, e o banco é do módulo que o abriu.
- `historico/periodo.py` — **novo**. A regra de "o resumo é devido", contando minutos de PC
  ligado desde o último entregue.
- `sistema/estado.py` — **importado e estendido**: ganha a leitura e a escrita do instante
  do último resumo entregue. Criado pela spec 4 e já usado pela spec 5; ganha uma chave,
  não muda de forma. A escrita é criada aqui e chamada pela 09b.
- `tests/historico/test_consulta.py` — **novo**. Banco de teste em pasta temporária.
- `tests/historico/test_periodo.py` — **novo**.
- `tests/sistema/test_estado.py` — ganha os testes da chave nova.

## Não mexer
- `historico/gravacao.py` e `historico/banco.py` — criados pela spec 08. Esta spec **lê sem
  editar**, no mesmo padrão de `pdh.py` entre as specs 3 e 6: a leitura por janela de tempo
  já vem pronta de `banco.py`.
- `ui/` inteiro — esta spec não tem efeito visível. A tela é a 09b.
- `notifications/` — a notificação é da 09b. Esta spec só responde se é devido.
- `hardware/` inteiro, `recursos.py`, `thresholds.py` — nada do que é medido ou
  classificado muda.

## Decisões tomadas
- N é fixo ou ajustável? → **Fixo, 10 horas.** "Ajustável" contrariava a seção Configuração
  do CLAUDE.md. Mesmo argumento dos limites: quem sabe escolher um bom N não precisa do app.
- O tempo contado é de PC ligado ou de app aberto? → **PC ligado**, escolha do usuário,
  reafirmada em 12/09/2026 no `/spec-review`.
- Como tratar o tempo em que o PC estava ligado mas o app fechado? → **Entra no período
  como lacuna**, gravada pela spec 08. A redação anterior ("como se não existisse")
  contrariava a decisão de cima: contar só minuto com amostra é contar tempo de app aberto.
  O resumo continua sem falar do que não mediu — ele diz quantos minutos mediu, e média e
  pico saem só desses.
  **Custo identificado durante a decisão:** o período pode atravessar vários dias sem
  avisar, o que torna "às 14h" ambíguo — por isso a leitura sinaliza quando cruza datas.
- Banco indisponível devolve vazio ou ausência? → **Ausência.** Vazio é informação, ausência
  é a falta dela; a spec 2 já faz essa distinção na saúde do disco.

## Impacto no CLAUDE.md
- **Estrutura real do projeto** → acrescentar `historico/consulta.py` e `historico/periodo.py`,
  mais os dois arquivos de teste.
- **Persistência de estado** → o `estado.json` deixa de estar "sem conteúdo próprio além do
  aviso da bandeja"; passa a guardar também o instante do último resumo entregue.
- **Testes** → atualizar a contagem.
