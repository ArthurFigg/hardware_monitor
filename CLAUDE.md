## Próxima sessão — começar por aqui

> **Sessão pausada em 05/09/2026.** A próxima ação é uma só e está abaixo.

## ► Rodar `/spec-review`

As três specs do projeto novo estão escritas e **nenhuma foi revisada** — todas nascem com
`**Revisão:** pendente`, e a regra do projeto é que spec pendente não é implementada. O
`/spec-review` lê as três juntas, procura conflito e dependência e propõe a ordem.

| Spec | O que faz | Score |
|---|---|---|
| `08-historico-persistente` | grava; nada aparece na tela | 5 |
| `09a-leitura-do-periodo` | lê o período e diz se o resumo é devido; sem tela | 4 |
| `09b-tela-de-resumo` | avisa e mostra | 5 |

Elas foram cortadas assim porque juntas passavam do limite de tamanho da skill. As duas de
cima são consumidas **sem edição** pelas de baixo — o mesmo arranjo de `pdh.py` entre as
specs 3 e 6.

Depois do review, implementar na ordem com `/implementar`, uma por vez, com `pytest`
passando antes de avançar.

---

**A v2.1.0 está publicada e verificada; a distribuição está encerrada por decisão.** O
Release traz o `MonitorDeHardware.exe` (21,3 MB) e o `.sha256`, o CI está verde e o
executável foi provado num Windows limpo.

**O projeto em curso é o novo: histórico persistente e resumo das últimas N horas** (itens
`C1` e `C3` do `aprovados.txt`). A triagem de 25/08/2026 já fixou a gravação — SQLite da
biblioteca padrão, em `%LOCALAPPDATA%`, uma média por minuto, 90 dias de retenção; medido em
5,1 MB para os 90 dias. **Quatro pontos foram decididos em 05/09/2026 e vencem o que o
`aprovados.txt` dizia antes:**

1. **O tempo contado é de PC ligado**, não de app aberto.
2. **O N é fixo, não ajustável** — "ajustável" contrariava a seção Configuração, e o
   argumento é o mesmo dos limiares.
3. **O plyer fica, e não se escreve `Shell_NotifyIcon` à mão.** A triagem mandava trocar
   porque o plyer não detecta clique na notificação, mas isso só importaria se o clique
   fosse no balão — **o clique no ícone da bandeja já abre a janela desde a spec 5**.
   Verificado no `pystray` instalado: ele tem `notify()` e usa o mesmo mecanismo, mas
   também não trata clique no balão, então trocar não compraria nada; e notificação pela
   bandeja morreria junto com ela, que hoje pode não subir.
4. **A segunda tela é só o resumo.** O diagnóstico da máquina sai deste projeto e vira o
   seguinte — ele não usa o histórico para nada, e essa é a prova de que são separados.

O que foi feito em 05/09/2026:

- [x] ~~**Publicar a v2.1.0**~~ — feito em 05/09/2026.
- [x] ~~**Deixar o CI verde**~~ — feito em 05/09/2026. Ver "Ressalva sobre o CI".
- [x] ~~**Rodar o `.exe` baixado do Release num Windows sem Python instalado.**~~ — feito
      em 05/09/2026, no Windows Sandbox. Ver "Prova em Windows limpo".

### Guardado por decisão em 05/09/2026 — não é pendência

Os três itens abaixo **saíram da fila**. O executável abre e roda, que era o que importava;
o que resta é reputação, não funcionamento. Só voltam se o gatilho aparecer.

- **SmartScreen.** O arquivo em `Downloads` já está marcado como baixado
  (`Zone.Identifier` com `ZoneId=3`), então basta clicar nele para ver o aviso. Ele
  aparecer é o **esperado** e já foi aceito: acontece com qualquer executável sem
  assinatura digital, e é uma vez só.
- **Verificação completa do Defender.** A varredura do arquivo já passou limpa em
  05/09/2026; o que falta é a completa, com o arquivo marcado. **Gatilho do plano B:** se
  algum dia o `.exe` for **bloqueado ou posto em quarentena** com o Defender ativo, o
  formato muda para pasta compactada em `.zip`. Lentidão na partida não aciona nada — já
  foi aceita.
- **Enviar o `.exe` para análise da Microsoft.** Gratuito e reduz o SmartScreen, mas vale
  só para aquele arquivo exato — cada versão nova pede envio novo. Fazer isso a cada
  release, antes de haver quem baixe, é trabalho recorrente sem retorno medido.

**O que faria isso voltar para a fila:** alguém relatar que não conseguiu abrir o programa,
ou que desistiu no aviso do Windows. Aí o problema deixa de ser hipótese e a assinatura
digital passa de "depois" para "necessária" — o risco já estava registrado em
"Distribuição".

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
- pystray 0.19.5 — ícone na bandeja do sistema
- Pillow 12.3.0 — desenha a imagem do ícone da bandeja
- pytest 9.0.3 — testes
- pyinstaller 6.22.2 — empacotamento em `.exe` (desenvolvimento)
- uv — gerenciador de dependências (`uv run`, `uv add`)

