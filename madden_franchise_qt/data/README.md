# Madden Franchise Event System

## Event Difficulty Weights

The difficulty weights control how likely an event is to occur based on your selected difficulty level. Here's how they work:

When the game rolls for an event, it:

1. Gets your current difficulty setting (cupcake, rookie, pro, all-madden, or diabolical)
2. For each event that matches your current season stage, it checks the difficulty weight
3. Generates a random number between 0 and 1
4. If the random number is less than the weight, the event becomes eligible to be selected

For example, looking at the "PED Suspension" event:
```
"difficulty_weights": {
  "cupcake": 0.1,
  "rookie": 0.3,
  "pro": 0.5,
  "all-madden": 0.7,
  "diabolical": 0.9
}
```

This means:
- On cupcake difficulty: 10% chance to be eligible
- On rookie difficulty: 30% chance to be eligible
- On pro difficulty: 50% chance to be eligible
- On all-madden difficulty: 70% chance to be eligible
- On diabolical difficulty: 90% chance to be eligible

Negative events typically have higher weights on harder difficulties, making them more likely to occur. Positive events often have higher weights on easier difficulties.

After determining all eligible events based on these probability checks, the game randomly selects one from the eligible pool.

## Season Stages

Events can be configured to only appear during specific season stages:

- pre-season
- regular-season-start
- regular-season-mid / trade-deadline
- regular-season-end
- playoffs
- off-season