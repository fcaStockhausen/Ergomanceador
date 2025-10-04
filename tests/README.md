# Automated Testing System

## Overview

Automated test runner that injects keyboard inputs from JSON sequences. No manual gameplay needed!

## Usage

### List available tests
```bash
python tests/test_runner.py list
```

### Run a specific test
```bash
python tests/test_runner.py spell_casting
python tests/test_runner.py basic_movement
python tests/test_runner.py jump_test
python tests/test_runner.py combined_test
```

## Test Sequences

Located in `tests/test_sequences.json`

### Creating New Tests

```json
{
  "my_test": {
    "description": "Description of what this tests",
    "duration": 5.0,
    "sequence": [
      {"time": 0.0, "key": "w", "action": "press"},
      {"time": 1.0, "key": "w", "action": "release"},
      {"time": 1.5, "key": "space", "action": "press"},
      {"time": 1.6, "key": "space", "action": "release"}
    ]
  }
}
```

**Fields:**
- `time`: Seconds from test start
- `key`: Key name (w, a, s, d, q, e, u, o, space, alt, etc.)
- `action`: "press" or "release"

## Available Tests

### `basic_movement`
Tests WASD movement controls (5 seconds)

### `spell_casting`
Tests element queueing (Q/E/U/O) and casting (SPACE) (8 seconds)
- Fire only
- Fire + Water (cancellation)
- Earth only
- Fire + Water + Earth + Air (4 elements)

### `jump_test`
Tests jump mechanics with ALT key (3 seconds)

### `combined_test`
Movement + spells + jumping together (10 seconds)

## How It Works

1. Loads test sequence from JSON
2. Initializes pygame and Game instance
3. Injects KEYDOWN/KEYUP events at specified times
4. Logs all inputs with timestamps
5. Runs for specified duration
6. Outputs results to console

## Benefits

- **Automated**: No manual testing needed
- **Reproducible**: Same inputs every time
- **Fast**: Run tests in seconds
- **Debuggable**: Logs show exact input timing
- **Extensible**: Add new tests in JSON

## Example Output

```
============================================================
Running test: spell_casting
Description: Test element queueing and spell casting
Duration: 8.0s
============================================================

[0.00s] Press Q
[0.10s] Release Q
[0.50s] Press SPACE
[0.60s] Release SPACE
[1.00s] Press Q
[1.10s] Release Q
[1.20s] Press E
[1.30s] Release E
[1.50s] Press SPACE
[1.60s] Release SPACE

Test 'spell_casting' completed!
```

## Interrupt Testing

Press **ESC** during test to quit early.