## Estado atual — v2.1.0 publicada; specs do projeto seguinte escritas e não revisadas

A v1 está funcional. Em 25/08/2026 foi feita a triagem de 30 ideias para a v2: 12 aprovadas, 11 adiadas, 7 descartadas. O plano vive em dois arquivos na raiz:
- `aprovados.txt` — o que fazer, agrupado em specs, com os achados técnicos de cada uma
- `ideias.txt` — histórico completo, incluindo o que foi recusado e por quê

A triagem falava em 6 specs; o `/spec` gerou **7** — a fila real está em `.claude/specs/`.
**As 7 specs da v2 estão concluídas** (26/08/2026). A spec 2 foi reaberta e revisada no
mesmo dia, para o cartão de Disco trocar de unidade por clique.

A v2.0.0 foi encerrada e marcada em 26/08/2026. Em 05/09/2026 o projeto foi reaberto para
resolver a distribuição — publicação pelo GitHub Actions e três defeitos que só aparecem na
máquina de quem baixa — e o resultado é a **v2.1.0, publicada, verificada e encerrada** no
mesmo dia.

Ainda em 05/09/2026, o projeto seguinte foi especificado: **histórico persistente e resumo
das últimas N horas**, em três specs (`08`, `09a`, `09b`), todas com revisão pendente.
Nenhuma linha de código dele existe. Ver a seção de abertura deste arquivo.

Para rodar:

```
uv run main.py
```

Para rodar os testes (392 testes, todos passando em ~7 s):

```
uv run pytest -v
```

Para gerar o executável distribuível:

```
uv run pyinstaller monitor.spec --noconfirm
```

Sai em `dist/MonitorDeHardware.exe`, arquivo único de ~20 MB. O `.exe` precisa estar
fechado antes de reconstruir — o Windows trava o arquivo em execução e o build falha.

**Isso é para conferir localmente. O executável que se distribui é o do Release**, gerado
pelo GitHub Actions — ver "Distribuição".

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
│                           por índice, com queda para o inglês. `Contador` lê um valor;
│                           `ContadorVetor` lê instâncias com curinga
│   ├── desempenho.py     — % Processor Performance + LeituraTemperatura e a regra de calor
│   ├── placa_video.py    — GPU Engine: agrega por placa e tipo de motor, pega o maior
│   └── thresholds.py     — Status enum, classificar(), classificar_temperatura(),
│                           estimar_temperatura(), descricao(), descricao_temperatura(),
│                           classificar_unidade(), classificar_disco(), mais_grave(),
│                           RastreadorAlerta
├── ui/
│   ├── __init__.py
│   ├── app.py            — AplicativoMonitor(CTkFrame): orquestra coleta, cards e notificações
│   ├── bandeja.py        — ícone na bandeja: cor pelo pior status, menu Abrir/Sair
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
│   │   ├── test_discos.py      — 33 testes (mock psutil e PowerShell)
│   │   ├── test_pdh.py         — 16 testes (pdh.dll mockada)
│   │   ├── test_placa_video.py — 21 testes (leitura PDH mockada)
│   │   ├── test_processos.py   — 8 testes (mock psutil)
│   │   └── test_thresholds.py  — 46 testes (limites, textos, temperatura, disco,
│   │                             calor, RastreadorAlerta)
│   ├── ui/
│   │   ├── conftest.py         — fixture raiz (CTk, session-scoped)
│   │   ├── test_app.py         — 82 testes
│   │   ├── test_bandeja.py     — 20 testes (pystray mockado)
│   │   ├── test_cards.py       — 18 testes
│   │   └── test_semaphore.py   — 5 testes
│   ├── notifications/
│   │   └── test_manager.py     — 13 testes (mock plyer)
│   ├── sistema/
│   │   ├── test_inicializacao.py   — 26 testes (winreg mockado)
│   │   ├── test_instancia_unica.py — 13 testes (kernel32 mockado)
│   │   ├── test_caminhos.py        — 6 testes (_MEIPASS simulado)
│   │   ├── test_estado.py          — 8 testes (pasta temporária)
│   │   └── test_uptime.py          — 6 testes
│   └── test_recursos.py        — 33 testes (textos, causas, origem única das frases)
├── sistema/
│   ├── __init__.py
│   ├── inicializacao.py  — entrada na chave Run do HKCU; caminho resolvido em execução,
│                           e corrigido sozinho quando o executável mudou de pasta
│   ├── instancia_unica.py — mutex nomeado do Windows: a segunda abertura mostra a janela
│                            da primeira e sai
│   ├── caminhos.py       — onde estão os arquivos que acompanham o app, empacotado ou não
│   ├── estado.py         — o pouco que o app lembra entre execuções, em %LOCALAPPDATA%
│   └── uptime.py         — "Ligado há 5h 23min" a partir dos segundos desde o boot
├── assets/
│   ├── icone.ico         — ícone do executável, 7 resoluções (16 a 256)
│   └── gerar_icone.py    — regenera o .ico; lê a cor do mesmo CORES do semáforo
├── monitor.spec          — build do PyInstaller: arquivo único, sem terminal, sem UPX
├── versao.txt            — identificação embutida no .exe (nome, autor, versão)
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
`_decisoes.md`. Há dois workflows: `.github/workflows/tests.yml` (testes, Linux) e
`.github/workflows/release.yml` (executável e Release, Windows).

