# multithread_animation
This project was developed as part of the MC504 course at Unicamp

## Creating a Env to install the pygames
```
python3 -m venv ~/multithread_animation/

source bin/activate
```
## To install:
```
pip install pygame

sudo apt update && sudo apt install python3-pygame
```
## How to compile and run
```
gcc -Wall -Wextra -pthread river_crossing.c -o river_crossing
./river_crossing river_crossing.c

```
