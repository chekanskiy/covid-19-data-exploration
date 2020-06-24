from prefect import task, Flow, Parameter
from prefect.tasks.shell import ShellTask
from datetime import timedelta

run_script = ShellTask(helper_script="cd ./scripts",
                       cache_for=timedelta(days=1),
                       return_all=True,
                       log_stdout=True)

with Flow("covid_update_data") as f:
    run_date = Parameter(name='run_date')

    # update_jhu = run_script(command="python 0_prepare_data_jhu.py")

    get_apple = run_script(command="python 1_apple_download_report.py")
    update_apple = run_script(command="python 2_prepare_data_apple.py")

    get_rki = run_script(command=f"python 3_rki_report_download.py --date={run_date}")
    parse_rki = run_script(command=f"python 4_rki_report_parse.py --date={run_date}")
    # update_rki = run_script(command="python 5_prepare_data_rki.py")

    update_apple.set_upstream(get_apple)
    parse_rki.set_upstream(get_rki)
    # update_rki.set_upstream(parse_rki)

f.run(parameters={"run_date": "2020-06-14"})
# f.visualize()