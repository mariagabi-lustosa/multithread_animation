<h1 align="center"> 
  🚣 Projeto de Animação Multithread: River Crossing 
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white" alt="C" />
  <img src="https://img.shields.io/badge/pthreads-blue?style=for-the-badge" alt="pthreads" />
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux" />
  <img src="https://www.pygame.org/docs/_images/pygame_logo.png" alt="Pygame" width = "120"
</p>

> Projeto de implementação de concorrência e sincronização de threads utilizando Semáforos e Mutexes, inspirado no livro *The Little Book of Semaphores* [1]. Desenvolvido para a disciplina de Sistemas Operacionais (MC504).

---

## 📋 Índice
- [Sobre o Projeto](#-sobre-o-projeto)
- [O Problema: Travessia do Rio](#-o-problema-travessia-do-rio)
- [Solução de Sincronização](#-solução-de-sincronização)
- [Visualizador e Animação](#-visualizador-e-animação)
- [Como Compilar e Executar](#-como-compilar-e-executar)
- [Entrega e Vídeo de Apresentação](#-entrega-e-vídeo-de-apresentação)

---

## 📖 Sobre o Projeto
O objetivo deste projeto é demonstrar o uso prático de mecanismos de sincronização (semáforos e *mutexs*) aplicados a múltiplas threads, acompanhado de uma animação gráfica que exibe o estado global da aplicação em tempo real [2]. A linguagem base para a lógica multithread é **C/C++** utilizando a biblioteca `pthreads` [3].

## 🚣 O Problema: Travessia do Rio (River Crossing)
O cenário ocorre próximo a Redmond, Washington, onde um barco a remo é compartilhado por hackers do sistema Linux e funcionários da Microsoft (chamados de *serfs*) para atravessar um rio [4]. 

**Regras estritas da travessia:**
1. **Capacidade:** O barco suporta exatamente quatro pessoas e só viaja cheio [4].
2. **Combinações proibidas:** Não é permitido colocar 1 hacker com 3 *serfs*, nem 1 *serf* com 3 hackers [4].
3. **Opções de Embarque:** As únicas combinações permitidas são:
   - 4 Hackers
   - 4 Serfs
   - 2 Hackers e 2 Serfs [4].
4. **Embarque:** Toda thread que entra no barco deve invocar a função `board`. As 4 threads devem embarcar antes que a próxima viagem comece [5].
5. **Partida:** Após o barco estar cheio, exatamente um dos passageiros deve assumir os remos invocando a função `rowBoat` [5].

## ⚙️ Solução de Sincronização
Para evitar *deadlocks* e garantir acesso concorrente seguro, utilizamos a biblioteca `pthread.h` e `semaphore.h` com os seguintes padrões:

* **Scoreboard (Placar):** Variáveis contadoras (`hackers` e `serfs`) protegidas por um **Mutex** avaliam se um grupo seguro pode ser formado [6].
* **Filas de Espera:** Semáforos `hackerQueue` e `serfQueue` pausam as threads até que uma combinação válida esteja pronta [6].
* **Barreira (Barrier):** Uma estrutura de barreira exige que todos os 4 membros estejam a bordo antes que o "capitão" invoque o remo e libere o *mutex* para o embarque seguinte [6, 7].

## 🎬 Visualizador e Animação
A aplicação não se limita ao terminal textual. O progresso das threads e a formação das viagens são exibidos a partir de uma animação Realizado com a biblioteca Pygame.
* Interface gráfica animada indicando os personagens aguardando na margem e o barco em travessia.
* Estado global ilustrando a formação dos grupos e bloqueios de sincronização [8].
* Parâmetros editáveis (ex: aumentar o fluxo de hackers ou serfs) [9].

## 🚀 Compilação e Execução

### Criando uma Env para instalar a biblioteca Pygame (Opcional a criação da VM)
```
python3 -m venv ~/multithread_animation/

source bin/activate
```
### Instalando Pygame:
```
pip install pygame

sudo apt update && sudo apt install python3-pygame
```

### Como compilar o código do River Crossing
```
gcc -Wall -Wextra -pthread river_crossing.c -o river_crossing

```


### Rodando o código do River Crossing e a Animação
```
./river_crossing | python3 visualizer.py
```
