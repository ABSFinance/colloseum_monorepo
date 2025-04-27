#!/bin/bash

# Activate the ABS_eval virtual environment where riskfolio is installed
source /Users/munseon-ug/robo_advisor/ABS_eval/venv/bin/activate

# Run the test
python /Users/munseon-ug/robo_advisor/colloseum_monorepo/core/tests/test_optimizer/test_optimizer.py "$@" 