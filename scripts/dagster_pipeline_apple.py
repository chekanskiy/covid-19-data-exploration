from dagster import (
    execute_pipeline,
    pipeline,
    solid,
    resource,
    ModeDefinition,
    Field,
    String,
    PresetDefinition,
    file_relative_path,
)

import os, sys
import pathlib
from datetime import datetime, timedelta


class LocalSQLiteWarehouse(object):
    def __init__(self, conn_str):
        self._conn_str = conn_str

    # In practice, you'll probably want to write more generic, reusable logic on your resources
    # than this tutorial example
    def update_db(self, records):
        import sqlite3

        conn = sqlite3.connect(self._conn_str)
        curs = conn.cursor()
        try:
            curs.execute("DROP TABLE IF EXISTS apple_report")
            curs.execute(
                """CREATE TABLE IF NOT EXISTS apple_report
                (name text, size real)"""
            )
            # curs.executemany(
            #     '''INSERT INTO apple_report VALUES
            #     (?, ?)''',
            #     [tuple(record.values()) for record in records],
            # )
        finally:
            curs.close()


@resource(config_schema={"conn_str": Field(String)})
def local_sqlite_warehouse_resource(context):
    return LocalSQLiteWarehouse(context.resource_config["conn_str"])


@solid(config_schema={"link": Field(String, is_required=False)})
def get_link(context) -> str:
    return context.solid_config["link"]


@solid(
    config_schema={
        "date_report": Field(
            String,
            is_required=False,
            default_value=(datetime.now().date() - timedelta(days=2)).strftime(
                "%Y-%m-%d"
            ),
        ),
        "output_path": Field(String, is_required=True),
    },
)
def download_csv(context, link: str) -> int:
    date_report = context.solid_config["date_report"]
    call = (
        f"curl -f -o {context.solid_config['output_path']}/applemobilitytrends-{date_report}.csv -L "
        f"{link}"
        f"{date_report}.csv"
    )
    context.log.info(call)

    output = os.system(call)
    if output != 0:
        raise Exception("Failed Download")

    return int(output)


@pipeline(
    mode_defs=[
        ModeDefinition(
            name="unittest",
            resource_defs={"warehouse": local_sqlite_warehouse_resource},
        ),
    ],
    preset_defs=[
        PresetDefinition(
            "unittest",
            run_config={
                "solids": {
                    "download_csv": {
                        "config": {
                            "date_report": (
                                datetime.now().date() - timedelta(days=2)
                            ).strftime("%Y-%m-%d"),
                            "output_path": f"{pathlib.Path(__file__).parent.resolve()}/../data-input/apple-mobility",
                        }
                    },  # 'output_path': f"{APP_PATH}/../data-input/apple-mobility"
                    "get_link": {
                        "config": {
                            "link": f"https://covid19-static.cdn-apple.com/covid19-mobility-data/2011HotfixDev{(datetime.now() - datetime(2020, 6, 22)).days}/v3/en-us/applemobilitytrends-"
                        }
                    },
                },
                "resources": {"warehouse": {"config": {"conn_str": ":memory:"}}},
            },
            mode="unittest",
        ),
        # PresetDefinition.from_files(
        #     'dev',
        #     environment_files=[
        #         file_relative_path(__file__, 'presets_dev_warehouse.yaml'),
        #         file_relative_path(__file__, 'presets_csv.yaml'),
        #     ],
        #     mode='dev',
        # ),
    ],
)
def apple_pipeline():
    download_csv(link=get_link())


if __name__ == "__main__":
    result = execute_pipeline(
        pipeline=apple_pipeline,
        mode="unittest",
        # run_config=run_config,
    )
    assert result.success

# def test_hello_cereal_solid():
#     res = execute_solid(hello_cereal)
#     assert res.success
#     assert len(res.output_value()) == 77


# def test_hello_cereal_pipeline():
#     res = execute_pipeline(hello_cereal_pipeline)
#     assert res.success
#     assert len(res.result_for_solid('hello_cereal').output_value()) == 77
