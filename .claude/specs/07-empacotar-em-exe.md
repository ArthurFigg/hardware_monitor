# Empacotar em .exe

**Ordem:** 7 de 7
**Depende de:** 04-abrir-com-o-windows-e-rodape (o registro aponta para este executável),
05-icone-na-bandeja (`pystray` e `Pillow` entram no que será empacotado)
**Score:** 2
**Revisão:** aprovada

## O que faz

O app vira um executável único, que roda em qualquer Windows sem Python instalado — sem o
qual ninguém além do autor consegue usá-lo.

## Comportamento

### O formato

- O build gera **um único `.exe`**. A pessoa baixa um arquivo e clica.
- O executável abre **sem janela de terminal**.
- O executável tem **ícone próprio** (`.ico`), que hoje não existe no projeto e será criado
  nesta spec.
- A partida do arquivo único leva de 2 a 5 segundos, porque ele se descompacta numa pasta
  temporária a cada abertura. Isso foi aceito: o app abre junto com o Windows, e durante o
  boot tudo já está lento — ninguém está esperando por ele.

### Medidas obrigatórias contra falso positivo de antivírus

O app faz duas coisas que somam risco heurístico: se descompacta sozinho (arquivo único) e
escreve na chave de inicialização do Windows (spec 4). Num executável sem assinatura digital,
isso é o retrato do que antivírus procura. As medidas abaixo são **obrigatórias no build**,
não opcionais:

- **Sem compressão UPX.** Executável comprimido com UPX é um dos padrões mais marcados, porque
  é o que malware usa para se esconder. O build precisa desabilitar isso explicitamente — o
  PyInstaller usa UPX sozinho quando o encontra instalado.
- **Com identificação embutida.** O `.exe` carrega nome do produto, autor, versão e descrição.
  Executável anônimo é tratado como suspeito por heurística, e a identificação também aparece
  nas propriedades do arquivo para quem clica com o botão direito.

A favor do app, e conta na avaliação: ele **não pede administrador** e **não acessa a
internet** — os dois comportamentos que mais pesam contra um executável desconhecido.

### O que continua acontecendo, e não tem como evitar agora

