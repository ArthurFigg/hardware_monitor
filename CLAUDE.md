## Projeto
Monitor de Hardware Minimalista — app desktop Python que traduz dados de CPU, RAM, Disco e Temperatura estimada em indicadores visuais simples (sistema de semáforo) para usuários não-técnicos.

### Escopo e público (decidido em 25/08/2026)
- **App para PC de mesa.** Bateria está fora do escopo por decisão, não por limitação — para quem não usa notebook, um card de bateria é ocupação inútil de tela.
- **Será distribuído para outras pessoas.** Não roda só na máquina do autor. Isso impõe as regras da seção "Distribuição".
- Público: quem não sabe interpretar número de hardware e quer saber se pode continuar usando o PC em paz.

## Stack
- Python 3.14.3 (pythoncore-3.14-64 — instalação Windows Store)
  - Nota antiga dizia "Tcl/Tk parcialmente disponível" sem dizer o que faltava. Verificado em 25/08/2026: Tk 8.6 presente e as pastas `tcl/`, `DLLs/` e `Lib/tkinter` existem — ou seja, o que a spec 7 precisa empacotar está lá. Se algo específico faltar, anotar aqui o que é; "parcialmente" sem detalhe não ajuda ninguém.
- psutil 7.2.2 — coleta de dados de hardware
- CustomTkinter 5.2.2 — interface gráfica moderna
- plyer 2.1.0 — notificações nativas do sistema operacional
- pytest 9.0.3 — testes
- uv — gerenciador de dependências (`uv run`, `uv add`)

## Estado atual — v1 completa; v2 planejada e ainda não implementada

A v1 está funcional. Em 25/08/2026 foi feita a triagem de 30 ideias para a v2: 12 aprovadas, 11 adiadas, 7 descartadas. O plano vive em dois arquivos na raiz:
- `aprovados.txt` — o que fazer, agrupado em 6 specs, com os achados técnicos de cada uma
- `ideias.txt` — histórico completo, incluindo o que foi recusado e por quê

Nenhuma das 6 specs foi implementada ainda.

Para rodar:

```
uv run main.py
```

Para rodar os testes (61 testes, todos passando):

```
uv run pytest -v
```

## Estrutura real do projeto

```
hardware_monitor/
├── hardware/
│   ├── __init__.py
│   ├── collector.py      — DadosHardware dataclass + coletar()
│   └── thresholds.py     — Status enum, classificar(), classificar_temperatura(),
│                           estimar_temperatura(), descricao(), descricao_temperatura(),
│                           RastreadorAlerta
├── ui/
│   ├── __init__.py
│   ├── app.py            — AplicativoMonitor(CTkFrame): orquestra coleta, cards e notificações
│   └── components/
│       ├── __init__.py
│       ├── semaphore.py  — Semaforo(CTkFrame): círculo colorido por status
│       └── cards.py      — CartaoRecurso(CTkFrame): semáforo + valor numérico + descrição
│                           Parâmetros: descricao_fn (textos por recurso) e formatar_valor
│                           (ex: "74%" para CPU/RAM/Disco, "~66°C" para Temperatura)
├── notifications/
│   ├── __init__.py
│   └── manager.py        — GerenciadorNotificacoes: dispara notificação uma vez por período de alerta
├── tests/
│   ├── hardware/
│   │   ├── test_collector.py   — 4 testes (mock psutil)
│   │   └── test_thresholds.py  — 32 testes (limites, textos, temperatura, RastreadorAlerta)
│   ├── ui/
│   │   ├── conftest.py         — fixture raiz (CTk, session-scoped)
│   │   ├── test_app.py         — 6 testes
│   │   ├── test_cards.py       — 9 testes
│   │   └── test_semaphore.py   — 5 testes
│   └── notifications/
│       └── test_manager.py     — 5 testes (mock plyer)
├── main.py               — cria CTk root, instancia AplicativoMonitor, chama mainloop()
├── aprovados.txt         — fila da v2: as 6 specs, com os achados tecnicos de cada uma
├── ideias.txt            — historico da triagem, incluindo o que foi recusado e por que
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── .gitattributes
├── README.md
└── CLAUDE.md
```

