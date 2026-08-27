# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto segue [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- O aviso de sobrecarga agora diz qual programa está consumindo a máquina, com o
  percentual — em vez de só apontar que algo está pesado
- Aviso quando um disco começa a dar sinais de desgaste, com o nome do disco — o caso
  em que apagar arquivo não resolve e o que vale é fazer cópia dos arquivos
- O cartão de Disco passou a olhar todas as unidades fixas do computador, e não só a
  do sistema; unidades removíveis, de rede e a partição de recuperação ficam de fora.
  Ele abre no disco em pior situação e **troca de disco a cada clique**, avisando quando
  o disco que está fora da tela é o que precisa de atenção
- O cartão de Temperatura avisa quando o processador diminui a própria velocidade para
  não esquentar — sem mudar de cor nem notificar, porque não há o que fazer a respeito
- Ícone ao lado do relógio, colorido pelo estado geral da máquina; fechar a janela agora
  esconde o app ali em vez de encerrá-lo, e o menu do ícone tem Abrir e Sair
- Interruptor para abrir o app junto com o Windows, já minimizado e sem roubar a tela no
  boot; desmarcar desfaz, e se algo bloquear a mudança o app diz o que aconteceu
- O rodapé mostra há quanto tempo o computador está ligado

### Modificado
- O alerta de disco cheio passou a considerar também quanto espaço sobrou, e não só o
  percentual: um SSD pequeno em 93% avisa, um HD grande em 90% não incomoda
- O aviso de espaço acabando agora diz quanto restou e em qual unidade

### Corrigido
- O aviso de temperatura crítica falava em "sobrecarga de memória" e mandava fechar
  aplicativos; agora fala de temperatura e manda verificar a ventilação
- O cartão de Disco parou de sugerir fechar programas para resolver falta de espaço,
  e passou a ter textos próprios
- O cartão de Temperatura acendia amarelo antes do de CPU, dando impressão de máquina
  esquentando sem motivo; agora os dois avisam no mesmo ponto de carga

## [1.0.0] — 2026-08-25

### Adicionado
- Monitor com quatro cartões: CPU, RAM, Disco e Temperatura estimada
- Sistema de semáforo (Normal, Atenção, Alerta) com textos sem jargão
- Notificação do sistema quando um recurso entra em alerta
- Modo claro e modo escuro, com botão para alternar
- Valor numérico em todos os cartões
