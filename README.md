Projeto de Animação Multithread: O Problema da Travessia do Rio (River Crossing)
📖 Sobre o Projeto
Este repositório contém a implementação do "Problema da Travessia do Rio" (River Crossing Problem), desenvolvido como parte da avaliação de Sistemas Operacionais
. O objetivo do projeto é demonstrar o uso prático de mecanismos de sincronização (semáforos e mutexes) aplicados a múltiplas threads, acompanhado de uma animação que exibe o estado global da aplicação em tempo real
.
🚣 O Problema da Travessia do Rio
O cenário se passa perto de Redmond, Washington, onde existe um barco a remo compartilhado por hackers do sistema Linux e por funcionários da Microsoft (chamados de serfs) para atravessar um rio
.
As regras para a travessia e sincronização das threads são estritas:
Capacidade do Barco: O barco suporta exatamente quatro pessoas; ele não sairá da margem com mais nem menos passageiros
.
Segurança e Convivência: Para garantir a segurança a bordo e evitar brigas, não é permitido colocar um hacker com três serfs, e nem um serf com três hackers
.
Combinações Permitidas: As únicas formações seguras para a viagem são grupos contendo quatro hackers, quatro serfs, ou um grupo misto contendo exatamente dois hackers e dois serfs
.
Embarque e Partida: À medida que cada thread entra no barco, ela deve invocar a função board
. Todas as quatro threads de um grupo devem obrigatoriamente embarcar antes que qualquer passageiro do próximo barco possa começar a entrar
.
O Capitão: Quando o barco estiver cheio, exatamente um dos quatro passageiros a bordo deve ser o responsável por remar, invocando a função rowBoat
.
⚙️ Detalhes da Implementação (Sincronização)
A lógica principal foi desenvolvida em C/C++ utilizando a biblioteca pthreads
. Para resolver as restrições de sincronização de forma livre de deadlocks e inanição (starvation), utilizamos os seguintes padrões baseados no livro The Little Book of Semaphores:
Padrão Scoreboard: Usamos duas variáveis contadoras (hackers e serfs) protegidas por um semáforo de exclusão mútua (mutex) para monitorar quem está esperando nas margens
.
Filas de Espera: Quando um passageiro chega e ainda não pode formar um grupo seguro, ele aguarda em seu respectivo semáforo de fila (hackerQueue ou serfQueue)
.
Padrão Barreira (Barrier): Utilizamos uma barreira para garantir que os 4 passageiros do grupo selecionado entrem no barco e confirmem o embarque antes do capitão remar e liberar o mutex para a próxima viagem
.
🎬 Animação e Visualização
Para não nos limitarmos a apenas mensagens de texto em um terminal, o projeto inclui um visualizador animado
. O estado de execução de cada thread é mapeado graficamente.
Na interface, você verá a margem do rio onde hackers e funcionários da Microsoft chegam e formam filas.
Assim que um grupo válido se forma (ex: 2 hackers e 2 serfs), a animação exibe o embarque e o barco atravessando a tela.
A animação permite que o usuário altere parâmetros de execução para observar diferentes comportamentos (ex: aumentar a taxa de chegada de apenas hackers)
.
🚀 Como Compilar e Executar
(Adicionar as instruções finais de compilação, como gcc -pthread ou a biblioteca gráfica escolhida, bem como o comando para iniciar a animação).