Ainda **não existe** `CHANGELOG.md`, e o `/spec-close` escreve nele a cada spec fechada —
criar antes de fechar a primeira. Também não existe `.claude/specs/`: o projeto foi
construído sem o ciclo de specs, e a v2 é a primeira a segui-lo.

## Decisões arquiteturais importantes

- `AplicativoMonitor` é `CTkFrame`, não `CTk` — o root é criado em `main.py` e passado como `master`. Isso permite que os testes compartilhem um único root Tcl/Tk (Python 3.14 não suporta múltiplos roots no mesmo processo).
- Fixture `raiz` em `conftest.py` é `scope="session"` pelo mesmo motivo — um único CTk para toda a suite.
- Thread de coleta usa `coletar()` com `interval=1` (bloqueia 1s) + loop contínuo. A UI puxa os dados a cada 100ms via `after()`.
- `RastreadorAlerta` em `thresholds.py` (não em `app.py`) porque é regra de negócio: confirma ALERTA só após 5s contínuos acima do limite.
- `GerenciadorNotificacoes` tem estado (`_notificado`) para não repetir a notificação enquanto o recurso permanece em ALERTA.
- **DEFEITO CONHECIDO, conserta na spec 1:** `manager.py` tem uma única mensagem fixa (`_MENSAGEM_ALERTA`), e `app.py` cria um notificador para os quatro recursos. Quando a **Temperatura** estoura, o usuário recebe um aviso dizendo "sobrecarga de memória/processamento" — assunto errado. E essa frase é cópia literal do texto de Alerta de CPU/RAM: a mesma string vive em `manager.py` e em `DESCRICOES`, e mudar uma não muda a outra. A spec 1 deve dar mensagem própria aos **quatro** recursos e acabar com a duplicação.
- Temperatura é **estimada** a partir do % de CPU (`estimar_temperatura(cpu)`): idle=35°C, carga máxima=85°C. Consequência a não esquecer: o card de Temperatura **não carrega informação independente** — é o % de CPU escrito em outra unidade. Por isso os pontos de corte dos dois precisam ficar alinhados (ver Thresholds), e por isso a spec 3 importa: o aviso de redução por calor é o primeiro sinal real que esse card ganha. Não usa WMI nem sensor real — leitura de sensor no Windows exige driver de kernel (admin) e não é viável sem dependência externa.
- `CartaoRecurso` aceita `descricao_fn` e `formatar_valor` para suportar textos e formatos diferentes por recurso sem duplicar o componente.

## Thresholds (nunca alterar sem avisar)
Fronteiras são inclusivas no limite inferior (`>=`), como o código faz — 60,0% já é Atenção; 85,0% já é Alerta.

- Normal: CPU e RAM abaixo de 60%
- Atenção: CPU ou RAM de 60% a 84,9%
- Alerta: CPU ou RAM em 85% ou mais, por mais de 5 segundos
- Temperatura Normal: abaixo de 65°C
- Temperatura Atenção: de 65°C a 79,9°C
- Temperatura Alerta: 80°C ou mais, por mais de 5 segundos

**Temperatura Atenção mudou de 60°C para 65°C em 25/08/2026** — este é o aviso exigido acima. Motivo: a temperatura é derivada do % de CPU (`estimar_temperatura`), então cada temperatura corresponde a um percentual exato. Com 60°C, o card de Temperatura acendia em CPU 50% — **antes** do card de CPU, que acende em 60%. Toda carga entre 50% e 59% mostrava amarelo na Temperatura com a CPU em verde, o que parece máquina esquentando sem motivo e corrói a confiança no semáforo. 65°C corresponde exatamente a CPU 60%: os dois acendem juntos.

O Alerta continua em 80°C (CPU 90%) de propósito, com a CPU ficando vermelha antes, em 85%. Temperatura **atrasada** em relação à carga é fisicamente correto — calor demora a subir. O defeito era a temperatura adiantada.

