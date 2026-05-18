# Hardware Monitor

Aplicativo desktop para monitoramento em tempo real de CPU, RAM e disco,
com interface gráfica moderna e notificações de sistema quando o uso
ultrapassa limites configuráveis.

## Sobre

Projeto em desenvolvimento que monitora os recursos do computador em uma
thread separada e atualiza a interface sem travar a aplicação. Quando o
uso de um recurso se mantém em nível crítico por mais de 5 segundos,
uma notificação nativa do sistema operacional é disparada.

## Tecnologias

- Python 3.12+
- CustomTkinter (interface gráfica moderna)
- psutil (coleta de dados de hardware)
- plyer (notificações nativas do SO)
- pytest (testes automatizados)

## Estrutura do projeto
hardware_monitor/
├── hardware/         # coleta de dados e classificação de status
├── notifications/    # gerenciamento de notificações do sistema
├── ui/               # interface gráfica e componentes
│   └── components/
└── tests/            # testes por camada (hardware, notifications, ui)

## Funcionalidades

- Monitoramento em tempo real de CPU, RAM e disco
- Três níveis de status: Normal, Atenção (>60%) e Alerta (>85%)
- Notificação nativa do SO ao detectar sobrecarga sustentada
- Alternância entre modo claro e escuro
- Coleta em thread separada para não travar a interface

## Como rodar

```bash
git clone https://github.com/ArthurFigg/hardware-monitor.git
cd hardware-monitor

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

pip install customtkinter psutil plyer

python main.py

# Rodar os testes:
pytest
```

## Status

🚧 Em desenvolvimento — funcionalidades básicas implementadas.

## Aprendizados

- Threading em Python para separar coleta de dados da interface gráfica
- Comunicação thread-safe com lock para evitar condições de corrida
- Arquitetura em camadas separando hardware, notificações e UI
- Testes organizados espelhando a estrutura do projeto
