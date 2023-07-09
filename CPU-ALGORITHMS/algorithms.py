
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
