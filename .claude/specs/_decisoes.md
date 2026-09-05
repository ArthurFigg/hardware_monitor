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

## A notificação continua na biblioteca atual, e o clique é no ícone

**Contexto:** a biblioteca de notificação dispara o aviso e esquece — não há como saber se
alguém clicou. Em agosto de 2026 isso foi lido como impedimento para o resumo de uso, que
seria aberto clicando na notificação, e a decisão registrada aqui mandava trocar a
biblioteca por chamada própria ao Windows.
**Decisão (revista em 05/09/2026):** a biblioteca fica. A premissa caiu — **o clique no
ícone da bandeja já abre a janela desde a spec 5**, então o caminho que o resumo precisava
já existe: a notificação avisa, a pessoa clica no ícone ao lado do relógio, a tela abre.
**Verificado no `pystray` 0.19.5 instalado:** ele tem `notify()` e usa o mesmo
`Shell_NotifyIcon` que se pensava escrever à mão, mas **também não trata clique no balão** —
`NIN_BALLOONUSERCLICK` nem está definido em `_util/win32.py`, só `WM_LBUTTONUP` e
`WM_RBUTTONUP`, que são cliques no ícone. Trocar não compraria o clique.
**Descartado:** escrever `Shell_NotifyIcon` à mão. Reescreveria código que funciona, e
notificação saindo pela bandeja morreria junto com ela — que pode não subir, e o projeto já
trata esse caso ("Sem bandeja no ar, fechar volta a encerrar").
**Custo aceito:** um clique a mais, no ícone em vez de no aviso.

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

## O CI roda em Windows — a tentativa de rodar em Linux falhou

**Contexto:** o app depende de coisas que só existem no Windows, e o runner gratuito e rápido
é Linux. A aposta registrada aqui era que, como toda fronteira com o sistema é mockada, a
suite rodaria em qualquer lugar.
**Decisão (corrigida em 05/09/2026):** o runner é `windows-latest`. A aposta não se sustentou
e o CI ficou vermelho de 27/08 a 05/09/2026 sem que ninguém olhasse — as v2.0.0 e v2.1.0
foram lançadas assim. Mock não alcança duas coisas que não são teste: **`hardware/pdh.py` faz
`from ctypes import wintypes` no topo**, que só existe no Windows, então o módulo nem carrega;
e **os testes de UI criam um root CTk de verdade**, que precisa de tela. Em `windows-latest` os
392 passam.
**Descartado:** manter Linux e pular o que depende do Windows — esvaziaria a suíte.
**Custo aceito:** runner Windows é mais lento que o Linux. A regra de mockar fronteira continua
valendo por si; ela só nunca serviu para tornar a suíte portátil, que era a leitura errada
registrada aqui.

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



## A tela pede texto já resolvido, nunca decide qual texto usar

**Contexto:** um recurso pode ter mais de uma redação para o mesmo status, porque a causa
muda o conselho — disco em Alerta por falta de espaço manda apagar arquivo, disco em Alerta
por desgaste manda fazer cópia, e trocar os dois dá conselho que não resolve nada. O cartão
recebia só o status e escolhia o texto por conta própria, o que na prática significava
escolher sempre a primeira redação.
**Decisão:** o cartão chama funções que já receberam a leitura e devolvem texto pronto —
descrição, valor formatado e linha extra. Quem decide qual redação vale é a descrição do
recurso, a partir dos dados; a tela só exibe o que voltou.
**Descartado:** passar a causa para o cartão junto do status. Funciona, mas espalha a regra:
cada componente novo precisaria saber que existe causa e lembrar de repassá-la.
**Custo aceito:** as funções que a tela recebe têm assinatura `(status, valor)` mesmo quando
o recurso ignora o valor, e um recurso que não declara variante nenhuma paga um desvio
inútil. Em troca, acrescentar redação nova não exige tocar em nenhum componente de tela.


## Contador do Windows é aberto uma vez e lido com a primeira amostra descartada

**Contexto:** os contadores de desempenho do Windows respondem por uma consulta que precisa
ser aberta antes de ler. Abrir uma por leitura custaria caro num ciclo de um segundo, e os
contadores de taxa — os que medem velocidade, uso, transferência — calculam a diferença entre
duas amostras em vez de devolver um número pronto.
**Decisão:** a consulta é aberta na primeira leitura e mantida pelo resto da execução, e a
primeira leitura de cada contador é jogada fora. A amostra de abertura fica a microssegundos
da primeira leitura, e a diferença entre elas dá um valor sem sentido — medido: 43% num
processador que estava em 107%. Não há como distinguir esse valor de uma queda real.
**Descartado:** ler e fechar a cada ciclo, que evitaria guardar estado e pagaria o custo de
abertura sessenta vezes por minuto.
**Custo aceito:** o primeiro valor de qualquer contador novo demora um ciclo a mais para
aparecer, e o módulo guarda estado entre chamadas.

