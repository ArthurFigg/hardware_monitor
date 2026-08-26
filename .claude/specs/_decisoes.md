# Decisões transversais — Monitor de Hardware Minimalista

> Mantido pelas skills do fluxo conforme as decisões são tomadas. Lido pelo
> `/session-start` e destilado pelo `/readme` na seção "Decisões técnicas".

**Entra aqui** a decisão que restringe código de mais de uma spec.
**Não entra** decisão de uma spec só (fica na spec), nem regra que o CLAUDE.md
global já impõe — obedecer não é decidir.

Cada entrada se explica sozinha: quem nunca viu o projeto entende a decisão e o
motivo sem abrir outro arquivo.

## Informação que não vira semáforo não vira cartão

**Contexto:** a triagem de agosto de 2026 avaliou 8 candidatos a cartão novo numa tela que
tinha 4. Vários eram informação boa que não dava para pintar de verde, amarelo ou vermelho:
velocidade de rede em MB/s não tem limite que signifique algo (5 MB/s satura uma internet de
50 mega e é nada numa de 500), e "quantos programas abrem com o Windows" é um número parado
que muda uma vez por mês.
**Decisão:** só vira cartão o que tem limite com significado e muda de cor. O resto vira
linha discreta no rodapé, vai para a segunda tela, ou não entra.
**Descartado:** cartões de rede, de programas na inicialização, de número de processos
abertos e de memória em disco — todos adiados por este critério, não por falta de espaço.

## Toda leitura de hardware esconde a si mesma quando falha

**Contexto:** o app será distribuído. As leituras foram validadas numa máquina só — Windows
11 build 26200, em português, com placa dedicada. Em Windows mais antigo, em outro idioma ou
num PC sem placa, elas podem simplesmente não responder.
**Decisão:** leitura que falha some da tela — esconde a linha ou o cartão inteiro. Nunca
mostra erro, nunca derruba o app. Vale para saúde do disco, redução de velocidade por calor
e uso da placa de vídeo.

## Nada do app é gravado na pasta do app

**Contexto:** o app vai rodar na máquina de outras pessoas, onde a pasta do projeto não
existe. E na máquina do autor essa pasta fica dentro do OneDrive, que sincronizaria cada
gravação sem parar.
**Decisão:** tudo que o app grava vai para `%LOCALAPPDATA%`. Vale para o interruptor de
abrir com o Windows e para o histórico do projeto seguinte.
**Descartado:** gravar ao lado do executável, que é o caminho mais curto e quebra nos dois
cenários acima.

## A notificação nomeia quem está consumindo, nunca acusa

**Contexto:** o programa mais pesado da máquina normalmente é o que a pessoa quer rodando.
Num jogo pesado, o topo da lista é o jogo — dizer que ele é o culpado é acusar exatamente o
que ela foi usar.
**Decisão:** o texto diz "chrome.exe está usando 78% da CPU". Nunca "culpado", nunca "feche
o Chrome". Quando fizer sentido sugerir ação, a sugestão é fechar os outros programas, não o
mais pesado.
**Descartado:** botão no cartão para encerrar o processo mais pesado — além de propor fechar
o que a pessoa quer aberto, entrega uma arma para quem menos consegue julgar se aquele
processo pode morrer.

## Varrer processos só quando há alerta, nunca a cada ciclo

**Contexto:** medido em agosto de 2026 nesta máquina: varrer os 268 processos custa 163 ms.
Rodando a cada segundo, isso ocupa 16% de um núcleo continuamente. Um monitor que come 16%
de CPU para avisar que a CPU está alta é uma piada.
**Decisão:** a varredura roda sob demanda, no momento em que um recurso entra em alerta —
que é o único instante em que o nome do programa é usado. Custo vira 163 ms esporádicos.
**Descartado:** varrer junto com a coleta de cada segundo, que é o jeito óbvio e o caro.

## Contador do Windows se resolve por número, com queda para o nome em inglês

