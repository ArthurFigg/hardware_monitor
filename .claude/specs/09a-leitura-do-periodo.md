# Leitura do período de uso

**Ordem:** 2 de 3
**Depende de:** 08-historico-persistente
**Score:** 4
**Revisão:** pendente

## O que faz
Lê o histórico gravado e responde duas perguntas, sem nada aparecer na tela: o que aconteceu
nas últimas N horas de uso, e se já é hora de avisar sobre isso.

## Comportamento

### O que é "N horas de uso"
- **N = 10 horas.** Fixo, não ajustável — a seção Configuração do CLAUDE.md vale aqui: para
  escolher um bom N a pessoa precisaria saber o que é um bom N.
- Uma hora de uso é uma hora com amostra gravada. O período são os **600 minutos gravados
  mais recentes**, venham de quando vierem.
- Tempo em que o PC estava ligado mas o app não rodava **não existe** para o período: sem
  amostra, sem minuto. O resumo nunca fala do que não mediu.
- Consequência aceita: quem usa o PC duas horas por dia recebe um período que atravessa
  vários dias. Por isso a leitura **informa se o período cruza mais de uma data** — a spec
  09b precisa disso para escrever a data junto do horário, senão "ficou pesado às 14h" fica
  ambíguo.

### O que a leitura devolve
- O período de fato coberto: primeiro e último instante com amostra, e quantos minutos tem.
- A média de cada recurso no período, e o maior valor atingido.
- A lista de episódios de alerta do período: recurso, quando começou, quanto durou, o valor
  de pico e o programa, quando houver.
- Por unidade de disco: quanto estava ocupado no começo do período, quanto está agora, e
  quanto resta livre. **Fato, nunca previsão** — em nenhum caso se estima quando enche.
- Episódio **sem instante de fim** (o app foi encerrado durante o alerta) é lido como
  encerrado no último minuto que tem amostra.
- Episódio que começou antes do período e invade a janela entra, recortado ao período.

### Quando o resumo é devido
- Conta os minutos com amostra desde o último resumo entregue. Ao passar de 600, é devido.
- O instante do último resumo vive no `estado.json` em `%LOCALAPPDATA%`, que já existe.
- Enquanto nunca houve resumo, a contagem começa da amostra mais antiga que existir.
- A regra só responde **se é devido**. Se o aviso sai ou não sai, e o que ele diz, é da
  spec 09b.

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
- [ ] Um banco cujos 600 minutos atravessam duas datas é sinalizado como período de mais de
      um dia; um que cabe numa data, não.
- [ ] Episódio sem instante de fim é devolvido com duração até o último minuto com amostra.
- [ ] Episódio iniciado antes do período aparece recortado, com a duração dentro da janela.
- [ ] Com 599 minutos desde o último resumo, não é devido; com 600, é.
- [ ] Sem nenhum resumo anterior registrado, a contagem parte da amostra mais antiga.
- [ ] Banco inexistente ou corrompido devolve ausência, distinguível de período sem
      episódios, e não levanta erro.

## Módulos afetados
- `historico/consulta.py` — **novo**. Monta o período a partir das amostras e episódios e
  devolve a leitura pronta.
- `historico/periodo.py` — **novo**. A regra de "o resumo é devido", contando minutos com
  amostra desde o último entregue.
- `sistema/estado.py` — **importado e estendido**: passa a guardar o instante do último
  resumo entregue. Criado pela spec 4 e já usado pela spec 5; ganha uma chave, não muda
  de forma.
- `tests/historico/test_consulta.py` — **novo**. Banco de teste em pasta temporária.
- `tests/historico/test_periodo.py` — **novo**.

## Não mexer
- `historico/gravacao.py` e `historico/banco.py` — criados pela spec 08. Esta spec **lê sem
  editar**, no mesmo padrão de `pdh.py` entre as specs 3 e 6.
- `ui/` inteiro — esta spec não tem efeito visível. A tela é a 09b.
- `notifications/` — o aviso é da 09b. Esta spec só responde se é devido.
- `hardware/` inteiro, `recursos.py`, `thresholds.py` — nada do que é medido ou
  classificado muda.

## Decisões tomadas
- N é fixo ou ajustável? → **Fixo, 10 horas.** "Ajustável" contrariava a seção Configuração
  do CLAUDE.md. Mesmo argumento dos limites: quem sabe escolher um bom N não precisa do app.
- O tempo contado é de PC ligado ou de app aberto? → **PC ligado**, escolha do usuário.
- Como tratar o tempo em que o PC estava ligado mas o app fechado? → **Como se não
  existisse.** É o único caminho em que o resumo nunca fala do que não mediu.
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
