import os

from odps import ODPS


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

o = ODPS(
    get_required_env('ODPS_ACCESS_KEY'),
    get_required_env('ODPS_ACCESS_SECRET'),
    os.getenv('ODPS_PROJECT', 'taidou_local_life'),
    endpoint=os.getenv('ODPS_ENDPOINT', 'https://service.cn-shanghai.maxcompute.aliyun.com/api')
)

sql = """
SELECT
    project_code,
    project_name,
    project_create_time,
    sheet_name,
    view_name,
    ds
FROM ods_feishu_main_project_process
WHERE ds = '20260707'
LIMIT 10
"""
inst = o.execute_sql(sql)
inst.wait_for_success()
with inst.open_reader() as reader:
    print('reader_count=', reader.count)
    for record in reader:
        print(record)