`post-linkedin.txt` na raiz é anotação pessoal para a postagem, está no `.gitignore` e não
faz parte do projeto.

## Decisões arquiteturais importantes

- `AplicativoMonitor` é `CTkFrame`, não `CTk` — o root é criado em `main.py` e passado como `master`. Isso permite que os testes compartilhem um único root Tcl/Tk (Python 3.14 não suporta múltiplos roots no mesmo processo).
- Fixture `raiz` em `conftest.py` é `scope="session"` pelo mesmo motivo — um único CTk para toda a suite.
- Thread de coleta usa `coletar()` com `interval=1` (bloqueia 1s) + loop contínuo. A UI puxa os dados a cada 100ms via `after()`.
- `RastreadorAlerta` em `thresholds.py` (não em `app.py`) porque é regra de negócio: confirma ALERTA só após 5s contínuos acima do limite.
- `GerenciadorNotificacoes` tem estado (`_notificado`) para não repetir a notificação enquanto o recurso permanece em ALERTA.
- **`recursos.py` na raiz é a fonte única do que o app vigia e do que ele diz.** Cada `Recurso` carrega: função de classificação própria, textos de cartão e de notificação (com variantes por causa — o Disco tem duas redações de Alerta), se notifica, se varre processos, formato do valor e se o cartão pode sumir. `app.py` monta cartões, rastreadores e notificadores percorrendo essa coleção e **não conhece nenhum recurso por nome**. Acrescentar um recurso é uma entrada, não três.
- O **pior status** entre os recursos é calculado em `recursos.py`, nunca em `app.py`. Recurso indisponível fica de fora da conta e o cartão dele some da tela.
- Temperatura é **estimada** a partir do % de CPU (`estimar_temperatura(cpu)`): idle=35°C, carga máxima=85°C. Consequência a não esquecer: o card de Temperatura **não carrega informação independente** — é o % de CPU escrito em outra unidade. Por isso os pontos de corte dos dois ficam alinhados (ver Thresholds), e por isso o aviso de redução de velocidade por calor, entregue na spec 3, é o primeiro sinal **real** que esse card carrega — o único dado dele que não vem do percentual de CPU. Não usa WMI nem sensor real — leitura de sensor no Windows exige driver de kernel (admin) e não é viável sem dependência externa.
- `CartaoRecurso` aceita `descricao_fn` e `formatar_valor` para suportar textos e formatos diferentes por recurso sem duplicar o componente.
- **O Disco olha todas as unidades fixas, e o status do cartão é o pior entre elas.**
  Unidade removível, de rede, de CD e qualquer uma com menos de 10 GB de tamanho total
  ficam de fora — este último filtro existe pela partição de recuperação do Windows
  (~500 MB, sempre quase cheia), que sem ele deixaria o app em Alerta permanente. O
  cartão **abre** exibindo a unidade que decidiu o status, nomeada e com um contador:
  "D: — 100% (2/2)". **Clicar no cartão passa para a próxima unidade** e dá a volta no
  fim; o contador some quando há uma unidade só, porque "(1/1)" não revelaria nada. **A pior unidade
  é a de pior status, não a de maior percentual** — as duas regras podem apontar para
  discos diferentes (um SSD de sistema com 8 GB livres está em Alerta pela regra de
  espaço e perde no percentual para um HD em 94% que está só em Atenção), e ordenar pelo
  percentual faria o semáforo acender por um disco e o rótulo nomear outro.
- **O cartão de Disco é uma janela de visualização; as decisões vêm da leitura inteira.**
  O clique troca o que aparece — número, cor e texto, sempre do mesmo disco —, mas a
  notificação e o pior status continuam saindo da pior unidade. Sem essa separação,
  selecionar um disco saudável desligaria o aviso do disco cheio e deixaria o ícone da
  bandeja verde com um disco em alerta. Quando a unidade exibida não é a pior, a linha
  extra do cartão diz qual está pior e que dá para clicar.
- **O que o cartão exibe nunca passa do que o app confirmou** (`menos_grave`): assim a
  janela de 5 s do `RastreadorAlerta` vale também para a tela, e um recorte não aparece
  mais grave do que a decisão.
