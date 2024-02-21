import os
import pytest
import argparse
from utils.send_allure_report import *
from concurrent.futures import ThreadPoolExecutor


class Runner:
    def __init__(self):
        self.WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d26f3c53-2019-4e04-8df5-64e417e31d43'

    def _run(self, case_path, env, browser, headless):
        result_dir = f'./outputs/result/xml_{browser}'
        report_dir = f'./allure-report/html_{browser}'

        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(report_dir, exist_ok=True)

        args = [
            '--alluredir', result_dir, '--clean-alluredir', f'{case_path}',
            f'--env={env}', f'--browser={browser}', f'--headless={headless}'
        ]
        pytest.main(args)
        os.system('allure generate %s -o %s --clean' % (result_dir, report_dir))

        json_data_path = os.path.join(report_dir, 'data', 'test-cases')
        total_cases, passed, failed, broken, skipped, total_time = get_test_results(json_data_path)

        send_test_report(
            self.WEBHOOK_URL, f'{env}', f'{browser}',
            total_cases, passed, failed, broken, skipped, total_time
        )

        renamed_file = f"{report_dir}/data/{env}_{browser}测试报告.csv"
        os.rename(f"{report_dir}/data/suites.csv", renamed_file)
        send_file(self.WEBHOOK_URL, renamed_file)

    def run_tests(self, env, headless):
        r = Runner()
        executes = [
            lambda: r._run("-k not (test_login_fail or test_login_success or test_firefox_login or test_webkit_login)",
                           env, "chromium", headless),
            lambda: r._run("-k not test_login_fail and not test_login_success and not test_chromium_login and not "
                           "test_webkit_login", env, "firefox", headless),
            lambda: r._run("-k not test_login_fail and not test_login_success and not test_chromium_login and not "
                           "test_firefox_login", env, "webkit", headless)
        ]

        with ThreadPoolExecutor(max_workers=len(executes)) as executor:
            executor.map(lambda method: method(), executes)


# python threading_run.py --env=prod --headless
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', action='store', default="test")
    parser.add_argument('--headless', action='store_true', default=False)

    args = parser.parse_args()
    env = args.env
    headless = args.headless

    r = Runner()
    r.run_tests(env, headless)
