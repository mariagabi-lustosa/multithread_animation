#include <stdio.h>
#include <string.h>
#include <semaphore.h>
#include <pthread.h>
#include <stdlib.h> // t
#include <time.h>   // t
#include <unistd.h> // t

#define NUM_HACKERS 12 // teste
#define NUM_SERFS 12   // teste
#define BOAT_CAPACITY 4
#define MIXED_GROUP_SIZE (BOAT_CAPACITY / 2)

int hackers = 0; // number of hackers wainting to board
int serfs = 0; // number of serfs wainting to board

sem_t mutex;
sem_t hackerQueue;
sem_t serfQueue;
pthread_barrier_t barrier;


void board(const char *type, int id) {

    printf("EMBARCOU:%s:%d\n", type, id);
    fflush(stdout);
}

void rowBoat(const char *captain_type, int id) {
    
    printf("REMOU:%s:%d\n", captain_type, id);
    fflush(stdout);
}
void signal_queue(sem_t *queue, int count) {
    for (int i = 0; i < count; i++) {
        sem_post(queue);
    }
}


void *hacker_routine(void *arg) {
    int id = *(int *)arg;

    int isCaptain = 0; // flag to indicate if this hacker is the captain

    sem_wait(&mutex);
    hackers++;
    printf("CHEGOU:HACKER:%d\n", id);
    fflush(stdout);
    usleep(800000);
    if (hackers == BOAT_CAPACITY) {
        hackers -= BOAT_CAPACITY;
        signal_queue(&hackerQueue, BOAT_CAPACITY); // signal BOAT_CAPACITY hackers to board
        isCaptain = 1; // set captain flag
    } else if (hackers >= MIXED_GROUP_SIZE && serfs >= MIXED_GROUP_SIZE) {
        hackers -= MIXED_GROUP_SIZE;
        serfs -= MIXED_GROUP_SIZE;
        signal_queue(&hackerQueue, MIXED_GROUP_SIZE); // signal MIXED_GROUP_SIZE hackers to board
        signal_queue(&serfQueue, MIXED_GROUP_SIZE); // signal MIXED_GROUP_SIZE serfs to board
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
    printf("CHEGOU:SERF:%d\n", id);  
    fflush(stdout);
    usleep(800000);
    if (serfs == BOAT_CAPACITY) {
        serfs -= BOAT_CAPACITY;
        signal_queue(&serfQueue, BOAT_CAPACITY); // signal BOAT_CAPACITY serfs to board
        isCaptain = 1; // set captain flag
    } else if (hackers >= MIXED_GROUP_SIZE && serfs >= MIXED_GROUP_SIZE) {
        hackers -= MIXED_GROUP_SIZE;
        serfs -= MIXED_GROUP_SIZE;
        signal_queue(&hackerQueue, MIXED_GROUP_SIZE); // signal MIXED_GROUP_SIZE hackers to board
        signal_queue(&serfQueue, MIXED_GROUP_SIZE); // signal MIXED_GROUP_SIZE serfs to board
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

    // verify if the number of hackers and serfs is a multiple of the boat capacity
    if (NUM_HACKERS % MIXED_GROUP_SIZE != 0 || NUM_SERFS % MIXED_GROUP_SIZE != 0 || (NUM_HACKERS + NUM_SERFS) % BOAT_CAPACITY != 0) {
        fprintf(stderr, "Numbers of hackers and serfs must be even, and their total must be a multiple of %d.\n", BOAT_CAPACITY);
        return 1;
    }

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

    
    srand(time(NULL)); //  gerador aleatório 

    int hackers_created = 0;
    int serfs_created = 0;
    int total_threads = NUM_HACKERS + NUM_SERFS;
// adc ju
    for (int i = 0; i < total_threads; i++) {
        // decide aleatoriamente  se cria hacker ou serf, respeitando o numero no define
        if ((rand() % 2 == 0 && hackers_created < NUM_HACKERS) || serfs_created == NUM_SERFS) {
            hacker_ids[hackers_created] = hackers_created + 1;
            error = pthread_create(&hacker_thread[hackers_created], NULL, hacker_routine, &hacker_ids[hackers_created]);
            if (error != 0) {
                fprintf(stderr, "pthread_create hacker_thread[%d]: %s\n", hacker_ids[hackers_created], strerror(error));
                return 1;
            }
            hackers_created++;
        } else {
            serf_ids[serfs_created] = serfs_created + 1;
            error = pthread_create(&serf_thread[serfs_created], NULL, serf_routine, &serf_ids[serfs_created]);
            if (error != 0) {
                fprintf(stderr, "pthread_create serf_thread[%d]: %s\n", serf_ids[serfs_created], strerror(error));
                return 1;
            }
            serfs_created++;
        }

        // Dá uma pausa de 2 segundos entre cada pessoa que chega na margem
        usleep(2000000); 
    }
    // === O SEU CÓDIGO CONTINUA DAQUI PARA BAIXO COM OS LOOPS DE PTHREAD_JOIN ===
    for (int i = 0; i < NUM_HACKERS; i++) {
        error = pthread_join(hacker_thread[i], NULL);
        if (error != 0) {
            fprintf(stderr, "pthread_join hacker_thread[%d]: %s\n", hacker_ids[i], strerror(error));
            return 1;
        }
    }

    for (int i = 0; i < NUM_SERFS; i++) {
        error = pthread_join(serf_thread[i], NULL);
        if (error != 0) {
            fprintf(stderr, "pthread_join serf_thread[%d]: %s\n", serf_ids[i], strerror(error));
            return 1;
        }
    }

    printf("Finish - %d:%d%d\n", NUM_HACKERS, NUM_SERFS);
    fflush(stdout); //sincroniza E/S

    int exit_status = 0;

    // destroy semaphores and barrier
    error = pthread_barrier_destroy(&barrier);
    if (error != 0) {
        fprintf(stderr, "pthread_barrier_destroy: %s\n", strerror(error));
        exit_status = 1;
    }
    error = sem_destroy(&serfQueue);
    if (error == -1) {
        perror("sem_destroy serfQueue");
        exit_status = 1;
    }
    error = sem_destroy(&hackerQueue);
    if (error == -1) {
        perror("sem_destroy hackerQueue");
        exit_status = 1;
    }
    error = sem_destroy(&mutex);
    if (error == -1) {
        perror("sem_destroy mutex");
        exit_status = 1;
    }

    return exit_status;
}