- **Clique de cartão é ligado em cada parte dele, não só no frame.** O Tk não propaga
  clique de filho para o pai — sem isso, clicar no número não faria nada e clicar na
  borda faria. O CustomTkinter esconde de `winfo_children()` o canvas onde desenha, e é
  nele que o `bind` acaba caindo: teste que só varre os filhos visíveis dá falso negativo.
- **A saúde é do disco físico e nunca é mapeada em unidade.** Um disco com várias
  partições faria o mapeamento errar, então a linha extra nomeia o disco. É relida a cada
  6 horas: desgaste evolui em semanas, a consulta custa ~3 s (abre um PowerShell), e o app
  vai viver na bandeja por semanas sem reiniciar (spec 4).
- **Consulta de saúde que falha devolve `None`, e `None` não é "todos saudáveis".** Tupla
  vazia é informação ("consultei, está tudo bem"); `None` é ausência dela. Os dois escondem
  a linha, mas só o segundo poderia virar alerta falso se fossem confundidos.
- **A regra de thread do Tkinter vale nas duas direções, e são regras diferentes.**
  Atualizar a cor do ícone **a partir da thread do Tkinter** é seguro e é assim que se faz.
  O contrário — a thread do `pystray` tocar widget — trava ou corrompe a interface em
  silêncio: o clique no ícone e o menu passam por `after(0, ...)`. `ui/bandeja.py` não
  conhece widget nenhum; recebe as ações prontas de quem o criou.
- **A thread de coleta também sobe pelo `main.py`, não no construtor** — mesma regra do
  ícone, e pelo mesmo motivo medido: janela construída não pode começar a ler a máquina só
  por existir.
- **O ícone da bandeja sobe pelo `main.py`, nunca no construtor da janela.** Subir no
  construtor faz toda janela criada — inclusive as dos testes — registrar um ícone de
  verdade no Windows, com uma thread de message loop por instância. Isso travou a suite
  uma vez; há teste que falha se alguém devolver a chamada para o construtor.
- **`disponivel` e `ativo` são coisas diferentes na bandeja:** a primeira diz que a
  biblioteca existe, a segunda que o ícone está no ar. Esconder a janela depende da
  segunda.
- **Laço agendado com `after()` para de mexer na tela assim que o app para.** Tanto a
  atualização dos cartões quanto a do rodapé checam isso **na entrada**, não só na hora de
  reagendar: sem essa checagem, um callback já agendado ainda dispara depois do fechamento e
  escreve em widget em destruição.
- **O contador de placa de vídeo tem três armadilhas, todas verificadas nesta máquina.**
  (1) Ele **não é traduzido**: `nome_por_indice` devolve `None` mesmo num Windows em
  português, então a queda para o nome em inglês é o caminho único, não precaução.
  (2) A função que lê o vetor devolve o código **como número negativo** no `ctypes` —
  `PDH_MORE_DATA` chega como -2147481646; sem `& 0xFFFFFFFF` nenhuma comparação casa e a
  leitura funcionando parece vazia. (3) Precisa de **duas coletas** antes do primeiro valor.
- **O uso da placa é o maior motor, agrupando por placa física E tipo.** Somar as 336
  instâncias daria acima de 100%; somar só por tipo juntaria o motor 3D da placa integrada
  com o da dedicada — e **esta máquina tem duas** (`0x00010327_phys_0` e
  `0x00011E36_phys_0`), então o exagero é real, não hipotético. Processos que dividem o
  mesmo motor somam entre si; placas diferentes nunca.
- **`RastreadorAlerta` confirma qualquer status, não só o ALERTA.** O padrão continua sendo
  vigiar ALERTA e cair para ATENCAO enquanto espera; a placa de vídeo pede o mesmo para o
  ATENCAO dela, porque nunca chega a Alerta e sem isso o cartão piscaria amarelo a cada pico
  de um segundo.
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
- **O ícone do arquivo e o ícone da janela são coisas separadas.** O `icon=` do
  `monitor.spec` só decide como o `.exe` aparece no Explorer; a janela aberta usa o que o
  Tk tiver, e sem `iconbitmap` isso é o ícone do próprio Tk. Por isso o `.ico` também
  entra no `datas` e é lido **em execução** — e ícone que falta esconde a si mesmo, como
  qualquer outra leitura.
- **Caminho de arquivo acompanhante passa por `sistema/caminhos.py`, nunca é montado à
  mão.** Empacotado em arquivo único, o app roda de uma pasta temporária diferente a cada
  abertura, anunciada em `sys._MEIPASS`; caminho relativo à pasta do projeto só existe na
  máquina de quem desenvolve.
- **Uma instância por vez, e a segunda mostra a janela da primeira.** O app entra na chave
  `Run`, então ele já está rodando quando a pessoa clica no executável — sem isso são dois
  processos, dois ícones na bandeja e notificação em dobro. Sair calado seria pior que o
  problema: a pessoa clicou e nada aconteceu. Mutex nomeado decide quem é a primeira;
  evento nomeado carrega o pedido, e a thread que espera nele entrega pelo `after(0, ...)`
  — mesma regra do ícone da bandeja.
