# multithread_animation

River crossing problem with multithreading visualization. This project was developed as part of the MC504 course at Unicamp.

## Structure

```
threads/    - C implementation (river_crossing.c, river_crossing.h, main.c)
animation/  - Python visualizer (main.py, renderer.py, entity.py, config.py)
```

## Setup

Create and activate a virtual environment, then install pygame:

```bash
python3 -m venv ~/multithread_animation

# bash
source ~/multithread_animation/bin/activate

# fish
source ~/multithread_animation/bin/activate.fish

pip install pygame
```

## Compile

```bash
cd threads
gcc -Wall -Wextra -pthread main.c river_crossing.c -o river_crossing
```

## Run

```bash
./threads/river_crossing | ~/multithread_animation/bin/python3 animation/main.py
```
