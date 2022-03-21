# (c) 2022 Warren Usui
# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Make the calls to generate results of a March Madness pool
"""
from collect_entries import collect_entries
from find_future_outcomes import find_future_outcomes
from generate_display import generate_display
collect_entries()
find_future_outcomes()
generate_display()