- **A correção do caminho no registro só roda empacotada.** Ela existe porque o programa
  não tem instalador e pode ser arrastado para outra pasta depois de ligar o interruptor,
  o que o tiraria do boot em silêncio. Rodando pelo código ela fica desligada: um teste em
  desenvolvimento apontaria a chave `Run` para a pasta do projeto, roubando a entrada do
  programa que a pessoa de fato usa.
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

**Placa de vídeo — implementado na spec 6 em 26/08/2026.** Atenção **acima de 95%**
(`> 95`) sustentado por 5 segundos. **Nunca chega a Alerta.**

Não "corrigir" para 60/85 por consistência — a inconsistência é proposital. Placa em 100%
durante um jogo é o esperado; com os limites de CPU e RAM o cartão ficaria amarelo o jogo
inteiro e vermelho sem nada errado. O único caso em que o número significa algo para este
público é a placa no limite de forma sustentada, que explica o jogo engasgando e tem ação
clara: baixar a qualidade gráfica. Não há vermelho porque não há emergência nem ação urgente.

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
- **Cinco cartões:** CPU, RAM, Disco, Temperatura e Placa de vídeo.
- Valor numérico exibido em todos os cards: percentual (%) para CPU/RAM/Disco e Placa de
  vídeo, temperatura estimada (~°C) para Temperatura
- **Cartão que troca de conteúdo por clique mostra a mãozinha do cursor, e só quando há
  para onde ir.** Cursor de mão em cartão que não faz nada é promessa que a tela não
  cumpre — vale para o Disco numa máquina com uma unidade só.
- **Rodapé:** interruptor "Abrir junto com o Windows" à esquerda, botão de tema à direita, e
  abaixo a linha discreta de uptime da máquina ("Ligado há 5h 23min") — sem cor e sem
  semáforo, porque não existe uptime em alerta. Atualiza de minuto em minuto.
- O rodapé usa `grid`, não `pack`: a regra de packing do projeto (`side="right"` antes de
  qualquer `expand=True`) é fácil de violar sem perceber, e o `grid` não tem esse problema.

## Melhorias — ver `aprovados.txt`
A lista solta que existia aqui foi substituída pela triagem de 25/08/2026. Não reintroduzir itens aqui: `aprovados.txt` é a fila, `ideias.txt` é o histórico.

As 7 specs aprovadas, na ordem:
1. ~~Notificações que dizem qual recurso e qual programa~~ — **concluída em 2026-08-26**
2. ~~Card Disco com limiares e textos próprios, saúde do disco, múltiplos discos~~ — **concluída em 2026-08-26**, revisada no mesmo dia para trocar de unidade por clique
3. ~~Correção do limiar de Temperatura Atenção (60°C → 65°C) + aviso de redução de velocidade por calor (contador PDH do Windows)~~ — **concluída em 2026-08-26**
4. ~~Abrir com o Windows e uptime no rodapé~~ — **concluída em 2026-08-26**
5. ~~Ícone na bandeja, com minimizar para lá~~ — **concluída em 2026-08-26**
6. ~~Cartão de placa de vídeo com uso real (usa o mecanismo da spec 3)~~ — **concluída em 2026-08-26**
7. ~~Empacotar em `.exe` (depende do caminho definido na spec 4)~~ — **concluída em 2026-08-26**

Depois delas, como projeto à parte: histórico persistente e resumo das últimas N horas.

**Leva seguinte, aberta em 05/09/2026** (também em `aprovados.txt`): `D3` — esconder o
cartão de placa de vídeo na máquina que não tem placa. Veio do teste no Windows Sandbox,
onde o cartão apareceu marcando 0% com a GPU desligada. **O critério não é "está em 0%"** —
placa de verdade ociosa também marca 0%, e esconder por valor trocaria um cartão inútil por
um que pisca. O caso novo é o contador abrir, listar instâncias e todas ficarem paradas em
zero; hoje o cartão já some nos outros dois (contador não abre, ou não lista nada). Falta
medir o que o contador lista num Windows real sem placa dedicada — sem esse dado, talvez a
resposta certa seja não fazer nada.

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

### Formato e build (spec 7, 26/08/2026)

**Quem gera o executável distribuído é o GitHub Actions, não esta máquina** (decidido em
05/09/2026). Empurrar a tag `vX.Y.Z` dispara `release.yml`, que compila no `windows-latest`
e publica o Release com o `.exe` e o hash SHA-256 anexados; as notas saem da seção do
CHANGELOG daquela versão. Motivo: gerando à mão, o arquivo publicado é o que alguém lembrou
de reconstruir, e "esqueci de rebuildar" não aparece em teste nenhum — aparece na máquina de
quem baixou, que é justamente quem não sabe diagnosticar computador.