## Relógio de condição sustentada anda na coleta, nunca em quem lê os dados

**Contexto:** avisos que só valem depois de a condição se manter por alguns segundos precisam
de alguém contando o tempo. O lugar tentador é a função que monta o dado para a tela, porque
é onde a informação aparece.
**Decisão:** a contagem avança dentro da coleta, que roda uma vez por ciclo por construção.
Quem lê os dados recebe a resposta já decidida e não mexe em relógio nenhum.
**Descartado:** contar dentro da função que extrai o valor para a tela. Funciona enquanto
houver um consumidor só; no segundo — um ícone de bandeja que também consulta o estado — o
relógio passa a andar duas vezes por ciclo e a janela encolhe pela metade, sem erro nem
teste vermelho.
**Custo aceito:** o objeto de dados carrega um campo já decidido em vez de só medições
cruas, e quem lê não consegue recalcular a janela com outro tempo.


## Ação que a pessoa pediu nunca falha em silêncio, nos dois sentidos

**Contexto:** a regra geral do projeto é que leitura que falha esconde a si mesma — cartão
some, linha some, e o app segue funcionando. Isso vale para o que o app foi buscar sozinho.
**Decisão:** quando a operação foi **pedida pela pessoa** — um interruptor, um botão —,
falhar em silêncio não é opção. O controle volta para o estado que o sistema de fato tem, e
uma linha explica por quê. E vale nos dois sentidos: ligar que não ligou e desligar que não
desligou são igualmente mentira, sendo o segundo pior, porque o efeito indesejado continua
acontecendo e a pessoa descobre pela presença dele.
**Descartado:** reverter o controle sem texto. Pareceria defeito do próprio app — "cliquei e
não marcou" — e a pessoa tentaria de novo pelo resto da vida.
**Custo aceito:** cada ação reversível precisa de duas frases, uma por sentido, e de um lugar
na tela para exibi-las.

## Caminho de executável é resolvido em execução, nunca escrito no código

**Contexto:** o app grava no sistema operacional um comando que o inicia — e esse comando
precisa funcionar na máquina de quem instalou, não na de quem desenvolveu.
**Decisão:** o caminho sai do interpretador em uso no momento, com dois ramos: rodando do
código-fonte, aponta para o interpretador sem console mais o script de entrada; rodando
empacotado, aponta para o próprio executável. Há teste que varre o fonte atrás de caminho de
máquina escrito à mão.
**Descartado:** gravar o caminho durante o desenvolvimento e ajustar depois. Funciona na
máquina de quem escreveu e em nenhuma outra, e o erro só aparece no computador de terceiros.
**Custo aceito:** o código carrega os dois ramos e um deles nunca roda em desenvolvimento,
então precisa de teste próprio para não apodrecer sem ninguém notar.


## O que a tela mostra e o que o app decide são coisas separadas

**Contexto:** um cartão que deixa a pessoa escolher qual fatia dos dados olhar — um disco
entre vários, um núcleo entre vários — é útil. Mas o mesmo cartão costuma ser a fonte do
estado que outras partes consomem: a notificação, o ícone de bandeja, o resumo.
**Decisão:** a decisão sai sempre da leitura inteira; o que a tela exibe é um recorte dela,
escolhido por quem olha. O recorte também não pode aparecer mais grave do que a decisão já
confirmada, para que janelas de confirmação por tempo valham para a tela também. E quando o
recorte exibido esconde algo pior, o cartão diz o que está escondido e como chegar lá.
**Descartado:** deixar o cartão ser a fonte do estado. É o caminho curto e cria um defeito
silencioso: escolher a fatia saudável desliga o aviso da fatia problemática, e nada na tela
denuncia isso.
**Custo aceito:** dois status por cartão em vez de um — o que foi decidido e o que está
sendo mostrado —, e o código precisa deixar claro em cada ponto qual dos dois está em jogo.


## Recurso de sistema operacional sobe pelo ponto de entrada, nunca por construtor

**Contexto:** algumas coisas que o app usa não são objetos comuns — registram algo no
sistema operacional e sobem uma thread própria: ícone de bandeja, atalho global de teclado,
servidor local. Criar o objeto é barato; ligá-lo não é.
**Decisão:** o construtor apenas monta o objeto; quem liga é o ponto de entrada do programa,
por chamada explícita. E o objeto distingue "a biblioteca existe" de "está no ar" — decisões
de comportamento dependem da segunda, não da primeira.
**Descartado:** ligar no construtor, que é conveniente e parece natural. O preço aparece nos
testes: cada objeto construído registra algo de verdade no sistema, com uma thread por
instância, e a suite trava sem dizer por quê.
**Custo aceito:** o ponto de entrada precisa lembrar de fazer a chamada, e há um teste
existindo só para garantir que ninguém devolva a chamada para o construtor.
