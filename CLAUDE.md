## Projeto
Monitor de Hardware Minimalista — app desktop Python que traduz dados de CPU, RAM e Disco em indicadores visuais simples (sistema de semáforo) para usuários não-técnicos.

## Stack
- Python 3.14 (pythoncore-3.14-64 — instalação Windows Store, Tcl/Tk parcialmente disponível)
- psutil 7.2.2 — coleta de dados de hardware
- CustomTkinter 5.2.2 — interface gráfica moderna
- plyer 2.1.0 — notificações nativas do sistema operacional
- pytest 9.0.3 — testes
- uv — gerenciador de dependências (`uv run`, `uv add`)

## Estado atual — projeto completo e funcional

Todas as 5 etapas foram implementadas. Para rodar:

```
uv run main.py
```

Para rodar os testes (40 testes, todos passando):

```
uv run pytest -v
```

## Estrutura real do projeto

```
hardware_monitor/
├── hardware/
│   ├── __init__.py
│   ├── collector.py      — DadosHardware dataclass + coletar()
│   └── thresholds.py     — Status enum, classificar(), descricao(), RastreadorAlerta
├── ui/
│   ├── __init__.py
│   ├── app.py            — AplicativoMonitor(CTkFrame): orquestra coleta, cards e notificações
│   └── components/
│       ├── __init__.py
│       ├── semaphore.py  — Semaforo(CTkFrame): círculo colorido por status
│       └── cards.py      — CartaoRecurso(CTkFrame): semáforo + título + descrição
├── notifications/
│   ├── __init__.py
│   └── manager.py        — GerenciadorNotificacoes: dispara notificação uma vez por período de alerta
├── tests/
│   ├── hardware/
│   │   ├── test_collector.py   — 4 testes (mock psutil)
│   │   └── test_thresholds.py  — 16 testes (limites, textos, RastreadorAlerta com mock de time)
│   ├── ui/
│   │   ├── conftest.py         — fixture raiz (CTk, session-scoped)
│   │   ├── test_app.py         — 4 testes (monitor usa fixture raiz)
│   │   ├── test_cards.py       — 5 testes
│   │   └── test_semaphore.py   — 5 testes
│   └── notifications/
│       └── test_manager.py     — 5 testes (mock plyer)
├── main.py               — cria CTk root, instancia AplicativoMonitor, chama mainloop()
├── pyproject.toml
└── CLAUDE.md
```

## Decisões arquiteturais importantes

- `AplicativoMonitor` é `CTkFrame`, não `CTk` — o root é criado em `main.py` e passado como `master`. Isso permite que os testes compartilhem um único root Tcl/Tk (Python 3.14 não suporta múltiplos roots no mesmo processo).
- Fixture `raiz` em `conftest.py` é `scope="session"` pelo mesmo motivo — um único CTk para toda a suite.
- Thread de coleta usa `coletar()` com `interval=1` (bloqueia 1s) + loop contínuo. A UI puxa os dados a cada 100ms via `after()`.
- `RastreadorAlerta` em `thresholds.py` (não em `app.py`) porque é regra de negócio: confirma ALERTA só após 5s contínuos acima de 85%.
- `GerenciadorNotificacoes` tem estado (`_notificado`) para não repetir a notificação enquanto o recurso permanece em ALERTA.
- `preview.py` na raiz é um script descartável de visualização — pode ser deletado.

## Thresholds (nunca alterar sem avisar)
- Normal: CPU e RAM entre 0% e 59%
- Atenção: CPU ou RAM entre 60% e 84%
- Alerta: CPU ou RAM acima de 85% por mais de 5 segundos

## Textos da interface (usar exatamente esses, sem alterar tom)
- Normal: "Desempenho estável. O sistema está operando com folga."
- Atenção: "Carga moderada. Vários processos estão exigindo recursos da máquina."
- Alerta: "Sobrecarga de memória/processamento. Feche aplicativos inativos para evitar travamentos."

## Regras fixas
- Coleta de dados sempre em thread separada, nunca na thread principal
- Nunca misturar lógica de hardware com lógica de UI
- Notificações só disparam no estado Alerta, silenciosas, somem sozinhas
- Todo módulo novo precisa de arquivo pytest junto
- Sem emojis ou tom de assistente animado nos textos da interface

## UI/UX
- Estilo minimalista, sem bordas pesadas ou gráficos de linha
- Suporte a Light Mode e Dark Mode com botão toggle
- Foco em indicadores visuais, não em números puros

## Melhorias possíveis (ainda não implementadas)
- Ícone na system tray com minimize para bandeja
- Histórico de uso em gráfico simples (últimos N minutos)
- Configuração de thresholds pelo usuário via arquivo `.env` ou UI
- Suporte a múltiplos discos (atualmente monitora só o disco raiz)
- Percentual numérico opcional nos cards (toggle de exibição)
- Auto-inicialização com o Windows (registro ou atalho na pasta Startup)
- Janela sempre visível (topmost) como opção

## Não fazer
- Não misturar responsabilidades num arquivo só
- Não criar lógica de negócio dentro de app.py
- Não disparar notificações em estados Normal ou Atenção
- Não usar jargões técnicos nos textos da interface
- Não criar segundo root CTk nos testes — usar a fixture `raiz` de conftest.py
