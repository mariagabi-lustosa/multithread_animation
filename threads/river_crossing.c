#include <stdio.h>
#include <unistd.h>
#include "river_crossing.h"

int hackers = 0;
int serfs = 0;

sem_t mutex;
sem_t hackerQueue;
sem_t serfQueue;
pthread_barrier_t barrier;


// prints protocol events read by the python visualizer
void board(const char *type, int id) {
    printf("BOARDED:%s:%d\n", type, id);
    fflush(stdout);
}

void rowBoat(const char *captain_type, int id) {
    printf("ROWED:%s:%d\n", captain_type, id);
    fflush(stdout);
}

// releases count threads that were blocked waiting on this queue
void signal_queue(sem_t *queue, int count) {
    for (int i = 0; i < count; i++) {
        sem_post(queue);
    }
}


void *passenger_routine(void *arg) {
    PassengerArgs *args = (PassengerArgs *)arg;
    int id = args->id;
    PassengerRole role = args->role;

    const char *type = (role == ROLE_HACKER) ? "HACKER" : "SERF";
    int *own_count = (role == ROLE_HACKER) ? &hackers : &serfs;
    int *other_count = (role == ROLE_HACKER) ? &serfs : &hackers;
    sem_t *own_queue = (role == ROLE_HACKER) ? &hackerQueue : &serfQueue;
    sem_t *other_queue = (role == ROLE_HACKER) ? &serfQueue : &hackerQueue;

    int isCaptain = 0;

    // enters the scoreboard's critical section and announces arrival
    sem_wait(&mutex);
    (*own_count)++;
    printf("ARRIVED:%s:%d\n", type, id);
    fflush(stdout);
    usleep(800000);

    // checks whether a valid group can already be formed
    if (*own_count == BOAT_CAPACITY) {
        *own_count -= BOAT_CAPACITY;
        signal_queue(own_queue, BOAT_CAPACITY);
        isCaptain = 1;
    } else if (*own_count >= MIXED_GROUP_SIZE && *other_count >= MIXED_GROUP_SIZE) {
        *own_count   -= MIXED_GROUP_SIZE;
        *other_count -= MIXED_GROUP_SIZE;
        signal_queue(own_queue,   MIXED_GROUP_SIZE);
        signal_queue(other_queue, MIXED_GROUP_SIZE);
        isCaptain = 1;
    } else {
        // not enough passengers yet, release the mutex and wait to be signaled
        sem_post(&mutex);
    }

    // blocks until released by whoever formed the group, or by itself if it is the captain
    sem_wait(own_queue);
    board(type, id);
    // waits for the other 3 passengers to board before departing
    pthread_barrier_wait(&barrier);
    if (isCaptain) {
        rowBoat(type, id);
        sem_post(&mutex);
    }

    return NULL;
}
