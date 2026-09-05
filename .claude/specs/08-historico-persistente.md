# Histórico persistente

**Ordem:** 1 de 3
**Depende de:** nenhuma
**Score:** 5
**Revisão:** pendente

## O que faz
Grava em disco, sem nada aparecer na tela, uma amostra por minuto de cada recurso e cada
episódio de alerta à parte, para o resumo da spec 09 ter o que ler.

## Comportamento

### Amostra por minuto
- Quando a coleta entrega uma leitura, o gravador acumula os valores do minuto em curso.
- Quando o minuto vira, grava a média do minuto: uma linha para CPU, uma para RAM, uma
  para a placa de vídeo, e **uma para cada unidade fixa de disco**.
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
  episódio sem fim é válido** e a spec 09 o trata como encerrado no último minuto que tem
  amostra.

### Retenção e falhas
- Ao abrir, apaga amostras e episódios com mais de 90 dias.
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
- [ ] Nenhuma linha de temperatura é gravada, mesmo com a leitura de temperatura presente.
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
- `historico/gravacao.py` — **novo**. Acumula o minuto em curso, fecha a média na virada,
  abre e fecha episódios de alerta.
- `main.py` — sobe o gravador junto com a thread de coleta e o fecha na saída limpa.
  **Não** no construtor da janela: é a mesma regra que a v2.1.0 aplicou ao ícone da bandeja
  e à própria coleta.
- `tests/historico/test_banco.py` — **novo**. Banco em pasta temporária.
- `tests/historico/test_gravacao.py` — **novo**. Relógio e leituras simulados.

## Não mexer
- `ui/` inteiro — esta spec não tem efeito visível na tela. Nenhum cartão, nenhuma linha,
  nenhum botão.
- `recursos.py` — o gravador percorre a coleção existente; não acrescenta campo a `Recurso`.
- `notifications/manager.py`, `ui/bandeja.py` — a notificação de resumo é da spec 09.
- `hardware/thresholds.py` e todos os módulos de leitura em `hardware/` — a gravação
  consome o que a coleta já produz e não muda como nada é medido nem classificado.
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
- **Melhorias — ver `aprovados.txt`** → marcar o `C1` como concluído.
- **Testes** → atualizar a contagem (hoje 392).
- **Stack** → nenhuma mudança; `sqlite3` é da biblioteca padrão e não é dependência nova.