**A implementar na spec 3** (`LIMITE_TEMP_ATENCAO` em `thresholds.py`, mais os testes de limite em `test_thresholds.py`). Esta skill não altera código.

**Disco (a mudar na spec 2 — este é o aviso exigido acima):** hoje o Disco não tem threshold próprio. Ele passa pelo mesmo `classificar()` de CPU e RAM (60/85) e herda o mesmo texto, o que produz conselho errado: disco 87% cheio manda "feche aplicativos inativos", e fechar programa não libera espaço em disco. A **spec 1** é dona de todos os textos do Disco — ela é dona de tudo que o app diz. A **spec 2** cria `classificar_disco()` e decide o limiar. Textos e medição foram separados de propósito: o texto não depende do limite.

## Textos da interface (usar exatamente esses, sem alterar tom)
CPU / RAM (e Disco, até a spec 2 dar textos próprios a ele):
- Normal: "Desempenho estável. O sistema está operando com folga."
- Atenção: "Carga moderada. Vários processos estão exigindo recursos da máquina."
- Alerta: "Sobrecarga de memória/processamento. Feche aplicativos inativos para evitar travamentos."

Temperatura:
- Normal: "Temperatura dentro do esperado. O processador está operando com segurança."
- Atenção: "Temperatura elevada. Verifique a ventilação do computador."
- Alerta: "Temperatura crítica. Feche aplicativos pesados e verifique o sistema de resfriamento."

## Regras fixas
- Coleta de dados sempre em thread separada, nunca na thread principal
- Nunca misturar lógica de hardware com lógica de UI
- Notificações só disparam no estado Alerta, silenciosas, somem sozinhas
- Todo módulo novo precisa de arquivo pytest junto — cobrindo a lógica dele. O que não é testável é a integração com o Windows, não o módulo (ver "Testes")
- Sem emojis ou tom de assistente animado nos textos da interface

## UI/UX
- Estilo minimalista, sem bordas pesadas ou gráficos de linha
- Suporte a Light Mode e Dark Mode com botão toggle
- Valor numérico exibido em todos os cards: percentual (%) para CPU/RAM/Disco, temperatura estimada (~°C) para Temperatura

## Melhorias — ver `aprovados.txt`
A lista solta que existia aqui foi substituída pela triagem de 25/08/2026. Não reintroduzir itens aqui: `aprovados.txt` é a fila, `ideias.txt` é o histórico.

As 7 specs aprovadas, na ordem:
1. Notificações que dizem qual recurso e qual programa
2. Card Disco com limiares e textos próprios, saúde do disco, múltiplos discos
3. Correção do limiar de Temperatura Atenção (60°C → 65°C) + aviso de redução de velocidade por calor (contador PDH do Windows)
4. Abrir com o Windows e uptime no rodapé
5. Ícone na bandeja, com minimizar para lá
6. Cartão de placa de vídeo com uso real (usa o mecanismo da spec 3)
7. Empacotar em `.exe` (depende do caminho definido na spec 4)

Depois delas, como projeto à parte: histórico persistente e resumo das últimas N horas.

**Três ideias foram descartadas resolvendo contradições que existiam neste arquivo:**
- Gráfico de linha: contrariava a regra de UI/UX. A regra fica, o item saiu.
- Notificação em Atenção: contrariava "Regras fixas" e "Não fazer". Decisão final: não dispara em Atenção — 60% a 84% acontece em uso normal e viraria ruído que faz o usuário desligar as notificações.
- Configuração de thresholds pelo usuário: descartada. Ver "Configuração".

## Não fazer
- Não misturar responsabilidades num arquivo só
- Não criar lógica de negócio dentro de app.py
- Não disparar notificações em estados Normal ou Atenção (decidido em 25/08/2026: é definitivo, não é pendência)
- Não usar jargões técnicos nos textos da interface
- Não criar segundo root CTk nos testes — usar a fixture `raiz` de conftest.py
- Não tentar ler temperatura real via WMI — exige admin e não funciona em todos os hardwares

