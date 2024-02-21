import os
import pytest
import argparse
from utils.send_allure_report import *

report_dir = './allure-report/html'
result_dir = './outputs/result/xml'
report_file = f"{report_dir}/data/suites.csv"
json_data_path = os.path.join(report_dir, 'data', 'test-cases')
webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d26f3c53-2019-4e04-8df5-64e417e31d43'


def run(testcases, env, browser, headless):
    # 创建报告目录
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    # 执行pytest命令
    pytest.main(['--alluredir', result_dir, '--clean-alluredir', f'{testcases}',
                 f'--env={env}', f'--browser={browser}', f'--headless={headless}'])
    # 生成Allure报告
    os.system('allure generate %s -o %s --clean' % (result_dir, report_dir))
    # 发送消息、文件到企业微信机器人
    total_cases, passed, failed, broken, skipped, total_time = get_test_results(json_data_path)
    send_test_report(webhook_url, env, browser, total_cases, passed, failed, broken, skipped, total_time)
    send_file(webhook_url, report_file)
    # 打开报告
    # os.system('allure open ' + report_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--testcases', default="./smoke_test/new/test_smoke.py")
    parser.add_argument('--env', default="test")
    parser.add_argument('--browser', default="chromium")
    parser.add_argument('--headless', action='store_true')

    args = parser.parse_args()
    testcases = args.testcases
    env = args.env
    browser = args.browser
    headless = args.headless

    run(testcases, env, browser, headless)

    # python run.py --testcases="-m smoke_test"
    # python run.py --testcases=./testcases --env=prod --browser=chromium --headless
    # python run.py --testcases="-k not (test_chromium_login or test_firefox_login or test_webkit_login)"
