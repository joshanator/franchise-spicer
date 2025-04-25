# Event System Tests

This document describes the test suite for the Madden Franchise events system and how to run the tests.

## Prerequisites

- Python 3.x
- The Madden Franchise application code

## Running the Tests

You can run all tests using the Python unittest module:

```bash
python -m unittest test_events.py
```

To run a specific test:

```bash
python -m unittest test_events.TestEvents.test_all_events_processable
```

## CI Pipeline

This project uses GitHub Actions for continuous integration testing. Every time a commit is pushed to the main, master, dev, or development branches, or when a pull request is created targeting these branches, the CI pipeline automatically runs the tests.

The CI pipeline:
1. Sets up Python environments (3.9 and 3.10)
2. Installs required dependencies including PySide6
3. Sets up X Virtual Frame Buffer (Xvfb) for QT testing on headless environments
4. Runs the full test suite
5. Runs critical tests individually for more detailed reporting
6. Tests unrealistic events and combined event pools

The workflow configuration file is located at `.github/workflows/tests.yml`.

### CI Status

You can check the status of the CI pipeline in the GitHub Actions tab of the repository.

## Available Tests

### `test_all_events_processable`

This is the primary comprehensive test that verifies all events in the system can be properly processed without errors.

- Processes every event in the `events.json` file
- Verifies target replacements, description formatting, and other key properties
- Tests event acceptance functionality
- Outputs success messages for each processed event

```bash
python -m unittest test_events.TestEvents.test_all_events_processable
```

### `test_unrealistic_events`

Tests unrealistic events from the unrealistic_events.json file:

- Processes every event in the `unrealistic_events.json` file
- Verifies these events can be processed correctly
- Tests event acceptance functionality for unrealistic events
- Outputs success messages for each processed unrealistic event

```bash
python -m unittest test_events.TestEvents.test_unrealistic_events
```

### `test_combined_event_pool`

Tests that the event pool correctly includes both normal and unrealistic events:

- Verifies that when unrealistic events are enabled, they're included in the event pool
- Checks that the combined pool size is correct
- Reports on the number of events in each category

```bash
python -m unittest test_events.TestEvents.test_combined_event_pool
```

### `test_events_with_options`

Tests events that include user-selectable options:

- Focuses on events with ID 10, 11, 12, 21, 22, 48, 50
- Verifies options are properly processed
- Tests the option selection functionality
- Checks that selected options are added to event history

```bash
python -m unittest test_events.TestEvents.test_events_with_options
```

### `test_random_impact_options`

Tests events with random outcome options:

- Focuses on events with ID 10, 22, 38, 51
- Verifies random impact selection functionality
- Checks that impacts can be selected based on provided weights

```bash
python -m unittest test_events.TestEvents.test_random_impact_options
```

### `test_difficulty_filter`

Tests that events are properly filtered by difficulty level:

- Tests all difficulty levels: cupcake, rookie, pro, all-madden, diabolical
- Verifies that the event manager can roll events at each difficulty

```bash
python -m unittest test_events.TestEvents.test_difficulty_filter
```

### `test_season_stage_filter`

Tests that events are properly filtered by season stage:

- Tests all season stages: Pre-Season, Regular Season Start, Regular Season Mid, Regular Season End, Post-Season, Off-Season
- Also tests internal stage representation formats
- Verifies that the event manager can roll events for each stage

```bash
python -m unittest test_events.TestEvents.test_season_stage_filter
```

### `test_trainer_events`

Tests events with trainer selections:

- Focuses on events with ID 19, 20, 35, 69, 70, 71, 72, 73, 74, 75, 76
- Verifies trainer selection and impact application
- Checks that trainer placeholders are properly replaced in descriptions and impacts

```bash
python -m unittest test_events.TestEvents.test_trainer_events
```

### `test_nested_options`

Tests events with nested options (options within options):

- Focuses on events with ID 12, 16, 68
- Verifies correct structure of nested options
- Checks that all nested options have valid descriptions

```bash
python -m unittest test_events.TestEvents.test_nested_options
```

### `test_find_all_events_with_options`

Informational test that identifies all events with options:

- Scans the entire events.json file
- Outputs a list of event IDs and titles that contain options
- Useful for identifying events to test in other test cases

```bash
python -m unittest test_events.TestEvents.test_find_all_events_with_options
```

### `test_find_all_events_with_random_impacts`

Informational test that identifies all events with random impact options:

- Scans the entire events.json file
- Outputs a list of event IDs and titles that contain random impact options
- Useful for identifying events to test in random impact tests

```bash
python -m unittest test_events.TestEvents.test_find_all_events_with_random_impacts
```

### `test_event_schema_validation`

Tests that all events in the JSON file follow the required schema:

- Verifies all required fields are present in each event
- Checks that difficulty weights include all difficulty levels
- Ensures season stages is a non-empty list
- For events with options, validates that each option has description and impact fields

```bash
python -m unittest test_events.TestEvents.test_event_schema_validation
```

## Test Configuration

The tests use a mock data manager with test configuration:
- Difficulty: pro
- Team name: Test Team
- Season stage: Pre-Season
- A complete roster with test player names
- Unrealistic events enabled

## Setting Up Unrealistic Events

To test unrealistic events, create a file at `madden_franchise_qt/data/unrealistic_events.json` with the following structure:

```json
{
  "unrealistic_events": [
    {
      "id": 1001,
      "title": "Test Unrealistic Event",
      "description": "This is a test unrealistic event",
      "impact": "This is the impact of the unrealistic event",
      "difficulty_weights": {
        "cupcake": 0.1,
        "rookie": 0.2,
        "pro": 0.3,
        "all-madden": 0.4,
        "diabolical": 0.5
      },
      "category": "test",
      "season_stages": [
        "pre-season",
        "regular-season-start"
      ]
    }
    // Add more unrealistic events as needed
  ]
}
```

The CI pipeline will create an empty unrealistic events file if one doesn't exist, but for more comprehensive testing, you should create your own with actual test events.

## Example Workflow

For general test execution:

```bash
# Run all tests
python -m unittest test_events.py

# Run a specific test category
python -m unittest test_events.TestEvents.test_random_impact_options

# Run tests with verbose output
python -m unittest -v test_events.py
```

When developing new events:

1. Add your event to `madden_franchise_qt/data/events.json`
2. Run `test_event_schema_validation` to verify your event follows the schema
3. Run `test_all_events_processable` to check if your event can be processed without errors
4. If your event has options or random impacts, run the specific tests for those features

For unrealistic events:

1. Add your unrealistic event to `madden_franchise_qt/data/unrealistic_events.json`
2. Run `test_unrealistic_events` to verify your unrealistic events can be processed
3. Run `test_combined_event_pool` to verify that unrealistic events are included in the event pool 