O workflow **falha antes de compilar** se a versão não bater nos cinco pontos
(`pyproject.toml` mais os quatro campos de `versao.txt`) ou se `upx=False` e
`version="versao.txt"` tiverem saído do `monitor.spec`. As conferências são ancoradas no
começo da linha de propósito: as duas medidas também aparecem no comentário do topo do
arquivo, e sem âncora apagar a linha real e deixar o comentário passaria.

A tag da v2.0.0 foi criada antes do workflow existir, então ele também aceita disparo
manual: roda a partir da `main` e recebe a tag como parâmetro, porque o Actions lê o
arquivo do workflow a partir do ref escolhido.

**O CI não substitui o teste em máquina limpa:** o runner tem Python instalado e não tem
área de trabalho, então ele prova que o executável **compila**, nunca que ele **abre**.

**Arquivo único**, gerado por `monitor.spec`. O executável se descompacta em
`%TEMP%\_MEIxxxxx` a cada abertura — 38 MB extraídos, apagados na saída normal.
**Medido em 05/09/2026: 1,4 s até a janela aparecer**, com o arquivo já em cache; a
estimativa anterior de 2 a 5 s era pessimista, e a primeira abertura de todas é mais lenta
que as seguintes.

Duas consequências do formato, ambas conhecidas e aceitas:
- **Encerrar pelo Gerenciador de Tarefas deixa os 38 MB no temp**, uma pasta por vez. Só a
  saída limpa apaga. Não tem conserto dentro do formato de arquivo único; o Windows acaba
  recolhendo pela limpeza de disco.
- Programa de limpeza agressivo que apague `%TEMP%\_MEIxxxxx` **com o app aberto** o
  quebra no meio da execução.

**Três medidas do build são obrigatórias, não preferência.** O app soma dois sinais que
antivírus procura: se descompacta sozinho e escreve na chave `Run`. Num executável sem
assinatura digital, isso basta para ser marcado.

- **`upx=False`** — comprimir com UPX é um dos padrões mais marcados, porque é o que malware
  usa para se esconder. O PyInstaller liga o UPX sozinho quando o encontra instalado, então
  desligar precisa ser explícito. Conferir pelas seções PE: se aparecer `UPX0`/`UPX1`, está
  comprimido. Procurar a string "UPX" no binário **não serve** — ela aparece no bootloader
  mesmo sem compressão.
- **`version="versao.txt"`** — executável anônimo é tratado como suspeito por heurística.
- **Arquivos de tema do CustomTkinter no `datas`** — são JSON e PNG carregados em tempo de
  execução, e o PyInstaller não os encontra sozinho. Sem eles o `.exe` compila e quebra ao
  abrir a janela.

A favor do app: **não pede administrador** e **não acessa a internet**, os dois
comportamentos que mais pesam contra um executável desconhecido.

**Versão em três lugares:** `pyproject.toml`, as tuplas de `versao.txt` e as strings de
`versao.txt`. Mudar em dois e esquecer o terceiro faz o arquivo informar uma versão e o
repositório declarar outra.

**Passo de release:** enviar o `.exe` para análise da Microsoft. É gratuito e eficaz, mas
vale só para aquele arquivo exato — cada versão nova precisa ser enviada de novo.

**O aviso do SmartScreen continua aparecendo** na primeira execução, e acontece com qualquer
executável sem assinatura digital. Foi aceito por ser uma vez só. Risco registrado: o público
deste app é justamente quem hesita diante de um aviso de segurança do Windows; se a adoção
travar aí, a assinatura digital passa de "depois" para "necessária".

**Plano B, com gatilho único:** se o executável for **bloqueado ou posto em quarentena** com
o Defender ativo, o formato muda para pasta compactada em `.zip`. Lentidão na partida **não**
aciona o plano B — ela já foi aceita.

**Verificado empacotado nesta máquina em 05/09/2026:** a janela abre com o ícone do app na
barra de título, a bandeja registra o ícone (classe `SystemTrayIcon` presente), fechar a
janela esconde sem encerrar o processo, a versão embutida aparece como 2.1.0 nas
propriedades do arquivo, `--minimizado` abre a janela minimizada e invisível como a chave
`Run` espera, e a segunda abertura mostra a janela da primeira — inclusive quando ela está
minimizada — e sai sozinha.

Mais três conferências do mesmo dia:
- **Sem UPX, conferido pelas seções PE:** as 7 seções são `.text`, `.rdata`, `.data`,
  `.pdata`, `.fptable`, `.rsrc` e `.reloc` — nenhuma `UPX0`/`UPX1`. É assim que se
  confere; procurar a string "UPX" no binário não serve.
- **Varredura do Defender no arquivo, com proteção em tempo real ligada: nenhuma ameaça.**
  Isso **não** cobre o SmartScreen, que é reputação na nuvem disparada pelo Mark of the Web
  e depende de o arquivo ter sido baixado.
