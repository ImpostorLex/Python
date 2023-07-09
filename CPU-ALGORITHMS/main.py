from flask import Flask, render_template, request
import requests

from algorithms import FCFS, SJF

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

        if algorithm == '0':

            wt, tat, rst, tat_avg, wt_avg, gantt_chart, at_bt, process_mapper, tat_sum, wt_sum, num_of_process = FCFS(
                at, bt)

        elif algorithm == '1':

            wt, tat, rst, tat_avg, wt_avg, gantt_chart, at_bt, process_mapper, tat_sum, wt_sum, num_of_process = SJF(
                at, bt)

            # print("WT:", wt)
            # print("TAT:", tat)
            # print("RST:", rst)
            # print("TAT Average:", tat_avg)
            # print("WT Average:", wt_avg)
            # print("Gantt Chart:", gantt_chart)
            # print("AT_BT:", at_bt)
            # print("process mapper:", process_mapper)

        # redirect user and clear form
        return render_template('index.html', zip=zip,  wt=wt, tat=tat,
                               at=at, bt=bt, rst=rst, tat_avg=tat_avg, wt_avg=wt_avg, gantt_chart=gantt_chart, at_bt=at_bt, process_mapper=process_mapper, tat_sum=tat_sum, wt_sum=wt_sum, num_of_process=num_of_process)

    return render_template('index.html', zip=zip,  wt=wt, tat=tat, rst=rst, tat_avg=tat_avg,
                           at=at, bt=bt, wt_avg=wt_avg, gantt_chart=gantt_chart, at_bt=at_bt, process_mapper=process_mapper, tat_sum=tat_sum, wt_sum=wt_sum, num_of_process=num_of_process)


if __name__ == "__main__":
    app.run(debug=True)
