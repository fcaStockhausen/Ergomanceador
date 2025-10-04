# TAS-Style Testing System

## Overview

Tool-Assisted testing system for Karaokeficador. Write input sequences in JSON, run automated tests, verify behaviors via log analysis.

---

## Quick Start

```bash
# List all tests
python tests/verified_test_runner.py list

# Run specific test
python tests/verified_test_runner.py element_fire

# Run all tests
python tests/verified_test_runner.py all
```

---

## Test Structure

### Test File: `tests/test_cases.json`

```json
{
  "test_name": {
    "description": "What this test does",
    "duration": 2.0,
    "sequence": [
      {"time": 0.5, "key": "q", "action": "press"},
      {"time": 0.6, "key": "q", "action": "release"},
      {"time": 1.0, "key": "space", "action": "press"},
      {"time": 1.1, "key": "space", "action": "release"}
    ],
    "expected_logs": [
      "Element FIRE queued: ['fire']",
      "AIMED CAST: Fire Blast"
    ]
  }
}
```

### Fields

- **description**: Human-readable test description
- **duration**: Test duration in seconds
- **sequence**: Array of timed key presses/releases
  - `time`: Seconds from test start
  - `key`: Key name (q, e, r, f, u, o, p, semicolon, space, g, backspace, etc.)
  - `action`: "press" or "release"
- **expected_logs**: Strings that MUST appear in game_debug.log

---

## Available Tests (14 total)

### Element Tests (8 tests)
- `element_fire` - Q key → Fire Blast
- `element_water` - E key → Water Stream
- `element_ice` - R key → Ice Shard
- `element_earth` - F key → Earth spell
- `element_nature` - U key → Thorn Whip
- `element_arcane` - O key → Arcane Missile
- `element_light` - P key → Light spell
- `element_shadow` - ; key → Shadow Bolt

### Feature Tests (6 tests)
- `queue_multiple` - Queue Fire + Water + Ice
- `backspace_remove` - BACKSPACE removes last element
- `fire_water_cancel` - Fire+Water → Steam Explosion (cancellation)
- `light_shadow_polarity` - Light+Shadow → Polarity amplification
- `max_queue_5` - Try to queue 6 elements (max is 5)
- `jump_test` - G key jump

---

## How Verification Works

1. **Run Test** - Execute automated input sequence
2. **Capture Logs** - Read `game_debug.log`
3. **Verify** - Check if expected strings appear in logs
4. **Report** - Show ✅ PASS or ❌ FAIL with missing items

### Example Output

```
======================================================================
🎮 Running: fire_water_cancel
📝 Test Fire+Water cancellation (opposing elements)
⏱️  Duration: 2.5s
======================================================================

[0.50s] ⌨️  Press Q
[0.80s] ⌨️  Press E
[1.20s] ⌨️  Press SPACE

======================================================================
📊 VERIFICATION RESULTS
======================================================================
✅ TEST PASSED: All expected behaviors verified!

✓ Found (3/3):
  ✓ Element FIRE queued: ['fire']
  ✓ Element WATER queued: ['fire', 'water']
  ✓ AIMED CAST: Steam Explosion
======================================================================
```

---

## Creating New Tests

### 1. Add to `test_cases.json`

```json
{
  "my_new_test": {
    "description": "Test my new feature",
    "duration": 3.0,
    "sequence": [
      {"time": 0.5, "key": "q", "action": "press"},
      {"time": 0.6, "key": "q", "action": "release"}
    ],
    "expected_logs": [
      "Element FIRE queued"
    ]
  }
}
```

### 2. Run Test

```bash
python tests/verified_test_runner.py my_new_test
```

### 3. Debug Failed Tests

If test fails, check what was actually logged:

```bash
cat game_debug.log | grep "FIRE"
```

Then adjust `expected_logs` to match actual log format.

---

## Supported Keys

**Movement:** w, a, s, d
**Aiming:** i, j, k, l
**Elements (Left):** q (fire), e (water), r (ice), f (earth)
**Elements (Right):** u (nature), o (arcane), p (light), semicolon (shadow)
**Actions:** space (cast), g (jump), backspace (remove element)
**Quit:** esc

---

## Best Practices

### ✅ DO
- Test single features in isolation
- Use short durations (2-4 seconds)
- Verify specific log messages
- Test edge cases (max queue, cancellations)
- Run tests after every change

### ❌ DON'T
- Make tests too long (>5 seconds)
- Test multiple unrelated features together
- Use vague expected logs (e.g., "CAST")
- Forget to add press + release for keys
- Skip verification (always add expected_logs)

---

## Integration with Development Workflow

### Before Committing Code

```bash
# Run full test suite
python tests/verified_test_runner.py all

# Should see:
# ✅ Passed: 14/14
# ❌ Failed: 0/14
```

### When Adding Features

1. Write test case FIRST
2. Run test (will fail)
3. Implement feature
4. Run test again (should pass)
5. Commit both code + test

### When Fixing Bugs

1. Write test that reproduces bug
2. Verify test fails
3. Fix bug
4. Verify test passes
5. Commit fix + test

---

## Exit Codes

- **0** = All tests passed
- **1** = One or more tests failed

Useful for CI/CD:

```bash
python tests/verified_test_runner.py all
if [ $? -eq 0 ]; then
  echo "All tests passed!"
else
  echo "Tests failed!"
  exit 1
fi
```

---

## Troubleshooting

### Test passes but shouldn't

- Check if `expected_logs` is empty
- Verify log messages are specific enough
- Add more verification points

### Test fails but shouldn't

- Check log file: `cat game_debug.log`
- Verify timing (key press too early/late?)
- Check key names match (semicolon vs ;)
- Ensure logger is initialized

### No logs generated

- Check if `utils/logger.py` is imported
- Verify `game_debug.log` permissions
- Run game manually to test logging

---

## Future Enhancements

**Planned:**
- Visual test results (screenshots)
- Performance metrics (FPS during test)
- Network test support (multiplayer)
- Randomized input testing (fuzzing)
- Test coverage reports

**Suggestions Welcome:**
- Add your ideas to test_cases.json
- Submit PRs with new test scenarios
- Report bugs via issues

---

## Example: Testing a New Element

```json
{
  "element_lightning": {
    "description": "Test Lightning element (T key - hypothetical)",
    "duration": 2.0,
    "sequence": [
      {"time": 0.5, "key": "t", "action": "press"},
      {"time": 0.6, "key": "t", "action": "release"},
      {"time": 1.0, "key": "space", "action": "press"},
      {"time": 1.1, "key": "space", "action": "release"}
    ],
    "expected_logs": [
      "Element LIGHTNING queued: ['lightning']",
      "AIMED CAST: Chain Lightning",
      "behavior: beam"
    ]
  }
}
```

Run:
```bash
python tests/verified_test_runner.py element_lightning
```

---

## Summary

**TAS Testing = Fast, Reliable, Automated**

- Write once, run forever
- Catch regressions instantly
- Document expected behavior
- No manual testing needed

**Use it before every commit!** 🚀
