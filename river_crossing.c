#include <stdio.h>
#include <semaphore.h>
#include <pthread.h>

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


int main() {
    int hacker_ids[4];
    int serf_ids[4];

    // initialize semaphores and barrier
    sem_init(&mutex, 0, 1);
    sem_init(&hackerQueue, 0, 0);
    sem_init(&serfQueue, 0, 0);
    pthread_barrier_init(&barrier, NULL, 4); // barrier for 4 passengers

    // Create threads for hackers and serfs
    pthread_t hacker_thread[4];
    pthread_t serf_thread[4];

    for (int i = 0; i < 4; i++) {
        hacker_ids[i] = i+1;
        serf_ids[i] = i+1;
        pthread_create(&hacker_thread[i], NULL, hacker_routine, &hacker_ids[i]);
        pthread_create(&serf_thread[i], NULL, serf_routine, &serf_ids[i]);
    }

    for (int i = 0; i < 4; i++) {
        pthread_join(hacker_thread[i], NULL);
        pthread_join(serf_thread[i], NULL);
    }

    // Wait for threads to finish (not shown)

    // destroy semaphores and barrier
    sem_destroy(&mutex);
    sem_destroy(&hackerQueue);
    sem_destroy(&serfQueue);
    pthread_barrier_destroy(&barrier);

    return 0;
}