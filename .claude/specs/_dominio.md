# Domínio — Monitor de Hardware Minimalista

> Gerado por /dominio em 2026-08-25. Lido automaticamente pelo /spec antes de gerar
> qualquer spec de feature.

## Entidades

| Entidade | O que é |
|---|---|
| **Recurso** | Algo da máquina que é vigiado: CPU, RAM, Disco, Temperatura e, a partir da spec 5, a placa de vídeo. Hoje aparece espalhado como texto solto (`"cpu"`, `"ram"`) nos dicionários do `app.py`. |
| **Leitura** | O valor de um recurso num instante: 74%, ~66°C. É o `DadosHardware` de hoje. |
| **Status** | O veredito do semáforo sobre uma leitura: Normal, Atenção, Alerta. Já existe no código com esse nome. |
| **Limite** | O número que separa um status do seguinte: 60%, 85%, 65°C. Hoje vive como constante solta (`LIMITE_ATENCAO`, `LIMITE_ALERTA`, `LIMITE_TEMP_*`). |
| **Episódio de alerta** | O acontecimento: o recurso ficou acima do limite por tempo suficiente, foi confirmado pelo `RastreadorAlerta` e disparou notificação. Tem começo e fim. |
| **Programa** | Um processo que está consumindo recurso, nomeado na notificação a partir da spec 1 ("chrome.exe está usando 78% da CPU"). |
| **Disco** | Existe separado de Recurso porque tem o que os outros não têm: modelo, tamanho, saúde, e há mais de um na máquina. |

### O que deliberadamente NÃO é entidade

- **Temperatura** — não é medida independente, é o percentual de CPU convertido por
  `estimar_temperatura()`. É uma **Leitura derivada**. Tratá-la como entidade própria
  esconderia que ela não carrega informação nova (ver a nota sobre alinhamento de limites
  em "Thresholds", no CLAUDE.md).
- **Semáforo** e **Cartão** — são peças de tela, não domínio.

## Glossário de termos

| Usar sempre | Evitar | Motivo |
|---|---|---|
| **recurso** | indicador, métrica | "recurso" é o que a máquina tem e o app vigia; os outros são jargão de monitoramento |
| **limite** | threshold, limiar | O código já usa `LIMITE_ATENCAO`, e a regra do projeto é código em português. "threshold" só sobreviveu como título de seção no CLAUDE.md |
| **notificação** | alerta, aviso, popup | "alerta" já é um status; usar a mesma palavra para o balão do Windows confunde os dois |
| **episódio de alerta** | alerta (para o acontecimento) | Separa o estado agora (`Status.ALERTA`) do acontecimento com começo e fim, que é o que o `RastreadorAlerta` controla |
| **processo** (no código) | app, task | `psutil` devolve processo — é o termo exato da ferramenta |
| **programa** (na interface) | processo, app, aplicativo | O usuário não-técnico entende "programa". A separação código/interface é proposital |
| **está usando** | culpado, causando, responsável | O app **nomeia** quem consome, não acusa. O processo mais pesado costuma ser o que o usuário quer rodando — um jogo, um editor de vídeo |
| **temperatura estimada** | temperatura | É derivada do % de CPU, não medida. "temperatura" seca sugere sensor real |
| **redução de velocidade por calor** | throttling | Jargão é proibido nos textos da interface. "throttling" só em nota técnica |
| **saúde do disco** | S.M.A.R.T. | Mesmo motivo |
| **cartão** | card | Código já usa `CartaoRecurso`, e a regra é português |
| **uso da placa de vídeo** (interface) | GPU | "GPU" pode ficar no código; na tela o público precisa da palavra inteira |

Os dois que mais evitam confusão real são **limite** e **episódio de alerta**. Os demais
são consistência de vocabulário.

## Bounded Contexts

**Contexto único** — todo o projeto é um domínio coeso.

Os três módulos (`hardware`, `ui`, `notifications`) compartilham o mesmo vocabulário: um
"recurso" significa a mesma coisa no coletor, no cartão e na notificação. Nenhuma parte
existiria sozinha — a notificação sem a coleta não tem o que notificar.

Verificado contra o que vem pela frente:

- As 6 specs da v2 não trazem vocabulário novo. Trazem mais recursos (placa de vídeo) e
  mais sinais sobre os mesmos recursos (calor, saúde do disco).
- O projeto seguinte (histórico) traz palavras novas — amostra, período, resumo — mas elas
  **somam** ao vocabulário em vez de conflitar: uma amostra é uma leitura guardada, um
  resumo fala dos mesmos episódios de alerta. Ninguém precisa redefinir "recurso" para
  trabalhar no histórico.

Separação só valeria se algo redefinisse as palavras — por exemplo, monitorar máquinas de
outras pessoas pela rede, onde "recurso" passaria a precisar de dono.