- **Nenhum dos 76 módulos carregados vem da instalação de Python nem do `.venv`.**
  `python314.dll` e `VCRUNTIME140.dll` saem de dentro do pacote. É a evidência mais forte
  possível nesta máquina de que o `.exe` não precisa de Python — mas não fecha o assunto:
  DLL carregada só depois (numa notificação, na consulta de disco) não apareceria aqui.

### Prova em Windows limpo (05/09/2026)

**O `.exe` do Release abre num Windows sem Python.** O teste rodou no **Windows Sandbox**,
que é recurso do próprio Windows 11 Pro — uma máquina limpa e descartável, sem instalar
nada. Ligar o recurso exige reiniciar uma vez; depois disso, abrir um arquivo `.wsb` que
mapeia uma pasta com o `.exe` e um script, mais outra pasta para o relatório sair. Não é
preciso um segundo computador, e a suposição contrária ficou escrita aqui por engano — o
item constou como "não dá para fazer na máquina de desenvolvimento".

**O script que produziu esta prova não foi guardado** (decidido em 05/09/2026). Repetir o
teste numa versão futura significa escrevê-lo de novo: ele copia o `.exe` para dentro,
procura Python de quatro formas, abre o programa, mede o tempo até a janela, lista de onde
vem cada DLL carregada e tira uma foto da tela. O caminho está descrito acima; o trabalho
é reescrever, não redescobrir.

Medido dentro do Sandbox (Windows 11 Enterprise build 26100), com o binário do Release
(SHA-256 `aae88aee…`, o mesmo publicado):

- **Sem Python de nenhuma forma:** os comandos `python`, `python3`, `py` e `pythonw` não
  existem, não há `HKLM\SOFTWARE\Python` nem `HKCU\SOFTWARE\Python`, não há pasta
  `C:\Python*` e não há `python*.dll` no `System32`. Quatro checagens porque uma só engana:
  na máquina de desenvolvimento o comando `python` também "não existe" (o que responde por
  ele é um atalho de 0 byte da Microsoft Store) e mesmo assim há cinco Pythons instalados.
- **A janela abriu em 1,4 s**, com ícone próprio, 370x647, e o ícone entrou na bandeja.
- **83 módulos carregados. Fora do `C:\Windows`, só seis** — e os seis saem de dentro do
  pacote (`_MEI…`): `python314.dll`, `python3.dll`, `tcl90.dll`, `tcl9tk90.dll`,
  `VCRUNTIME140.dll` e `VCRUNTIME140_1.dll`. Nada foi buscado numa instalação de Python,
  porque não havia nenhuma para buscar. Isso fecha a ressalva antiga de que uma DLL
  carregada tarde poderia não aparecer: aqui não haveria de onde ela vir.
- **Os cinco cartões leram a máquina** e nenhum quebrou: CPU 0%, RAM 45%, Disco C: 3%,
  Temperatura ~35°C, Placa de vídeo 0%. O contador de disco não mostrou "(n/n)", correto
  para uma máquina de uma unidade só.

**Observação, não defeito:** o Sandbox roda com a GPU desligada e o cartão de placa de vídeo
ainda assim apareceu, marcando 0% em verde. Ele não quebrou — que é a regra —, mas também
não sumiu. Vale decidir depois se cartão que só sabe dizer 0% deveria se esconder; num PC
sem placa dedicada de verdade o contador pode se comportar diferente do que se viu aqui.

**Ainda sem verificação:** uma verificação completa do Defender, com o arquivo **baixado
pelo navegador** e não com o de `dist/`, e o aviso do SmartScreen.

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

**Implementado na spec 5 em 26/08/2026:**
- Fechar a janela **esconde** para a bandeja; a coleta e as notificações continuam.
- **No primeiro fechamento a janela não some**: aparece o aviso "O monitor continua
  rodando. Clique no ícone ao lado do relógio para abrir de novo." Mensagem em janela
  escondida ninguém lê, então a janela fica até o fechamento seguinte. O "já mostrei" vive
  em `%LOCALAPPDATA%`, então vale para a instalação inteira, não para a execução. O aviso
  some quando a janela reaparece — é recado de uso único.
- Encerrar de verdade é pelo **Sair** no menu do ícone. Sem essa opção a pessoa ficaria sem
  jeito de fechar o app.