**Contexto:** os nomes dos contadores de desempenho do Windows são traduzidos por idioma.
"Processor Information" vira "Informações do Processador" em português — mas o contador de
placa de vídeo não é traduzido e continua em inglês na mesma máquina. Fixar o nome quebra o
app em qualquer Windows de idioma diferente.
**Decisão:** buscar o número do contador (que é igual em todo idioma) e traduzir para o nome
local; quando a tradução vier vazia, usar o nome em inglês.
**Descartado:** escrever o nome traduzido direto no código — funciona só na máquina de quem
escreveu.

## A notificação passa a sair do ícone da bandeja, não da biblioteca atual

**Contexto:** a biblioteca de notificação usada hoje dispara o aviso e esquece — não há como
saber se alguém clicou. O resumo de uso planejado depende justamente disso: notificação
curta que abre uma tela ao ser clicada.
**Decisão:** quando o ícone da bandeja existir, a notificação passa a sair dele, que detecta
o clique. O app deixa de depender da biblioteca atual para isso.
**Descartado:** manter a biblioteca e abrir mão do clique, o que mataria o resumo de uso.

## Python 3.14 fica, em vez de voltar para uma versão mais assentada

**Contexto:** a preferência geral é usar a penúltima versão estável, porque biblioteca costuma
demorar a suportar release novo — e este projeto ainda vai acrescentar quatro dependências.
**Decisão:** manter 3.14. Verificado em 26/08/2026 que `ruff`, `pystray`, `Pillow` e
`pyinstaller` resolvem para 3.14; o motivo da regra não se aplica aqui.
**Descartado:** voltar para 3.13 — mexeria num ambiente com 61 testes passando sem ganho, e a
arquitetura de testes existe por causa do 3.14 (ele não aceita dois roots Tcl/Tk no mesmo
processo, por isso a fixture de root é compartilhada pela suíte inteira).
**Custo aceito:** ao acrescentar dependência nova, conferir suporte a 3.14 antes — não é
garantido como seria numa versão mais antiga.

## O CI roda em Linux, mesmo o app sendo só para Windows

**Contexto:** o app depende de coisas que só existem no Windows — chave do registro, contadores
de desempenho, consulta de disco. O runner gratuito e rápido é Linux.
**Decisão:** rodar os testes em Linux mesmo assim. Isso só funciona porque toda fronteira com o
sistema é mockada, e é exatamente essa a regra de testes do projeto.
**Custo aceito:** nenhum teste pode tocar o Windows de verdade. Na prática isso vira uma trava
útil: CI vermelho por causa de chamada real ao sistema significa teste que não deveria existir.
O que não é testável assim (ícone da bandeja, superaquecimento físico, contador em outra
máquina) já está declarado como verificação manual.

## Um lugar só descreve cada recurso, e a tela não conhece recurso por nome

**Contexto:** o app vigia CPU, RAM, Disco e Temperatura, e vai ganhar mais. Antes, cada um
aparecia em três dicionários paralelos dentro da tela — um de rastreadores, um de
notificadores, um de cartões. Acrescentar um recurso exigia lembrar dos três, e esquecer um
não quebrava teste nenhum: a coisa só sumia da tela em silêncio.
**Decisão:** cada recurso é descrito uma vez, em `recursos.py` na raiz — com a própria função
de classificação, os textos de cartão e de notificação, se notifica, se varre processos, o
formato do valor e se o cartão pode sumir. A tela percorre essa coleção e não tem nome de
recurso escrito em lugar nenhum. Acrescentar recurso passa a ser uma entrada.
**Descartado:** manter os dicionários e acrescentar mais um a cada spec — mais barato agora e
pago quatro vezes depois.
**Custo aceito:** o arquivo fica na raiz, e não em `hardware/` nem em `ui/`, porque carrega
texto de interface e regra de classificação ao mesmo tempo. Quem procurar por camada não
acha de primeira.

