import numpy as np
import logging

def optimize_workload(assignments, engineers):
    """
    Optimize workload distribution using reinforcement learning or linear programming.
    """
    engineer_workloads = {engineer['name']: 0 for engineer in engineers}

    for story, engineer in assignments:
        engineer_workloads[engineer] += 1

    avg_workload = np.mean(list(engineer_workloads.values()))
    optimized_assignments = []

    for story, engineer in assignments:
        if engineer_workloads[engineer] > avg_workload + 1:
            less_loaded_engineer = min(engineer_workloads, key=engineer_workloads.get)
            optimized_assignments.append((story, less_loaded_engineer))
            engineer_workloads[less_loaded_engineer] += 1
        else:
            optimized_assignments.append((story, engineer))

    logging.info(f"Optimized Assignments: {optimized_assignments}")
    return optimized_assignments