## Distribuição (decidido em 25/08/2026)
O app será usado por outras pessoas, em outras máquinas, com outros Windows.

- **Nenhum caminho da máquina do autor.** Nem `.venv`, nem a pasta do projeto. Na máquina
  do usuário final elas não existem.
- **Toda leitura de hardware precisa degradar sozinha.** Os contadores foram validados numa
  máquina só (Windows 11 build 26200, em português). Em Windows mais antigo, em outro idioma
  ou em PC sem placa dedicada, a leitura pode falhar. Regra: **falhou, esconde a linha ou o
  card. Nunca quebra o app.**
- Nomes de contadores do Windows são traduzidos por idioma. Resolver por índice
  (`Perflib\009` dá o índice a partir do nome em inglês) e cair para o nome em inglês quando
  não houver tradução — o contador de GPU não é traduzido, o de CPU é.
- O card de GPU precisa se comportar em PC sem placa dedicada.

## Persistência de estado
- Nada é gravado em disco na v1.
- A partir da v2, o que for gravado vai para `%LOCALAPPDATA%` — **nunca** na pasta do app.
  Vale para o histórico e para o interruptor de abrir com o Windows.
- A pasta deste projeto está dentro do OneDrive: gravar aqui sincronizaria arquivo sem parar.

## Ciclo de vida da janela (a implementar na spec 4)
- O app abre junto com o Windows, **minimizado**, e nunca rouba a tela no boot.
- Isso é opcional e reversível por um interruptor na própria interface. Programa que se
  instala na inicialização e não oferece saída é comportamento de coisa ruim.
- Fechar a janela esconde para a bandeja; não encerra o monitoramento.
- Entrada de inicialização na chave `Run` do `HKCU` (não exige admin), apontando para o
  `.exe` da spec 7.

## Configuração
O app **não tem configuração pelo usuário**, e isso é decisão, não esquecimento.

- Não há `.env` nem `.env.example` — não existe nada para configurar.
- Limiares não são ajustáveis (nem por arquivo, nem por tela). Para escolher um limite a
  pessoa precisa saber o que é um bom limite; quem sabe isso não precisa deste app.
  Ter escolhido 60% e 85% por ela é o produto, não uma limitação dele.
- Se usuários reclamarem que alerta demais ou de menos, o sinal é ajustar o padrão para
  todo mundo — não transferir a decisão a eles.
- Única exceção: o interruptor de abrir com o Windows.

## Setup do ambiente

> Projeto **existente**, não novo: não há `uv init` a rodar. Este setup é ajuste do que já
> existe, e quita as dívidas da seção "Qualidade — dívidas conhecidas".

**Python:** 3.14 — **mantido**. A preferência geral é pela penúltima estável, mas essa regra
existe para evitar biblioteca sem suporte, e foi verificado em 26/08/2026 que as quatro
dependências que ainda vão entrar (`ruff` 0.16.4, `pystray` 0.19.5, `Pillow` 12.3.0,
`pyinstaller` 6.22.2) resolvem para 3.14. Trocar agora seria mexer num ambiente com 61 testes
passando sem ganho — e a arquitetura de testes (fixture de root único) existe por causa do
3.14.

**Comandos de execução:**
```bash
uv add "psutil>=7.2.2,<8.0.0" "customtkinter>=5.2.2,<6.0.0" "plyer>=2.1.0,<3.0.0"
uv add --dev "pytest>=9.0.3,<10.0.0" "ruff>=0.16.4,<0.17.0"
uv run ruff format .
uv run ruff check .
uv run pytest -v
```

As três primeiras já estão instaladas — o `uv add` aqui serve para **acrescentar o teto de
versão**, que hoje falta. O teto do `ruff` é apertado de propósito: ele ainda está em `0.x`, e
regra de formatação muda entre versões menores; teto largo faria o formatador reescrever o
projeto sozinho numa atualização.

**Antes de aceitar o `ruff format`:** ele conserta as 10 linhas acima de 88 caracteres de uma
vez, mas reformata tudo que discordar do estilo dele — o diff pode ser bem maior que 10 linhas.
Olhar o diff antes de commitar. Os textos da interface são fixos: quebrar a linha, **nunca**
mudar a frase.

