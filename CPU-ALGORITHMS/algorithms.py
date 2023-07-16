from collections import OrderedDict
import csv
from icecream import ic
import pandas as pd


def FCFS(at, bt):

    AT_BT = []

    num_of_process = len(at)

    # Group AT and BT
    AT_BT = [(int(a), int(b), i+1)
             for i, (a, b) in enumerate(zip(at, bt))]

    sorted_AT_BT = sorted(AT_BT)

    AT_BT.sort()
    gantt_chart = {}

    ctr = 1
    gantt_value = 0
    # Since it is already sorted
    for x, y, _ in AT_BT:

        # Do Gantt Chart
        gantt_value += y
        gantt_chart[ctr] = gantt_value
        ctr = ctr + 1

    TAT = []
    WT = []
    RST = []

    tat_gantt_ctr = 1
    tat_at_ctr = 0

    wt_bt_ctr = 0

    tat_sum = 0
    wt_sum = 0

    rst_gantt_ctr = 1
    rst_at_ctr = 0

    process_mapper = [item[2] for item in sorted_AT_BT]

    for num in gantt_chart:

        # Calculate TURN-AROUND-TIME
        tat_value = gantt_chart[tat_gantt_ctr] - AT_BT[tat_at_ctr][0]
        TAT.append(tat_value)
        tat_gantt_ctr = tat_gantt_ctr + 1
        tat_at_ctr = tat_at_ctr + 1

        # Calculate Waiting time
        wt_value = max(tat_value - AT_BT[wt_bt_ctr][1], 0)
        WT.append(wt_value)
        wt_bt_ctr += 1

        # Calculate average time
        tat_sum += tat_value
        wt_sum += wt_value

        # Calculate the RESPONSE TIME
        rst_val = max(gantt_chart[rst_gantt_ctr] - AT_BT[rst_at_ctr][0], 0)
        RST.append(rst_val)
        rst_gantt_ctr += 1
        rst_at_ctr += 1

    tat_avg = tat_sum / num_of_process
    wt_avg = wt_sum / num_of_process

    return WT, TAT, RST, tat_avg, wt_avg, gantt_chart, AT_BT, process_mapper, tat_sum, wt_sum, num_of_process


def SJF(at, bt):

    AT_BT = []

    num_of_process = len(at)

    # Group AT and BT
    AT_BT = [(int(b), int(a), i+1)
             for i, (b, a) in enumerate(zip(bt, at))]

    # The lambda acts as a user def function and lamba is great for
    # one liner function, since no matter what CPU algo it is
    # 0 AT is KING! and must go first
    sorted_AT_BT = sorted(AT_BT, key=lambda x: (x[1] != 0, x[0]))

    gantt_chart = {}

    ctr = 1
    gantt_value = 0
    # Since it is already sorted
    for x, y, _ in sorted_AT_BT:

        # Do Gantt Chart
        print(f"Proces{x}")
        gantt_value += x
        gantt_chart[ctr] = gantt_value
        ctr = ctr + 1

    print(f"Sorted : {sorted_AT_BT}")
    print(f"Gantt Chart: {gantt_chart}")
    TAT = []
    WT = []
    RST = []

    tat_gantt_ctr = 1
    tat_at_ctr = 0

    wt_bt_ctr = 0

    tat_sum = 0
    wt_sum = 0

    rst_gantt_ctr = 1
    rst_at_ctr = 0

    process_mapper = [item[2] for item in sorted_AT_BT]

    for num in gantt_chart:

        # Calculate TURN-AROUND-TIME
        tat_value = gantt_chart[tat_gantt_ctr] - sorted_AT_BT[tat_at_ctr][0]
        TAT.append(tat_value)
        tat_gantt_ctr = tat_gantt_ctr + 1
        tat_at_ctr = tat_at_ctr + 1

        # Calculate Waiting time
        wt_value = max(tat_value - sorted_AT_BT[wt_bt_ctr][1], 0)
        WT.append(wt_value)
        wt_bt_ctr += 1

        # Calculate average time
        tat_sum += tat_value
        wt_sum += wt_value

        # Calculate the RESPONSE TIME
        rst_val = max(gantt_chart[rst_gantt_ctr] -
                      sorted_AT_BT[rst_at_ctr][0], 0)
        RST.append(rst_val)
        rst_gantt_ctr += 1
        rst_at_ctr += 1

    tat_avg = tat_sum / num_of_process
    wt_avg = wt_sum / num_of_process

    return WT, TAT, RST, tat_avg, wt_avg, gantt_chart, AT_BT, process_mapper, tat_sum, wt_sum, num_of_process