- Na primeira execução, o Windows exibe o aviso do SmartScreen ("O Windows protegeu o seu
  computador"), com "Não executar" em destaque. A pessoa precisa clicar em "Mais informações"
  e depois em "Executar assim mesmo".
- Isso acontece com **qualquer** executável sem assinatura digital, arquivo único ou pasta.
  Foi aceito por ser uma vez só.
- A solução definitiva é assinatura digital — ver "Decisões tomadas".

### Onde os dados ficam

- O executável **nunca** grava ao lado de si mesmo. Tudo que o app guardar vai para
  `%LOCALAPPDATA%`, como o CLAUDE.md já determina.
- Isso vale principalmente para o projeto seguinte (histórico), mas precisa estar correto
  desde o primeiro build: uma pasta temporária que se apaga a cada execução é o pior lugar
  possível para guardar dados.

### Caminho da inicialização

- Quando o app está empacotado, a entrada do registro criada pela spec 4 aponta para **este
  `.exe`**, não para o `pythonw.exe` do ambiente de desenvolvimento.
- O app precisa se reconhecer empacotado em tempo de execução para resolver o caminho certo.

### Plano B, com gatilho definido

- Se, no teste com o Defender ativo, o executável for **bloqueado ou colocado em quarentena**,
  o formato muda para pasta compactada em `.zip` — que reduz bastante o risco de quarentena,
  embora não elimine o aviso do SmartScreen.
- Este é o único critério para mudar de formato. Lentidão na partida **não** é motivo.

## Critérios verificáveis

- [ ] `uv run pytest -v` continua passando — esta spec não muda comportamento nenhum
- [ ] O build gera um único `.exe` e o comando de build está documentado
- [ ] O `.exe` abre sem janela de terminal
- [ ] O `.exe` exibe nome, autor, versão e descrição nas propriedades do arquivo
- [ ] O build não usa compressão UPX — verificável no arquivo de configuração do build
- [ ] O `.exe` roda numa máquina **sem Python instalado** — verificação manual, e é o único
      teste que prova que o empacotamento cumpriu seu objetivo
- [ ] O `.exe` não é bloqueado nem colocado em quarentena com o Defender ativo — verificação
      manual; se falhar, aciona o plano B
- [ ] Com o app empacotado, marcar o interruptor de inicialização escreve o caminho do `.exe`
      no registro, não o do ambiente de desenvolvimento

## Módulos afetados

- Arquivo de build do PyInstaller — **novo**. Define arquivo único, sem terminal, sem UPX,
  com ícone e com identificação; inclui os arquivos de tema do CustomTkinter, que é o que
  quebra o empacotamento quando esquecido.
- Arquivo de identificação de versão — **novo**. Nome do produto, autor, versão, descrição.
- `assets/icone.ico` — **novo**. Ícone do executável.
- `main.py` — passa a aceitar o argumento `--minimizado` que a entrada do registro envia.
  **A detecção de "estou empacotado" NÃO é desta spec:** ela mora em
  `sistema/inicializacao.py`, criada pela spec 4, que já cobre os dois ramos com teste.
  Esta spec apenas **verifica** que o ramo empacotado funciona de verdade. Antes, as duas
  reivindicavam a mesma detecção e nenhuma a definia.
- `pyproject.toml` — acrescenta o PyInstaller como dependência de **desenvolvimento**, não de
  produção.
- Documentação do processo de release: como gerar o `.exe` e o passo de enviar o arquivo para
  a Microsoft analisar.

## Não mexer

- **Nenhum comportamento do app.** Esta spec só empacota o que já existe. Se algo precisar
  mudar em `hardware/`, `ui/` ou `notifications/` para o empacotamento funcionar, isso é sinal
  de que alguma spec anterior deixou um caminho fixo onde não devia — corrigir lá, não aqui.
- Todos os módulos das specs 1 a 6.
- Os limites, textos e regras de qualquer recurso.
- O formato de pasta — só entra se o gatilho do plano B for acionado.

## Decisões tomadas

- **Arquivo único, não pasta** → escolha do usuário, com dois motivos que se sustentam: é mais
  fácil para quem recebe, e a partida lenta não incomoda porque o app abre junto com o
  Windows, quando tudo já está lento. O contra-argumento (risco de antivírus) foi tratado com
  medidas, não com mudança de formato.
- **O aviso do SmartScreen foi aceito** → é uma vez só, na primeira execução. O usuário
  considerou aceitável. Registrado o risco que fica: o público-alvo do app é justamente quem
  hesita diante de um aviso de segurança do Windows; se a adoção travar aí, a assinatura
  digital passa de "depois" para "necessária".
- **Sem UPX e com identificação embutida são obrigatórios** → são configuração de build, custo
  zero, e atacam justamente o que faz a heurística marcar o arquivo.
- **Enviar o executável para análise da Microsoft entra como passo de release** → é gratuito e
  eficaz, mas vale só para aquele arquivo exato: cada versão nova precisa ser enviada de novo.
  Por isso é passo de release documentado, não etapa de build.
- **Assinatura digital fica registrada como o caminho definitivo** → é o que resolve o
  SmartScreen de verdade. Certificado comercial é caro, mas projeto de código aberto tem
  caminho barato ou gratuito, e este já está público no GitHub. Não é para agora; é para
  quando o app começar a circular.
- **Plano B com gatilho** → só bloqueio ou quarentena no teste com Defender muda o formato
  para pasta. Lentidão na partida não é motivo, porque já foi aceita.
- Aplicadas sem perguntar, por já estarem no CLAUDE.md: nenhum caminho da máquina do autor;
  dados em `%LOCALAPPDATA%`, nunca ao lado do executável; os arquivos de tema do CustomTkinter
  precisam ser incluídos à mão.

## Impacto no CLAUDE.md

- **Estado atual** → acrescentar como gerar o executável, ao lado de como rodar e como testar.
- **Stack** → acrescentar o PyInstaller como dependência de desenvolvimento.
- **Distribuição** → acrescentar o formato escolhido (arquivo único), as medidas obrigatórias
  de build, o passo de release de enviar para análise, e o gatilho do plano B.
- **Estrutura real do projeto** → acrescentar o arquivo de build, o de identificação de versão
  e `assets/icone.ico`.
- **Melhorias — ver `aprovados.txt`** → marcar a spec 7 como especificada; com ela, todas as 7
  specs da v2 estão especificadas e o ciclo está pronto para o `/spec-review`.
