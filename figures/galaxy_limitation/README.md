# Galaxy Limitation Figure Notes

This directory contains derived figures generated from immutable artifacts under `outputs/`.

Run count read: 61

Runs excluded from plots because they lacked a scored Galaxy-only route and had no explicit Galaxy-limitation evidence: 4

Runs with explicit Galaxy-limitation evidence: 54

Runs with material non-Galaxy workaround evidence: 47

Galaxy-blocked failures: 5

Galaxy-limited runs solved via workaround: 25

Galaxy-limited runs where workaround was insufficient: 21

Classification is evidence-based and conservative. A run is marked as Galaxy-limited when one or more stored artifacts indicate Galaxy-specific constraints, including Galaxy/API/job/upload errors, queue or disabled-service events, wrapper/schema friction, missing Galaxy output capability, or `External_manipulation` text saying non-Galaxy processing materially prepared task-specific inputs before Galaxy performed final extraction. The `No explicit Galaxy limitation` group is reserved for scored runs with Galaxy tools/results and no material non-Galaxy workaround.

These plots are intended to show when Galaxy constrained task accomplishment, not to score ordinary agent mistakes. Local preparation errors without Galaxy evidence remain outside the Galaxy-limitation classes.
