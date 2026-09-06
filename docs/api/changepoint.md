# changepoint

This file comes from the comments in the headers. Do not change it by hand.
To make it again, give:

```bash
python3 scripts/api_doc.py
```

Saying when a reading has changed. Declared in `ffitt/detect/changepoint.h`.

[Back to the index](../API.md) | [How the detect modules work](../../ffitt/detect/README.md) | [How it works](../diagrams/detect/changepoint.html) ([preview](https://htmlpreview.github.io/?https://github.com/AugustinJose1221/ffitt/blob/development/docs/diagrams/detect/changepoint.html))

## Overview

Say when a reading has changed, as soon as it has.

A bearing runs a little warmer than it did. A pump draws a little more
current. A tank leaks slowly enough that any one reading looks ordinary. In
each of them the change is SMALLER THAN THE NOISE, thus no threshold on a
single sample can find it: a threshold low enough to catch the change fires
on the noise all day, and one high enough to be quiet never fires at all.

What finds it is that the change KEEPS HAPPENING and the noise does not. Add
up how far each sample stands from where it should be, and the noise wanders
about nothing while a change walks steadily away. The running sum is held at
nothing from below, so that a long quiet spell cannot build up credit that a
later change spends: what is measured is how far the reading has run since it
last looked ordinary, and not how far it has run since the beginning.

TWO SUMS AND NOT ONE. A rise and a fall usually mean different things -- a
bearing that warms is wearing, one that cools has lost its load -- thus they
are counted apart and the answer says which happened.

WHAT IT COSTS. This is not a way of seeing a change sooner than the numbers
allow. It is a way of trading: a smaller change can be found, and finding it
takes longer. The delay is roughly the threshold divided by half the smallest
change worth finding, in samples, and changepoint_delay_for gives it.

THE ONE WAY THIS FAILS QUIETLY: it is told what ordinary looks like, once,
and it believes that for ever. A reading whose ordinary level drifts of its
own accord walks away from a level that no longer means anything, and the
alarm that follows is about the drift. Where the level drifts, take it off
first with dcblock or detrend, and give this what is left.

## Method

The change is smaller than the noise, thus no threshold on one sample can
find it. What can find it is a running total that only ever grows when the
readings lean one way:

    S = max(0, S + (x[n] - mean - slack))

The slack is what a reading is allowed to be above the mean without counting.
While the readings are ordinary they fall above and below it, S is pushed down
as often as up, and the max at zero keeps it near nothing. Once the mean has
really moved, every reading pushes S the same way and it climbs steadily.

Thus the evidence ADDS UP over many samples, and a change too small to see in
any one of them is found after enough of them.

Two numbers set the behaviour, and they trade against each other:

    slack      how large a change is worth finding at all
    threshold  how much evidence is wanted before saying so

A smaller threshold finds the change sooner and gives more false alarms. This
is not a fault to be tuned away; it is the trade itself, and both directions
are a real choice.

Two totals run, one for a rise and one for a fall, because a total that only
grows upward cannot see a reading that has dropped.

## Macros

### `CHANGEPOINT_DEFAULT_CHANGE`

```c
#define CHANGEPOINT_DEFAULT_CHANGE      REAL_C(1.0)
```

### `CHANGEPOINT_DEFAULT_THRESHOLD`

```c
#define CHANGEPOINT_DEFAULT_THRESHOLD   REAL_C(5.0)
```

## Types

### `changepoint_t`

```c
typedef struct{
    real_t expected;            // Where the reading sits when nothing is wrong
    real_t deviation;           // How far it wanders there
    real_t smallest_change;     // The smallest change worth finding
    real_t threshold;           // How far a sum must run before it says so
    real_t high;                // The running sum upwards
    real_t low;                 // And downwards
    uint32_t since_high;        // Samples since the upward sum left nothing
    uint32_t since_low;         // And the downward one
    uint32_t counted;           // Samples since the last alarm
    bool designed;              // True once changepoint_design has been called
}changepoint_t;
```

## Functions

### `changepoint_is_valid_deviation`

```c
bool changepoint_is_valid_deviation(real_t deviation);
```

Give whether the reading wanders by an amount this can work with. A wander of
nothing means every sample is exact, and then a change of any size shows in
one sample and needs none of this.

### `changepoint_is_valid_change`

```c
bool changepoint_is_valid_change(real_t smallest_change);
```

Give whether a change of this size is one that can be looked for. The size is
in units of how far the reading wanders, thus 1.0 means a change the size of
the noise and 0.5 means half of it.

### `changepoint_is_valid_threshold`

```c
bool changepoint_is_valid_threshold(real_t threshold);
```

Give whether a sum must run this far. The threshold is in the same units, and
it is the whole of the trade between how often the alarm is wrong and how
long it takes.

### `changepoint_make`

```c
changepoint_t changepoint_make(void);
```

Give a watcher that is not yet watching anything.

### `changepoint_design`

```c
bool changepoint_design(changepoint_t* changepoint, real_t expected, real_t deviation, real_t smallest_change, real_t threshold);
```

Tell the watcher what ordinary looks like and what to look for.

The expected value and the deviation are what the reading does when nothing
is wrong, and they are usually measured from a stretch of reading known to be
good: stats_mean and stats_deviation give both.

The smallest change and the threshold are in units of the deviation. A
smallest change of 1.0 and a threshold of 5.0 is the usual place to start.

THE THRESHOLD IS THE WHOLE OF THE TRADE, and these are the two numbers it
trades between. Measured on twenty million samples of normal noise with a
smallest change of 1.0, and none of it changing at all:

  threshold    one wrong alarm in    samples to find a change of 1.0
  ---------    ------------------    -------------------------------
       4.0                   168                                  8
       5.0                   465                                 10
       6.0                  1265                                 12
       8.0                  9281                                 16

Reading down the table is the choice. A watcher on a bearing that is read
once a second sees 86 400 samples a day, thus a threshold of 5.0 cries wolf
about 185 times a day and a threshold of 8.0 about nine times. Neither number
is right; which one is depends on what a wrong alarm costs and what a missed
change costs, and the arithmetic cannot say.

The right hand column is changepoint_delay_for, which is exact. The middle
column moves with the SHAPE of the noise as well as its spread: the same
measurement on an even spread rather than a normal one gave one wrong alarm
in 372 samples at a threshold of 5.0 and one in 5115 at 8.0. Measure it on
your own reading where it matters.

Give false and leave the watcher as it was if any of the four is refused.

### `changepoint_process_sample`

```c
changepoint_way_t changepoint_process_sample(changepoint_t* changepoint, real_t sample);
```

Give the watcher one sample and hear whether the reading has changed.

THE ANSWER IS GIVEN ONCE AND THE SUMS ARE THEN PUT BACK TO NOTHING, so that
the next alarm is about the next change and not about the same one still
running. Where the change is still there, the sums build again and the alarm
comes again after the same delay.

### `changepoint_process_block`

```c
bool changepoint_process_block(changepoint_t* changepoint, const real_t* input, uint32_t count, changepoint_way_t* way, uint32_t* at);
```

Give a whole block to the watcher and hear about the FIRST change in it.

Gives true where a change was found, and writes which way it went and the
sample of the block it was reported at. Gives false where the block held
none, leaving both untouched. Either may be NULL.

THE WHOLE BLOCK IS ALWAYS READ, whether a change was found in it or not, thus
the watcher is left standing at the end of it and the next block carries on.
A block holding more than one change reports only the first: reach for
changepoint_process_sample where every one of them matters.

changepoint_began_ago still says how long before the alarm the reading
started walking away, and must be read straight after this.

### `changepoint_began_ago`

```c
uint32_t changepoint_began_ago(const changepoint_t* changepoint);
```

Give how many samples ago the change that was just reported began.

This is the number that makes the alarm useful. The alarm arrives late by
design, thus knowing WHEN it arrived says little; knowing when the reading
started running away says which batch, which shift or which load it was.

Only meaningful straight after changepoint_process_sample gave something
other than CHANGEPOINT_NONE.

### `changepoint_running_high`

```c
real_t changepoint_running_high(const changepoint_t* changepoint);
```

Give how far the upward sum has run, in units of the deviation. It reaches
the threshold when the alarm goes. Reading it between alarms says how close
the reading is standing to one.

### `changepoint_running_low`

```c
real_t changepoint_running_low(const changepoint_t* changepoint);
```

And the downward sum.

### `changepoint_delay_for`

```c
real_t changepoint_delay_for(const changepoint_t* changepoint, real_t change);
```

Give roughly how many samples it takes to find a change of the given size,
once that change has begun. The size is in units of the deviation.

This is the number to choose a threshold by. A threshold twice as high is
wrong half as often and takes twice as long, and which of those matters is
not something the arithmetic can say.

Give 0 where the change is not one the watcher would find at all, which is
any change smaller than half the smallest change it was designed for: below
that the sum wanders about nothing and never arrives.

### `changepoint_reset`

```c
void changepoint_reset(changepoint_t* changepoint);
```

Put both sums back to nothing and forget how long they have been running.
What the watcher was told about the reading is kept.
