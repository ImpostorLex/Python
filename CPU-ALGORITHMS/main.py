from flask import Flask, render_template, request
import requests

from algorithms import FCFS, SJF, SRTF

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    wt, tat, rst, tat_avg, wt_avg, gantt_chart, at_bt, process_mapper, tat_sum, wt_sum, num_of_process = [
    ], [], [], 0, 0, {}, [], [], 0, 0, 0

    at = []
    bt = []
    if request.method == 'POST':

        bt = request.form.get("burstTime")
        at = request.form.get("arrivalTime")
        algorithm = request.form.get("selectBox")

        bt = list(bt.split(' '))
        at = list(at.split(' '))

        # Check for letters in bt
        for i in range(len(bt)):
            if not bt[i].isdigit():
                error_message = "Invalid input in burstTime"
                return render_template('index.html', error_message=error_message)

        for i in range(len(at)):
            if not at[i].isdigit():
                error_message = "Invalid input in arrivalTime"
                return render_template('index.html', error_message=error_message)

        if algorithm == '0':

            wt, tat, rst, tat_avg, wt_avg, gantt_chart, at_bt, process_mapper, tat_sum, wt_sum, num_of_process = FCFS(
                at, bt)

            m = "FCFS"
        elif algorithm == '1':

            wt, tat, rst, tat_avg, wt_avg, gantt_chart, at_bt, process_mapper, tat_sum, wt_sum, num_of_process = SJF(
                at, bt)

            m = "SJF"

        elif algorithm == '3':

            wt, tat, sum_tat, sum_wt, avg_tat, avg_wt, num_of_process, remove_dups, gantt_chart_real, atbt = SRTF(
                at, bt)

            m = "SRTF"

            return render_template('index.html', error_message="", m=m, zip=zip, wt2=wt, tat=tat, wt_sum=sum_wt,
                                   tat_sum2=sum_tat, tat_avg=avg_tat, wt_avg=avg_wt,
                                   sum_wt=sum_wt, process=remove_dups,
                                   gantt_chart=gantt_chart_real, sorted_abt=atbt, num_p=num_of_process
                                   )

        # redirect user and clear form
        return render_template('index.html', error_message="", m=m, zip=zip,  wt=wt, tat=tat,
                               at=at, bt=bt, rst=rst, tat_avg=tat_avg, wt_avg=wt_avg, gantt_chart=gantt_chart, at_bt=at_bt, process_mapper=process_mapper, tat_sum=tat_sum, wt_sum=wt_sum, num_of_process=num_of_process)

    return render_template('index.html', error_message="", zip=zip,  wt=wt, tat=tat, rst=rst, tat_avg=tat_avg,
                           at=at, bt=bt, wt_avg=wt_avg, gantt_chart=gantt_chart, at_bt=at_bt, process_mapper=process_mapper, tat_sum=tat_sum, wt_sum=wt_sum, num_of_process=num_of_process)


if __name__ == "__main__":
    app.run(debug=True)
