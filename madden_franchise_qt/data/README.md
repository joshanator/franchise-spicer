# Madden Franchise Event System

## Event Difficulty Weights

The difficulty weights control how likely an event is to occur based on your selected difficulty level. Here's how they work:

When the game rolls for an event, it:

1. Gets your current difficulty setting (easy, medium, or hard)
2. For each event that matches your current season stage, it checks the difficulty weight
3. Generates a random number between 0 and 1
4. If the random number is less than the weight, the event becomes eligible to be selected

For example, looking at the "PED Suspension" event:
```
"difficulty_weights": {
  "easy": 0.3,
  "medium": 0.5,
  "hard": 0.7
}
```

This means:
- On easy difficulty: 30% chance to be eligible
- On medium difficulty: 50% chance to be eligible
- On hard difficulty: 70% chance to be eligible

Negative events typically have higher weights on harder difficulties, making them more likely to occur. Positive events often have higher weights on easier difficulties.

After determining all eligible events based on these probability checks, the game randomly selects one from the eligible pool.

## Season Stages

Events can be configured to only appear during specific season stages:

- Pre-Season: Weeks 1-4
- Regular Season Start: Weeks 5-7
- Regular Season Mid: Weeks 8-15
- Regular Season End: Weeks 16-22
- Post-Season: Weeks 23-26
- Off-Season: Week 27+ 