def get_values(d):
    values = []
    for key, value in d.items():
        if isinstance(value, dict):
            values.extend(get_values(value))
        else:
            if key == 'BT':
                values.append(value)
    return values


# at_bt_dict = {
#     'P4': {'BT': 7, 'AT': 0},
#     'P1': {'BT': 4, 'AT': 3},
#     'P3': {'BT': 4, 'AT': 8},
#     'P5': {'BT': 6, 'AT': 12},
#     'P2': {'BT': 9, 'AT': 5}
# }

# cp_atbt_dict = {
#     'P4': {'BT': 7, 'AT': 0},
#     'P1': {'BT': 4, 'AT': 3},
#     'P3': {'BT': 4, 'AT': 8},
#     'P5': {'BT': 6, 'AT': 12},
#     'P2': {'BT': 9, 'AT': 5}
# }

def SRTF(at, bt):

    num_of_process = len(at)

    # Group AT and BT
    AT_BT = [(int(b), int(a), i+1)
             for i, (b, a) in enumerate(zip(bt, at))]

    # The lambda acts as a user def function and lamba is great for
    # one liner function, since no matter what CPU algo it is
    # 0 AT is KING! and must go first
    sorted_AT_BT = sorted(AT_BT, key=lambda x: (x[1] != 0, x[0]))

    at_bt_dict = OrderedDict()
    cp_atbt_dict = OrderedDict()

    ic(sorted_AT_BT)

    # Turned the sorted list into a dictionary
    # since it is already sorted.
    for w, z, t in sorted_AT_BT:

        ic(t)
        process_key = f"P{t}"

        at_bt_dict[process_key] = {
            "BT": w,
            "AT": z,
        }

        cp_atbt_dict[process_key] = {
            "BT": w,
            "AT": z,
        }

    gantt_chart = []  # To store the Gantt chart
    current_time = min(at_bt_dict.values(), key=lambda x: x['AT'])[
        'AT']  # Current time in the scheduling algorithm

    while at_bt_dict:
        ready_queue = [
            process for process in at_bt_dict if at_bt_dict[process]['AT'] <= current_time
        ]
        if not ready_queue:
            current_time += 1
            continue

        shortest_process = min(
            ready_queue, key=lambda x: at_bt_dict[x]['BT'])

        # Get the arrival time and burst time of the shortest process
        arrival_time = at_bt_dict[shortest_process]['AT']
        burst_time = at_bt_dict[shortest_process]['BT']

        # Calculate the start time, end time, and turnaround time
        start_time = current_time
        end_time = current_time + 1
        turnaround_time = end_time - arrival_time

        # Update the Gantt chart with the process and its start and end times
        gantt_chart.append((shortest_process, start_time, end_time))

        # Update the burst time of the shortest process
        at_bt_dict[shortest_process]['BT'] -= 1

        # Remove the process if the burst time becomes zero
        if at_bt_dict[shortest_process]['BT'] == 0:
            del at_bt_dict[shortest_process]

        # Update the current time
        current_time += 1

    # Sort the Gantt chart based on start time
    gantt_chart.sort(key=lambda x: x[1])

    # Print the Gantt chart
    res = [eval(i) for i in at]
    res.sort()
    bt_values = get_values(cp_atbt_dict)

    gantt_value_as_list = []

    curr = 0
    for bt_val in bt_values:

        curr += bt_val
        gantt_value_as_list.append(curr)

    gantt_chart_real = []
    process_order = []
    for process, start, end in gantt_chart:

        if end >= int(res[0]) and (end in res or end == cp_atbt_dict[process]['BT']):

            gantt_chart_real.append((end, process))
            process_order.append(process)
            print(f"{end}: {process}")

        elif any(end == value for value in gantt_value_as_list):

            gantt_chart_real.append((end, process))
            process_order.append(process)
            print(f"{end}: {process}")

    remove_dups = list(dict.fromkeys(process_order))

    # Calculate TAT
    tat = []
    wt = []

    ctr2 = 0
    for key2 in remove_dups:

        new_tat = max(gantt_value_as_list[ctr2] - cp_atbt_dict[key2]['AT'], 0)
        tat.append(new_tat)

        new_wt = max(new_tat - cp_atbt_dict[key2]['BT'], 0)
        wt.append(new_wt)

        ctr2 = ctr2 + 1

    sum_tat = sum(tat)
    sum_wt = sum(wt)
    avg_tat = sum_tat / num_of_process
    avg_wt = sum_wt / num_of_process

    return wt, tat, sum_tat, sum_wt, avg_tat, avg_wt, num_of_process, remove_dups, gantt_chart_real, sorted_AT_BT
