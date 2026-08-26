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

## Estado atual — v2 em andamento: 1 spec de 7 concluída

A v1 está funcional. Em 25/08/2026 foi feita a triagem de 30 ideias para a v2: 12 aprovadas, 11 adiadas, 7 descartadas. O plano vive em dois arquivos na raiz:
- `aprovados.txt` — o que fazer, agrupado em specs, com os achados técnicos de cada uma
- `ideias.txt` — histórico completo, incluindo o que foi recusado e por quê

A triagem falava em 6 specs; o `/spec` gerou **7** — a fila real está em `.claude/specs/`.
As specs 1 (notificações por recurso), 2 (medição de disco), 3 (redução de velocidade por
calor) e 4 (abrir com o Windows e rodapé) foram concluídas em 26/08/2026. As 3 restantes
estão aprovadas pelo `/spec-review` e pendentes, na ordem 05 → 07. A próxima é a
**05 — ícone na bandeja**.

Para rodar:

```
uv run main.py
```

Para rodar os testes (246 testes, todos passando):

```
uv run pytest -v
```

## Estrutura real do projeto

```
hardware_monitor/
├── hardware/
│   ├── __init__.py
│   ├── collector.py      — DadosHardware dataclass + coletar()
│   ├── processos.py      — varredura sob demanda: quem está consumindo CPU/RAM
│   ├── discos.py         — unidades fixas (filtros de removível/rede/CD e de <10 GB) +
│                           saúde dos discos físicos via Get-PhysicalDisk, com cache de 6h
│   ├── pdh.py            — contadores de desempenho do Windows via ctypes; nome resolvido
│                           por índice, com queda para o inglês. A spec 6 importa sem editar
│   ├── desempenho.py     — % Processor Performance + LeituraTemperatura e a regra de calor
│   └── thresholds.py     — Status enum, classificar(), classificar_temperatura(),
│                           estimar_temperatura(), descricao(), descricao_temperatura(),
│                           classificar_unidade(), classificar_disco(), mais_grave(),
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
│   │   ├── test_collector.py   — 8 testes (mock psutil)
│   │   ├── test_desempenho.py  — 11 testes (pdh mockado)
│   │   ├── test_discos.py      — 24 testes (mock psutil e PowerShell)
│   │   ├── test_pdh.py         — 16 testes (pdh.dll mockada)
│   │   ├── test_processos.py   — 8 testes (mock psutil)
│   │   └── test_thresholds.py  — 46 testes (limites, textos, temperatura, disco,
│   │                             calor, RastreadorAlerta)
│   ├── ui/
│   │   ├── conftest.py         — fixture raiz (CTk, session-scoped)
│   │   ├── test_app.py         — 33 testes
│   │   ├── test_cards.py       — 13 testes
│   │   └── test_semaphore.py   — 5 testes
│   ├── notifications/
│   │   └── test_manager.py     — 13 testes (mock plyer)
│   ├── sistema/
│   │   ├── test_inicializacao.py — 18 testes (winreg mockado)
│   │   ├── test_estado.py        — 8 testes (pasta temporária)
│   │   └── test_uptime.py        — 6 testes
│   └── test_recursos.py        — 33 testes (textos, causas, origem única das frases)
├── sistema/
│   ├── __init__.py
│   ├── inicializacao.py  — entrada na chave Run do HKCU; caminho resolvido em execução
│   ├── estado.py         — o pouco que o app lembra entre execuções, em %LOCALAPPDATA%
│   └── uptime.py         — "Ligado há 5h 23min" a partir dos segundos desde o boot
├── recursos.py           — Recurso: fonte única do que o app vigia e do que ele diz
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

O `CHANGELOG.md` foi criado em 26/08/2026, com a v1.0.0 registrada e a seção "Não lançado"
pronta para o `/spec-close`. O `.claude/specs/` tem as 7 specs da v2, o `_dominio.md` e o
`_decisoes.md`. O CI está em `.github/workflows/tests.yml`.

## Decisões arquiteturais importantes

- `AplicativoMonitor` é `CTkFrame`, não `CTk` — o root é criado em `main.py` e passado como `master`. Isso permite que os testes compartilhem um único root Tcl/Tk (Python 3.14 não suporta múltiplos roots no mesmo processo).
- Fixture `raiz` em `conftest.py` é `scope="session"` pelo mesmo motivo — um único CTk para toda a suite.
- Thread de coleta usa `coletar()` com `interval=1` (bloqueia 1s) + loop contínuo. A UI puxa os dados a cada 100ms via `after()`.
- `RastreadorAlerta` em `thresholds.py` (não em `app.py`) porque é regra de negócio: confirma ALERTA só após 5s contínuos acima do limite.
- `GerenciadorNotificacoes` tem estado (`_notificado`) para não repetir a notificação enquanto o recurso permanece em ALERTA.
- **`recursos.py` na raiz é a fonte única do que o app vigia e do que ele diz.** Cada `Recurso` carrega: função de classificação própria, textos de cartão e de notificação (com variantes por causa — o Disco tem duas redações de Alerta), se notifica, se varre processos, formato do valor e se o cartão pode sumir. `app.py` monta cartões, rastreadores e notificadores percorrendo essa coleção e **não conhece nenhum recurso por nome**. Acrescentar um recurso é uma entrada, não três.
- O **pior status** entre os recursos é calculado em `recursos.py`, nunca em `app.py`. Recurso indisponível fica de fora da conta e o cartão dele some da tela.
- Temperatura é **estimada** a partir do % de CPU (`estimar_temperatura(cpu)`): idle=35°C, carga máxima=85°C. Consequência a não esquecer: o card de Temperatura **não carrega informação independente** — é o % de CPU escrito em outra unidade. Por isso os pontos de corte dos dois precisam ficar alinhados (ver Thresholds), e por isso a spec 3 importa: o aviso de redução por calor é o primeiro sinal real que esse card ganha. Não usa WMI nem sensor real — leitura de sensor no Windows exige driver de kernel (admin) e não é viável sem dependência externa.
- `CartaoRecurso` aceita `descricao_fn` e `formatar_valor` para suportar textos e formatos diferentes por recurso sem duplicar o componente.
- **O Disco olha todas as unidades fixas, e o status do cartão é o pior entre elas.**
  Unidade removível, de rede, de CD e qualquer uma com menos de 10 GB de tamanho total
  ficam de fora — este último filtro existe pela partição de recuperação do Windows
  (~500 MB, sempre quase cheia), que sem ele deixaria o app em Alerta permanente. O
  cartão exibe a unidade que decidiu o status, nomeada: "D: — 100%". **A pior unidade
  é a de pior status, não a de maior percentual** — as duas regras podem apontar para
  discos diferentes (um SSD de sistema com 8 GB livres está em Alerta pela regra de
  espaço e perde no percentual para um HD em 94% que está só em Atenção), e ordenar pelo
  percentual faria o semáforo acender por um disco e o rótulo nomear outro.
- **A saúde é do disco físico e nunca é mapeada em unidade.** Um disco com várias
  partições faria o mapeamento errar, então a linha extra nomeia o disco. É relida a cada
  6 horas: desgaste evolui em semanas, a consulta custa ~3 s (abre um PowerShell), e o app
  vai viver na bandeja por semanas sem reiniciar (spec 4).
- **Consulta de saúde que falha devolve `None`, e `None` não é "todos saudáveis".** Tupla
  vazia é informação ("consultei, está tudo bem"); `None` é ausência dela. Os dois escondem
  a linha, mas só o segundo poderia virar alerta falso se fossem confundidos.
- **Laço agendado com `after()` para de mexer na tela assim que o app para.** Tanto a
  atualização dos cartões quanto a do rodapé checam isso **na entrada**, não só na hora de
  reagendar: sem essa checagem, um callback já agendado ainda dispara depois do fechamento e
  escreve em widget em destruição.
- **A velocidade real do processador vem de uma consulta PDH persistente**, aberta uma
  vez e reaproveitada, com o nome do contador resolvido pelo **número** (`Processor
  Information` = 2610, `% Processor Performance` = 2660). Confirmado nesta máquina: o nome
  devolvido é "% de Desempenho do Processador" — o nome em inglês não existe aqui, então
  resolver por índice não é preciosismo, é o que faz o contador abrir.
- **`psutil.cpu_freq()` não serve no Windows** e não deve ser tentado: devolve 3701 MHz
  fixo nesta máquina, parado ou sob carga, porque lê a frequência nominal do registro e não
  o clock real.
- **A primeira leitura de um contador PDH é sempre descartada.** Um contador de taxa calcula
  a diferença entre duas amostras, e a amostra de abertura fica a microssegundos da primeira
  leitura: o valor sai sem sentido (medido: 43% num processador que estava em 107%). Não dá
  para distinguir isso de uma queda real.
- **A janela de 5 s do aviso de calor avança dentro do `coletar()`, e só ali.** É o único
  ponto que roda uma vez por ciclo. Se o relógio andasse em quem lê os dados, cada consumidor
  novo (a bandeja da spec 5) o encurtaria pela metade sem que ninguém percebesse.
- **`Recurso` ganhou `causa_fn`, `linha_extra_fn`, `detalhe_fn` e `descricao_de()`** — o
  Disco é o único que os usa hoje. Sem eles, a variante de texto de desgaste que a spec 1
  escreveu era código morto: não havia caminho que a acionasse. O cartão chama
  `descricao_de(status, valor)`, que resolve a causa a partir da leitura — chamar
  `descricao(status)` direto devolvia sempre a causa padrão, que para o Disco é espaço, e
  o disco em desgaste mandava apagar arquivo. `app.py` mudou em três linhas e continua sem
  conhecer recurso por nome.

## Thresholds (nunca alterar sem avisar)
Fronteiras são inclusivas no limite inferior (`>=`), como o código faz — 60,0% já é Atenção; 85,0% já é Alerta.

- Normal: CPU e RAM abaixo de 60%
- Atenção: CPU ou RAM de 60% a 84,9%
- Alerta: CPU ou RAM em 85% ou mais, por mais de 5 segundos
- Temperatura Normal: abaixo de 65°C
- Temperatura Atenção: de 65°C a 79,9°C
- Temperatura Alerta: 80°C ou mais, por mais de 5 segundos

**Temperatura Atenção mudou de 60°C para 65°C — implementado na spec 3 em 26/08/2026.** Motivo: a temperatura é derivada do % de CPU (`estimar_temperatura`), então cada temperatura corresponde a um percentual exato. Com 60°C, o card de Temperatura acendia em CPU 50% — **antes** do card de CPU, que acende em 60%. Toda carga entre 50% e 59% mostrava amarelo na Temperatura com a CPU em verde, o que parece máquina esquentando sem motivo e corrói a confiança no semáforo. 65°C corresponde exatamente a CPU 60%: os dois acendem juntos.

O Alerta continua em 80°C (CPU 90%) de propósito, com a CPU ficando vermelha antes, em 85%. Temperatura **atrasada** em relação à carga é fisicamente correto — calor demora a subir. O defeito era a temperatura adiantada.

**Em vigor desde 26/08/2026.** Conferido ponto a ponto na máquina: CPU 59% deixa os dois
cartões em Normal, CPU 60% acende os dois em Atenção juntos, e o Alerta segue desalinhado de
propósito (CPU vermelha em 85%, temperatura só em 90%).

**Aviso de redução de velocidade por calor:** aparece quando a carga fica em **85% ou mais** e
a velocidade do processador **abaixo de 90%**, as duas juntas, por 5 segundos contínuos. Não
muda o status nem dispara notificação — é linha extra no cartão de Temperatura. As duas
condições são obrigatórias porque o contador também cai com o PC ocioso, e ali a queda é
economia de energia. O 90% é fundamentado e não medido (não dá para provocar superaquecimento
real): é o primeiro número a ajustar se o aviso nunca aparecer ou aparecer demais.

**Disco — implementado na spec 2 em 26/08/2026.** Tem limiares próprios, e dois de cada
tipo. Cada unidade é classificada pelo **pior dos dois critérios**, o que acontecer primeiro:

- Atenção: 85% ocupado **ou** menos de 20 GB livres
- Alerta: 95% ocupado **ou** menos de 10 GB livres, por mais de 5 segundos
- Desgaste do disco físico: **Alerta direto**, sem passar pelos números

Percentual sozinho não serve: 95% de um SSD de 120 GB deixa 6 GB, com o que o Windows já não
instala atualização — avisaria tarde. 95% de 1 TB deixa 50 GB, que é folga — avisaria cedo, e
alarme falso ensina a ignorar o semáforo. Verificado nesta máquina em 26/08/2026: C: em 77,6%
com 208 GB livres (Normal) e D: em 99,6% com 478 MB livres (Alerta pelos dois critérios).

## Textos da interface (usar exatamente esses, sem alterar tom)

**Origem única: `recursos.py` na raiz.** Nenhuma frase é escrita em `manager.py` nem em
`thresholds.py` — há teste que varre o projeto e falha se alguma for duplicada.

CPU / RAM:
- Normal: "Desempenho estável. O sistema está operando com folga."
- Atenção: "Carga moderada. Vários processos estão exigindo recursos da máquina."
- Alerta: "Sobrecarga de memória/processamento. Feche aplicativos inativos para evitar travamentos."

Disco:
- Normal: "Espaço em disco suficiente. Não há risco no momento."
- Atenção: "Espaço em disco diminuindo. Vale apagar arquivos que você não usa mais."
- Alerta por falta de espaço: "Espaço em disco acabando. Apague arquivos grandes ou mova para outro lugar."
- Alerta por desgaste: "Disco com sinais de desgaste. Faça uma cópia dos seus arquivos importantes."

Notificações (título + corpo), uma por recurso:
- CPU: "CPU em sobrecarga" / "{programa} está usando {N}% da CPU. Feche programas que não estiver usando."
- RAM: "Memória em sobrecarga" / mesma frase, trocando CPU por memória
- Disco (espaço): "Espaço em disco acabando" / "Apague arquivos grandes ou mova para outro lugar."
- Disco (desgaste): "Disco com sinais de desgaste" / "Faça uma cópia dos seus arquivos importantes."
- O texto de desgaste do cartão vale em **Atenção e em Alerta**, com a mesma frase: o
  `RastreadorAlerta` segura o Disco em Atenção nos primeiros 5 s, e sem a variante nesse
  status o cartão cairia no texto de espaço — mandando apagar arquivo para resolver
  defeito de hardware.
- Temperatura: "Temperatura crítica" / "O processador está muito quente. Feche programas pesados e verifique a ventilação."
- Sem programa identificado, o corpo sai só com a frase de ação — nunca com lacuna vazia.
- O alerta de espaço ganha os números antes da ação: "Restam 4,2 GB na unidade C:". É
  acréscimo, não substituição — a frase de ação continua correta sozinha, e o alerta de
  desgaste não recebe esse acréscimo porque lá o espaço é irrelevante.

Linha extra do cartão (abaixo da descrição, escondida quando vazia):
- Disco com desgaste: "O disco {nome} está dando sinais de desgaste."
- A spec 3 reusa essa mesma linha para o aviso de redução de velocidade por calor.

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
- **Rodapé:** interruptor "Abrir junto com o Windows" à esquerda, botão de tema à direita, e
  abaixo a linha discreta de uptime da máquina ("Ligado há 5h 23min") — sem cor e sem
  semáforo, porque não existe uptime em alerta. Atualiza de minuto em minuto.
- O rodapé usa `grid`, não `pack`: a regra de packing do projeto (`side="right"` antes de
  qualquer `expand=True`) é fácil de violar sem perceber, e o `grid` não tem esse problema.

## Melhorias — ver `aprovados.txt`
A lista solta que existia aqui foi substituída pela triagem de 25/08/2026. Não reintroduzir itens aqui: `aprovados.txt` é a fila, `ideias.txt` é o histórico.

As 7 specs aprovadas, na ordem:
1. ~~Notificações que dizem qual recurso e qual programa~~ — **concluída em 2026-08-26**
2. ~~Card Disco com limiares e textos próprios, saúde do disco, múltiplos discos~~ — **concluída em 2026-08-26**
3. ~~Correção do limiar de Temperatura Atenção (60°C → 65°C) + aviso de redução de velocidade por calor (contador PDH do Windows)~~ — **concluída em 2026-08-26**
4. ~~Abrir com o Windows e uptime no rodapé~~ — **concluída em 2026-08-26**
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
- **O interruptor de abrir com o Windows não tem estado próprio.** A entrada na chave `Run`
  do `HKCU` **é** o estado: o app a lê ao abrir e o interruptor nasce do que está lá. Assim
  não há como o interruptor discordar da realidade, nem quando a pessoa remove a entrada por
  fora, pelo Gerenciador de Tarefas.
- O que de fato vai para `%LOCALAPPDATA%` é o `sistema/estado.py`
  (`%LOCALAPPDATA%\MonitorDeHardware\estado.json`), hoje sem conteúdo próprio — ele existe
  para a spec 5 lembrar se já mostrou a mensagem de primeira vez.
- A pasta deste projeto está dentro do OneDrive: gravar aqui sincronizaria arquivo sem parar.

## Ciclo de vida da janela

**Implementado na spec 4 em 26/08/2026:**
- O app abre junto com o Windows, **minimizado**, e nunca rouba a tela no boot. A entrada
  passa `--minimizado`, e o `.exe` da spec 7 precisa aceitar exatamente esse argumento.
- Isso é opcional e reversível por um interruptor na própria interface. Programa que se
  instala na inicialização e não oferece saída é comportamento de coisa ruim — e isso vale
  nos dois sentidos: **quando a remoção da entrada falha, o interruptor volta a marcado e
  avisa que o app ainda vai abrir.** Desmarcar em silêncio com a entrada ainda lá seria
  exatamente o comportamento que a regra proíbe.
- Entrada na chave `Run` do `HKCU` (não exige admin). O caminho é resolvido em tempo de
  execução: `pythonw.exe` mais o `main.py` em desenvolvimento, o `.exe` quando empacotado.
  Nunca caminho fixo — na máquina de quem instalar, a pasta deste projeto não existe.

**Ainda pendente (spec 5):**
- Fechar a janela esconde para a bandeja; não encerra o monitoramento. Hoje fechar ainda
  encerra o app.

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

**EXECUTADO em 26/08/2026.** Resultado real, que corrige a expectativa que estava escrita aqui:
o `ruff format` **não** conserta linha longa que seja *string* — formatador nenhum quebra
string. Ele arrumou 3 arquivos (ordenação de imports, asserções longas, chamadas de `grid`), as
linhas caíram de 10 para 5, e os 61 testes continuaram passando. Nenhum texto de interface foi
alterado — as frases só passaram para linha própria.

**As 5 que restam são todas os textos da interface** em `DESCRICOES` e um teste que compara com
um deles. Ficam como estão de propósito: a **spec 1** move esses textos para `recursos.py`, e
quebrá-los agora seria trabalho que a spec 1 refaz. A spec 1 já os escreve quebrados.

E vale saber: o `ruff check` **não reclama** de linha longa — essa regra não está no conjunto
padrão. O `line-length = 88` só orienta o formatador.

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

- ~~`ruff` configurado mas não instalado~~ → **resolvido em 26/08/2026**: `ruff>=0.16.4,<0.17.0`
  entrou como dependência de desenvolvimento e rodou.
- ~~10 linhas passam de 88 caracteres~~ → **5, em 26/08/2026**. O `ruff format` resolveu as
  outras 5. As restantes (4 em `hardware/thresholds.py`, 1 em
  `tests/hardware/test_thresholds.py`) são *strings* — os textos da interface — e formatador
  não quebra string. Ficam para a **spec 1**, que move esses textos para `recursos.py` e já os
  escreve quebrados. Quebrar antes seria refazer depois.
- **Dois construtores passam de 20 linhas:** `ui/app.py.__init__` (**35**, era 44 — encolheu
  com a troca dos três dicionários pelo `Recurso`) e `ui/components/cards.py.__init__` (35). O do `app.py` vai crescer: a spec 4 acrescenta o
  interruptor de inicialização e a spec 5 acrescenta o card de GPU. Extrair a montagem dos
  cards e dos notificadores antes que as specs piorem o quadro.
- ~~Dependências sem teto de versão~~ → **resolvido em 26/08/2026**: as três de produção e as
  duas de desenvolvimento têm teto.

- **`ConfirmadorSustentado` e `RastreadorAlerta` implementam a mesma janela de tempo**, um
  sobre `bool` e outro sobre `Status`. Duplicação consciente: unificar é mexer em código de
  outra spec que funciona, e a regra do projeto manda perguntar antes de refatorar.
- **Texto de interface mora em três lugares agora:** `recursos.py` (textos de recurso),
  `ui/app.py` (os avisos do interruptor de inicialização) e `sistema/uptime.py` ("Ligado
  há"). A regra escrita diz "origem única em `recursos.py`", e o teste que a guarda cobre só
  os textos de recurso. Decidir se a regra passa a dizer "textos de recurso" ou se essas
  frases migram.
- **`_criar_rodape` em `ui/app.py` tem 41 linhas** — são quatro construções de widget em
  sequência. Em compensação o `__init__` caiu de 35 para 20, com `_preparar_janela`,
  `_criar_cards` e `_criar_rodape` extraídos.
- **Três funções em `hardware/pdh.py` passam de 20 linhas** (`_abrir` 30, `ler` 23,
  `__init__` 22). Ficam assim porque a spec 6 importa `pdh.py` **sem editar**, e quebrar as
  funções agora mudaria a superfície que ela vai consumir.

Verificado e limpo: nenhum `print()`, nenhum `except Exception`, nenhum `import *`, nenhum
uso de async.

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
