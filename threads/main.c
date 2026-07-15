#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include "river_crossing.h"

int main(void) {
    if (NUM_HACKERS % MIXED_GROUP_SIZE != 0 || NUM_SERFS % MIXED_GROUP_SIZE != 0 || (NUM_HACKERS + NUM_SERFS) % BOAT_CAPACITY != 0) {
        fprintf(stderr, "Numbers of hackers and serfs must be even, and their total must be a multiple of %d.\n", BOAT_CAPACITY);
        return 1;
    }

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

    pthread_t hacker_thread[NUM_HACKERS];
    pthread_t serf_thread[NUM_SERFS];
    PassengerArgs hacker_args[NUM_HACKERS];
    PassengerArgs serf_args[NUM_SERFS];

    srand(time(NULL));

    int hackers_created = 0;
    int serfs_created = 0;
    int total_threads = NUM_HACKERS + NUM_SERFS;

    for (int i = 0; i < total_threads; i++) {
        if ((rand() % 2 == 0 && hackers_created < NUM_HACKERS) || serfs_created == NUM_SERFS) {
            hacker_args[hackers_created] = (PassengerArgs){ hackers_created + 1, ROLE_HACKER };
            error = pthread_create(&hacker_thread[hackers_created], NULL, passenger_routine, &hacker_args[hackers_created]);
            if (error != 0) {
                fprintf(stderr, "pthread_create hacker_thread[%d]: %s\n", hacker_args[hackers_created].id, strerror(error));
                return 1;
            }
            hackers_created++;
        } else {
            serf_args[serfs_created] = (PassengerArgs){ serfs_created + 1, ROLE_SERF };
            error = pthread_create(&serf_thread[serfs_created], NULL, passenger_routine, &serf_args[serfs_created]);
            if (error != 0) {
                fprintf(stderr, "pthread_create serf_thread[%d]: %s\n", serf_args[serfs_created].id, strerror(error));
                return 1;
            }
            serfs_created++;
        }

        usleep(2000000);
    }

    for (int i = 0; i < NUM_HACKERS; i++) {
        error = pthread_join(hacker_thread[i], NULL);
        if (error != 0) {
            fprintf(stderr, "pthread_join hacker_thread[%d]: %s\n", hacker_args[i].id, strerror(error));
            return 1;
        }
    }

    for (int i = 0; i < NUM_SERFS; i++) {
        error = pthread_join(serf_thread[i], NULL);
        if (error != 0) {
            fprintf(stderr, "pthread_join serf_thread[%d]: %s\n", serf_args[i].id, strerror(error));
            return 1;
        }
    }

    printf("Final:%d:%d\n", NUM_HACKERS, NUM_SERFS);
    fflush(stdout);

    int exit_status = 0;

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