**Pastas a criar:** nenhuma. A spec 1 cria `recursos.py` na raiz e `hardware/processos.py`, e
as duas pastas já existem. O pacote `sistema/` entra na spec 4.

**Arquivo a criar:**
```bash
touch CHANGELOG.md
```
O `/spec-close` escreve nele a cada spec fechada, e a spec 1 é a primeira do ciclo. Formato
Keep a Changelog + SemVer, conforme o CLAUDE.md global.

**Conteúdo do `.env.example`:** nenhum. O app não tem configuração pelo usuário, por decisão
registrada na seção "Configuração" — não existe o que configurar.

**Dependências que ficam de fora agora** (entram quando a spec chegar):
- `pystray`, `Pillow`: spec 5 (ícone na bandeja)
- `pyinstaller` (dev): spec 7 (empacotar em `.exe`)

**CI — `.github/workflows/tests.yml`:**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest -v
```

**Ressalva sobre o CI:** o runner é Linux e o app é Windows-only — leitura de registro,
contadores PDH e `Get-PhysicalDisk` não existem lá. Isso só funciona porque a regra de testes
do projeto manda mockar toda fronteira de sistema; se algum teste tocar o Windows de verdade,
ele quebra no CI. É uma trava útil: CI vermelho aqui significa teste que não devia existir.

## Qualidade — dívidas conhecidas (levantadas em 25/08/2026)
Achadas comparando o projeto com as regras do CLAUDE.md global. Nenhuma é urgente;
todas devem ser resolvidas na etapa de setup, antes da primeira spec.

- **`ruff` está configurado mas não instalado.** O `pyproject.toml` tem
  `[tool.ruff] line-length = 88`, mas o ruff não é dependência do projeto — nunca rodou.
  Instalar como dependência de desenvolvimento e rodar antes da primeira spec.
- **10 linhas passam de 88 caracteres**, consequência direta do item acima:
  4 em `hardware/thresholds.py`, 3 em `tests/hardware/test_thresholds.py`,
  2 em `ui/components/cards.py`, 1 em `tests/ui/test_app.py`.
  Quase todas são os textos longos da interface. **Quebrar a linha, nunca mudar a frase** —
  os textos são fixos (ver "Textos da interface").
- **Dois construtores passam de 20 linhas:** `ui/app.py.__init__` (44) e
  `ui/components/cards.py.__init__` (35). O do `app.py` vai crescer: a spec 4 acrescenta o
  interruptor de inicialização e a spec 5 acrescenta o card de GPU. Extrair a montagem dos
  cards e dos notificadores antes que as specs piorem o quadro.
- **Dependências sem teto de versão** no `pyproject.toml` (`customtkinter>=5.2.2` sem
  `<6.0.0`, e as demais). Contraria a regra global de sempre fixar teto. Corrigir junto com
  a instalação do ruff.

Verificado e limpo: nenhum `print()`, nenhum `except`, nenhum `import *`, nenhum uso de
async.

## Testes — o que precisa estar coberto
Regra: **lógica coberta, fronteira mockada.**

- Toda regra de decisão tem teste com valores simulados: quando classificar em cada status,
  quando acusar redução por calor, quando esconder uma linha que falhou ao ler.
- Leitura real de hardware é fronteira: mockar, como já se faz com `psutil` e `plyer`.
- **Ficam sem teste automatizado, por não serem testáveis:** o desenho do ícone na
  bandeja, o superaquecimento físico e o comportamento dos contadores do Windows em
  outras máquinas. Verificação desses três é rodando o app.
- Isso não isenta o módulo do teste: o módulo da bandeja tem arquivo de teste como
  qualquer outro, cobrindo a lógica dele (qual cor para qual status, o que acontece ao
  clicar). O que fica de fora é a chamada ao Windows que desenha o ícone.
- Não criar teste que dependa do hardware desta máquina. Num app distribuído, teste que só
  passa aqui é teste que mente para quem baixar.