- **Sem bandeja no ar, fechar volta a encerrar.** App que não tem como ser reaberto não
  pode se esconder.

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
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest -v
```

**O runner é Windows, e a tentativa de rodar no Linux falhou — não repetir.** O CI nasceu
em `ubuntu-latest` apostando que a regra de mockar toda fronteira de sistema bastaria para a
suite rodar em qualquer lugar. Não bastou, e ficou vermelho de 27/08 a 05/09/2026 sem que
ninguém olhasse: as v2.0.0 e v2.1.0 foram lançadas assim. A aposta ignorava duas coisas que
não são teste e por isso nenhum mock alcança — **`hardware/pdh.py` faz `from ctypes import
wintypes` no topo**, que só existe no Windows, então o módulo nem carrega; e **os testes de
UI criam um root CTk de verdade**, que precisa de tela, e o runner Linux não tem uma.

A premissa que estava escrita aqui — "CI vermelho significa teste que não devia existir" —
era falsa: quem não roda no Linux é o código de produção, não o teste. Em `windows-latest`
os 392 passam. A regra de mockar fronteira continua valendo por si; ela só nunca serviu para
tornar a suite portátil.

## Qualidade — dívidas conhecidas (levantadas em 25/08/2026)
Achadas comparando o projeto com as regras do CLAUDE.md global. Nenhuma é urgente;
todas devem ser resolvidas na etapa de setup, antes da primeira spec.

- ~~`ruff` configurado mas não instalado~~ → **resolvido em 26/08/2026**: `ruff>=0.16.4,<0.17.0`
  entrou como dependência de desenvolvimento e rodou.
- **29 linhas passam de 88 caracteres** (medido em 05/09/2026; eram 30 no fim da v2, e os
  módulos novos da v2.1.0 não acrescentaram nenhuma). Delas, 3 são comentários e o resto são
  quase todas *strings* e docstrings — formatador não quebra nenhum dos dois. Vale saber
  por que o `ruff check` passa mesmo assim: a regra de linha longa
  (E501) **não está no conjunto padrão**, e o `line-length = 88` só orienta o formatador.
  Quem quiser tratar isso como erro precisa ligar a regra explicitamente.
- **Os construtores couberam.** Ao fim da v2, `ui/app.py.__init__` tem 26 linhas (era 44) e
  `ui/components/cards.py.__init__` tem 21 (era 35) — as extrações feitas ao longo das specs
  4, 5 e 6 absorveram o interruptor, a bandeja e o cartão de placa de vídeo sem inchar
  nenhum dos dois. Seguem pouco acima das 20 linhas de referência, ambos como sequências
  diretas de construção, sem ramificação.
- ~~Dependências sem teto de versão~~ → **resolvido em 26/08/2026**: as três de produção e as
  duas de desenvolvimento têm teto.

- **`ConfirmadorSustentado` e `RastreadorAlerta` implementam a mesma janela de tempo**, um
  sobre `bool` e outro sobre `Status`. Duplicação consciente: unificar é mexer em código de
  outra spec que funciona, e a regra do projeto manda perguntar antes de refatorar.
- ~~`tests/ui/test_app.py` domina o tempo da suite~~ → **resolvido em 26/08/2026**: de
  10min30s para ~8 s. A thread de coleta subia no construtor, então cada janela criada em
  teste começava a ler a máquina — e as threads que sobreviviam ao fim do teste chamavam
  `coletar()` **de verdade**, depois que os mocks saíam de cena: PowerShell do disco,
  contadores PDH e `cpu_percent` bloqueando 1 s, por teste. Agora quem sobe a coleta é o
  `main.py`, e há teste que falha se alguém devolver a chamada para o construtor. Cada teste sobe a thread de coleta real,
  que roda em laço apertado com o `coletar()` mockado até `_rodando` virar falso. Resolver
  é mexer na fixture e afeta todos os testes de UI — decidir separado.
- **Texto de interface mora em três lugares agora:** `recursos.py` (textos de recurso),
  `ui/app.py` (os avisos do interruptor de inicialização) e `sistema/uptime.py` ("Ligado
  há"). A regra escrita diz "origem única em `recursos.py`", e o teste que a guarda cobre só
  os textos de recurso. Decidir se a regra passa a dizer "textos de recurso" ou se essas
  frases migram.
- ~~`_criar_rodape` com 41 linhas~~ → **resolvido em 26/08/2026**: virou `_criar_controles`
  mais `_criar_linha_de_recado`, e `_organizar` ganhou `_organizar_rodape`. Restam em
  `ui/app.py` três funções entre 25 e 27 linhas (`__init__`, `_avancar_selecao`,
  `_atualizar_cards`), todas sequências diretas sem ramificação.
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

---
**Encerrado em:** 2026-08-26 (v2.0.0)
**Reaberto em:** 2026-09-05 para a v2.1.0 — publicação e três defeitos que só aparecem na
máquina de quem baixa: janela sem ícone próprio, duas instâncias ao mesmo tempo e a entrada
do boot apontando para o caminho antigo.
**Versão:** v2.1.0 — publicada, verificada e encerrada em 05/09/2026
**Testes:** 392 passando (em ~7 s, e verdes também no CI, que passou a rodar em Windows)
**Specs concluídas:** 7 de 7 da v2 (a spec 2 passou por uma revisão)
**Specs escritas e não revisadas:** 3 — `08`, `09a` e `09b`, do projeto de histórico
**Próxima ação:** `/spec-review` sobre as três
**Período:** 2026-05-17 a 2026-09-05
