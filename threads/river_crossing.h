#ifndef RIVER_CROSSING_H
#define RIVER_CROSSING_H

#include <semaphore.h>
#include <pthread.h>

#define NUM_HACKERS 12
#define NUM_SERFS 12
#define BOAT_CAPACITY 4
#define MIXED_GROUP_SIZE (BOAT_CAPACITY / 2)

extern int hackers;
extern int serfs;

extern sem_t mutex;
extern sem_t hackerQueue;
extern sem_t serfQueue;
extern pthread_barrier_t barrier;

typedef enum {
    ROLE_HACKER,
    ROLE_SERF
} PassengerRole;

typedef struct {
    int id;
    PassengerRole role;
} PassengerArgs;

void board(const char *type, int id);
void rowBoat(const char *captain_type, int id);
void signal_queue(sem_t *queue, int count);
void *passenger_routine(void *arg);

#endif
