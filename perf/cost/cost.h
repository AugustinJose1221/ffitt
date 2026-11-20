#ifndef COST_H
#define COST_H

#include <ffitt/core/real.h>

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

// WHAT THESE TESTS ARE FOR.
//
// The headers of this library say what things cost. movavg says its work does
// not follow the window and that an equal fir costs two hundred times as much
// at a window of 4096. resample says the filtering costs the output rate and
// not the input rate. correlate says the plain method wins below about 300
// samples. Those sentences are the reason a caller picks one function over
// another.
//
// Nothing held them. The benchmark beside this one MEASURES and PRINTS, thus a
// claim could stop being true and the table would still be printed and still
// be green. These tests measure the same things and then say whether the claim
// still stands, and the exit code says it too.
//
// WHY A CLAIM IS HELD LOOSELY AND NOT TIGHTLY.
//
// A time measured on one machine is not the time on another. The cache, the
// other work of the machine and the compiler all move it. Thus a claim of two
// hundred times is held at fifty times and a claim of sixty-four times is held
// at five. What is tested is the SHAPE of the cost, which is what the header
// promises a caller: that one way is far cheaper than the other, or that the
// cost does not follow a size. A margin that wide cannot be met by accident
// and cannot be missed by a busy machine.
//
// Every claim below was made to fail on purpose before it was kept, so that a
// test that cannot fail is not counted as a test that passed.

// The reading of the monotonic clock in seconds. A change of the time of day
// does not disturb it.
//
// A TIME IS A double HERE AND NEVER A real_t. Built for a float, real_t holds
// about 7 digits, and the clock counts seconds since 1970, which is already 10
// digits. Every reading then rounds to the same number and every measured time
// comes out as exactly zero. It was written with real_t first and every claim
// below reported not-a-number.
double cost_now(void);

// WHERE THE ANSWERS GO SO THAT THE COMPILER CANNOT THROW THE WORK AWAY.
//
// A measured statement whose answer nothing reads is work the compiler may
// remove, and a loop that was removed is measured as taking no time at all.
// Every measurement below adds its answer here.
extern volatile real_t cost_sink;

extern int claims_tested;
extern int claims_held;
extern int claims_broken;

// Measure a statement and give the time of its FASTEST run.
//
// The fastest run is the one least disturbed by the other work of the machine,
// because that other work can only make a run slower and never faster.
#define COST_MEASURE(seconds_out, repeat_count, statement)          \
    do                                                              \
    {                                                               \
        double cost_start;                                          \
        double cost_elapsed;                                        \
                                                                    \
        (seconds_out) = 0.0;                                        \
                                                                    \
        for(uint32_t cost_repeat = 0u;                              \
            cost_repeat < (repeat_count);                           \
            cost_repeat++)                                          \
        {                                                           \
            cost_start = cost_now();                                \
            statement;                                              \
            cost_elapsed = cost_now() - cost_start;                 \
                                                                    \
            if((cost_repeat == 0u) || (cost_elapsed < (seconds_out))) \
            {                                                       \
                (seconds_out) = cost_elapsed;                        \
            }                                                       \
        }                                                           \
    }while(0)

// Keep the fastest of the measurements made so far, one round at a time.
//
// THE TWO SIDES OF A CLAIM ARE MEASURED IN TURN, AND NOT ONE AFTER THE OTHER.
//
// Every claim is a ratio of two times. Each time was once the fastest of seven
// runs, and the seven runs of one side were all made before the seven runs of
// the other. The fastest of seven removes a short disturbance inside one side.
// It cannot remove one that lasts through all seven runs of one side and not
// of the other: a neighbour on the same machine that is busy for a few
// seconds, or the clock of the processor changing between the two. Each side
// then took its fastest run under its own conditions, and the ratio carried
// the difference.
//
// That broke a claim on the build machine and nowhere else. The plain filter
// ran twice as slowly for all seven of its runs, and a ratio that measures
// 2.24 was reported as 1.05. Issue #95 holds the record.
//
// Thus each module now makes ONE run of each of its measurements per round,
// and calls this for each of them, for as many rounds as it once made runs. A
// disturbance that lasts falls on every side alike, and a change of clock is
// shared by every side rather than set against one. The work is the same as
// before; only the order has changed.
//
// Give the round, counted from 0. The first round keeps what it measures,
// whatever it is.
void cost_keep_fastest(double* fastest, double measured, uint32_t round);

// Say that the measured ratio must be at least as large as the claim asks.
// Use it for "far cheaper than" and "so many times as much".
void cost_claim_at_least(const char* module, const char* claim,
                         double measured, double least_allowed);

// Say that the measured ratio must be no larger than the claim asks.
// Use it for "the cost does not follow the size".
void cost_claim_at_most(const char* module, const char* claim,
                        double measured, double largest_allowed);

// Write the head of the report.
void cost_report_header(void);

// Write the foot of the report and the tally.
void cost_report_summary(void);

// A number between -0.5 and 0.5, from the same stream at every run.
real_t cost_random_value(void);

void run_ringbuf_cost_tests(void);
void run_resample_cost_tests(void);
void run_correlate_cost_tests(void);
void run_movavg_cost_tests(void);
void run_goertzel_cost_tests(void);
void run_convolve_cost_tests(void);

#endif//COST_H
