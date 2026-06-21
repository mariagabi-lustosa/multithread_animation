#include <stdio.h>
#include <string.h>
#include <semaphore.h>
#include <pthread.h>

#define NUM_HACKERS 4
#define NUM_SERFS 4
#define BOAT_CAPACITY 4

int hackers = 0; // number of hackers wainting to board
int serfs = 0; // number of serfs wainting to board

sem_t mutex;
sem_t hackerQueue;
sem_t serfQueue;
pthread_barrier_t barrier;


void board(const char *type, int id) {
    printf("%s %d boarded the boat.\n", type, id);
}

void rowBoat(const char *captain_type, int id) {
    printf("%s %d is rowing the boat.\n", captain_type, id);
}


void *hacker_routine(void *arg) {
    int id = *(int *)arg;

    int isCaptain = 0; // flag to indicate if this hacker is the captain

    sem_wait(&mutex);
    hackers++;

    if (hackers == 4) {
        hackers -= 4;
        for (int i = 0; i < 4; i++) {
            sem_post(&hackerQueue); // signal 4 hackers to board
        }
        isCaptain = 1; // set captain flag
    } else if (hackers >= 2 && serfs >= 2) {
        hackers -= 2;
        serfs -= 2;
        for (int i = 0; i < 2; i++) {
            sem_post(&hackerQueue); // signal 2 hackers to board
            sem_post(&serfQueue); // signal 2 serfs to board
        }
        isCaptain = 1; // set captain flag
    } else {
        sem_post(&mutex);
    }

    
    sem_wait(&hackerQueue); // hacker waits to board
    board("Hacker", id);
    pthread_barrier_wait(&barrier);
    if (isCaptain) {
        rowBoat("Hacker", id);
        sem_post(&mutex); // captain releases the mutex
    }

    return NULL;
}


void *serf_routine(void *arg) {
    int id = *(int *)arg;

    int isCaptain = 0; // flag to indicate if this serf is the captain

    sem_wait(&mutex);
    serfs++;

    if (serfs == 4) {
        serfs -= 4;
        for (int i = 0; i < 4; i++) {
            sem_post(&serfQueue); // signal 4 serfs to board
        }
        isCaptain = 1; // set captain flag
    } else if (hackers >= 2 && serfs >= 2) {
        hackers -= 2;
        serfs -= 2;
        for (int i = 0; i < 2; i++) {
            sem_post(&hackerQueue); // signal 2 hackers to board
            sem_post(&serfQueue); // signal 2 serfs to board
        }
        isCaptain = 1; // set captain flag
    }
    else {
        sem_post(&mutex);
    }

    
    sem_wait(&serfQueue); // serf waits to board
    board("Serf", id);
    pthread_barrier_wait(&barrier);
    if (isCaptain) {
        rowBoat("Serf", id);
        sem_post(&mutex); // captain releases the mutex
    }

    return NULL;
}


int main(void) {
    int hacker_ids[NUM_HACKERS];
    int serf_ids[NUM_SERFS];

    // initialize semaphores and barrier
    if (sem_init(&mutex, 0, 1) == -1) {
        perror("sem_init mutex");
        return 1;
    }
    if (sem_init(&hackerQueue, 0, 0) == -1) {
        perror("sem_init hackerQueue");
        sem_destroy(&mutex);
        return 1;
    }
    if (sem_init(&serfQueue, 0, 0) == -1) {
        perror("sem_init serfQueue");
        sem_destroy(&hackerQueue);
        sem_destroy(&mutex);
        return 1;
    }
    int error = pthread_barrier_init(&barrier, NULL, BOAT_CAPACITY);    
    if (error != 0) {
        fprintf(stderr, "pthread_barrier_init: %s\n", strerror(error));
        sem_destroy(&serfQueue);
        sem_destroy(&hackerQueue);
        sem_destroy(&mutex);
        return 1;
    }

    // create threads for hackers and serfs
    pthread_t hacker_thread[NUM_HACKERS];
    pthread_t serf_thread[NUM_SERFS];

    for (int i = 0; i < NUM_HACKERS; i++) {
        hacker_ids[i] = i+1;
        pthread_create(&hacker_thread[i], NULL, hacker_routine, &hacker_ids[i]);    }

    for (int i = 0; i < NUM_SERFS; i++) {
        serf_ids[i] = i+1;
        pthread_create(&serf_thread[i], NULL, serf_routine, &serf_ids[i]);
    }

    for (int i = 0; i < NUM_HACKERS; i++) {
        pthread_join(hacker_thread[i], NULL);
    }

    for (int i = 0; i < NUM_SERFS; i++) {
        pthread_join(serf_thread[i], NULL);
    }

    // destroy semaphores and barrier
    pthread_barrier_destroy(&barrier);
    sem_destroy(&serfQueue);
    sem_destroy(&hackerQueue);
    sem_destroy(&mutex);

    return 0;
}