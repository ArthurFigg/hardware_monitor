# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto segue [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- O aviso de sobrecarga agora diz qual programa está consumindo a máquina, com o
  percentual — em vez de só apontar que algo está pesado

### Corrigido
- O aviso de temperatura crítica falava em "sobrecarga de memória" e mandava fechar
  aplicativos; agora fala de temperatura e manda verificar a ventilação
- O cartão de Disco parou de sugerir fechar programas para resolver falta de espaço,
  e passou a ter textos próprios

## [1.0.0] — 2026-08-25

### Adicionado
- Monitor com quatro cartões: CPU, RAM, Disco e Temperatura estimada
- Sistema de semáforo (Normal, Atenção, Alerta) com textos sem jargão
- Notificação do sistema quando um recurso entra em alerta
- Modo claro e modo escuro, com botão para alternar
- Valor numérico em todos os cartões
