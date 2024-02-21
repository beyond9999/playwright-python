import os
import json
import requests


def send_message(wx_url, message):
    headers = {'Content-Type': 'application/json'}
    data = {
        'msgtype': 'markdown',
        'markdown': {'content': message},
        "mentioned_list": ["@all"],
    }

    r = requests.post(wx_url, headers=headers, data=json.dumps(data))
    return r.status_code == 200


def get_test_results(report_path):
    total = passed = failed = broken = skipped = 0
    total_time = 0

    json_files = [file for file in os.listdir(report_path) if file.endswith('.json')]

    for json_file in json_files:
        json_path = os.path.join(report_path, json_file)
        with open(json_path, 'r', encoding='utf-8') as file:
            test_case_data = json.load(file)
            total += 1
            status = test_case_data['status']
            if status == 'passed':
                passed += 1
            elif status == 'failed':
                failed += 1
            elif status == 'broken':
                failed += 1
            elif status == 'skipped':
                skipped += 1

            if 'time' in test_case_data:
                total_time += int(test_case_data['time']['duration'] / 1000)

    return total, passed, failed, broken, skipped, total_time


def send_test_report(wx_url, env, browser, total, passed, failed, broken, skipped, total_time):
    if failed == 0 and broken == 0:
        test_result = "通过"
    else:
        test_result = "失败"

    success_rate = (passed / total) * 100 if total > 0 else 0

    message_content = f'## 本次 {env}_{browser}测试执行情况如下：\n' \
                      f'>测试结果：{test_result}\n' \
                      f'>用例总数：{total} 条\n' \
                      f'>通过用例数：<font color=\"info\">{passed}</font> 条\n' \
                      f'>失败用例数：<font color=\"warning\">{failed}</font> 条\n' \
                      f'>异常用例数：<font color=\"warning\">{broken}</font> 条\n' \
                      f'>跳过用例数：<font color="comment">{skipped}</font> 条\n' \
                      f'>用例成功率：<font color=\"info\">{success_rate:.2f}%</font>\n' \
                      f'>用例执行耗时：<font color="comment">{total_time}</font> s\n' \
                      f'>测试报告：[请点击该链接](http://work.weixin.qq.com/api/doc\n)'

    if send_message(wx_url, message_content):
        print('消息发送成功')
    else:
        print('消息发送失败')


def send_file(wx_url, file_path):
    k = wx_url.split('key=')[1]
    upload_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={k}&type=file'
    with open(file_path, 'rb') as file:
        data = {'file': file}
        response = requests.post(url=upload_url, files=data)
        json_res = response.json()
        media_id = json_res.get('media_id')

    if media_id:
        file_data = {"msgtype": "file", "file": {"media_id": media_id}}
        r = requests.post(url=wx_url, json=file_data)
        if r.status_code == 200:
            print('文件发送成功')
            return True

    print('文件发送失败')
    return False
