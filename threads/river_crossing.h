#ifndef RIVER_CROSSING_H
#define RIVER_CROSSING_H

#include <semaphore.h>
#include <pthread.h>

#define NUM_HACKERS 12
#define NUM_SERFS 12
#define BOAT_CAPACITY 4
#define MIXED_GROUP_SIZE (BOAT_CAPACITY / 2)


/* scoreboard protected by the mutex (number of hackers and serfs waiting) */ 
extern int hackers;
extern int serfs;

/*
 * mutex protects the scoreboard,
 * queues release the chosen passengers,
 * barrier waits for the group to board
 */
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


/* Emits a BOARDED event to stdout for the visualizer */
void board(const char *type, int id);

/* Emits a ROWED event to stdout, signaling the boat has departed */
void rowBoat(const char *captain_type, int id);

/* Posts to a semaphore count times, releasing count waiting threads */
void signal_queue(sem_t *queue, int count);

/* Thread entry point for a passenger. Waits for a valid boarding group,
* boards the boat, and rows if elected captain */
void *passenger_routine(void *arg);

#endif
