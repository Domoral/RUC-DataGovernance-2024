
# encoding:utf-8

import requests
import base64
import re, os, json, random, time, http.client
from config.apikey import half_api_key, full_api_key
import fire
from datetime import datetime

'''
通用文字识别
'''

def prompt(words):
    template = """你将会得到一个词构成的列表, 这些词是发票上通过OCR技术识别出来的文字.
词列表如下: [{words}]

请帮我解析出这张发票的以下信息:
1. 票据头
2. 票据号
3. 门诊号
4. 医疗机构
5. 姓名
6. 医保类型("自费医疗"或"公费医疗")
7. 项目
8. 合计金额

注意, OCR技术识别出的文字可能不准确, 如"自费医疗"可能识别为"百费医疔", "票据号"可能识别为"要据号". 请尽量根据上下文进行判断并纠错.

请按照以下的json格式返回解析出的信息:
```json
{{
    "票据头": "<填入你解析出的票据头>",
    "票据号": "<填入你解析出的票据号>",
    "门诊号": "<填入你解析出的门诊号>",
    "医疗机构": "<填入你解析出的医疗机构>",
    "姓名": "<填入你解析出的姓名>",
    "医保类型": "<填入你解析出的医保类型>",
    "项目": "<填入你解析出的项目>",
    "合计金额": "<填入你解析出的合计金额>",
}}
```

请确保不返回任何其他内容. 有些信息可能不存在, 请填入"None".
"""
    return template.format(words=words)

def llm_gen(prompt, model):
    
    if "gpt-3.5" or "gpt-4" in model:
        api_key = random.choice(full_api_key)
        base_url = "aigcbest.top"
    else:
        api_key = full_api_key
        base_url = "https://api2.aigcbest.top/v1"
    
    messages = [
        {
            "role": "user", 
            "content": prompt
        }
    ]

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": model,
        "messages": messages,
        "response_format": {
            "type": "json_object"
        },
    }
    gpt_responses = None
    retry_num = 0
    retry_limit = 2
    error = None
    while gpt_responses is None:
        try:
            conn = http.client.HTTPSConnection(base_url)
            conn.request("POST", "/v1/chat/completions", json.dumps(payload), headers)
            res = conn.getresponse()
            if res.status == 200:
                data = res.read()
                gpt_responses = json.loads(data)  # 将返回的字节数据解析为JSON格式
                error = None
        except Exception as e:
            print(str(e), flush=True)
            error = str(e)
            if "This model's maximum context length is" in str(e):
                print(e, flush=True)
                gpt_responses = {
                    "choices": [{"message": {"content": "PLACEHOLDER"}}]
                }
            elif retry_num > retry_limit:
                error = "too many retry times"
                gpt_responses = {
                    "choices": [{"message": {"content": "PLACEHOLDER"}}]
                }
            else:
                time.sleep(60)
            retry_num += 1
    if error:
        raise Exception(error)
    
    return gpt_responses["choices"][0]['message']['content']

'''
def is_chinese_name(name):
    # 常见姓氏列表
    common_surnames = {"王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗", "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧", "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕", "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎", "余", "潘", "杜", "戴", "夏", "钟", "汪", "田", "任", "姜", "范", "方", "石", "姚", "谭", "廖", "邹", "熊", "金", "陆", "郝", "孔", "白", "崔", "康", "毛", "邱", "秦", "江", "史", "顾", "侯", "邵", "孟", "龙", "万", "段", "雷", "钱", "汤", "尹", "黎", "易", "常", "武", "乔", "贺", "赖", "龚", "文"}

    if name == '金额' or name == '项目':
        return False
    # 检查名字长度
    if len(name) < 2 or len(name) > 3:
        return False

    # 检查姓氏
    if name[0] in common_surnames:
        return True

    return False

def is_chinese(string):
    # 匹配中文字符的正则表达式
    pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(pattern.search(string))
'''

def main(base_dir: str):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    # base_dir = "发票医疗数据1"
    access_token = '24.764a381ec05838653e4b75d1656922f5.2592000.1731759611.282335-115908367'

    logs = []
    for file in os.listdir(base_dir)[:2]:
        try:
            filename = os.path.join(base_dir, file)
            f = open(filename, 'rb')
            img = base64.b64encode(f.read())

            params = {"image":img}
            request_url = request_url + "?access_token=" + access_token
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers).json()
            response = [item['words'] for item in response['words_result']]
            llm_res = llm_gen(prompt = prompt(words=response), model = "gpt-4o")
            llm_res = json.loads(llm_res)
            logs.append(llm_res)
            print(llm_res)
        except:
            continue
    
    cur_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    with open(f'result_ocr&agent_{cur_time}.json', 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(logs, ensure_ascii=False))
        fp.close()


if __name__ == '__main__':
    fire.Fire(main)


        # if response:
        #     try:
        #         res = response.json()['words_result']
        #         after_pro = False
        #         after_he = False
        #         hospital = True
        #         for i, item in enumerate(res):
        #             try:
        #                 if '项' in item['words']:
        #                     after_pro = True
        #                 if '合' in item['words']:
        #                     after_he = True
        #                 if '门诊' in item['words']:
        #                     json_res['门诊号'] = item['words'][4:]
        #                 elif '据号' in item['words']:
        #                     json_res['票据号'] = item['words'][4:]
        #                 elif i < 6 and len(item['words']) > 10 and '门诊' not in item['words']:
        #                     json_res['票据头'] = item['words']
        #                 elif hospital and '医院' in item['words']:
        #                     json_res['医疗机构'] = item['words']
        #                     hospital = False
        #                 elif len(item['words']) == 10:
        #                     try:
        #                         int(item['words'])
        #                         json_res['业务流水号'] = item['words']
        #                     except:
        #                         pass
        #                 elif '费医疗' in item['words']:
        #                     if '百' in item['words']:
        #                         json_res['医保类型'] = '自费医疗'
        #                     else:
        #                         json_res['医保类型'] = item['words']
        #                 elif is_chinese_name(item['words']):
        #                     json_res['姓名'] = item['words']
        #                 elif after_pro and len(item['words']) >= 3:
        #                     json_res['项目'] = item['words']
        #                     after_pro = False
        #                 elif '-' in item['words'] and ':' in item['words']:
        #                     json_res['就诊时间'] = item['words']
        #                 elif after_he:
        #                     try:
        #                         money = int(item['words'])
        #                         if money > 0:
        #                             json_res['合计金额'] = item['words']
        #                         after_he = False
        #                     except:
        #                         pass
        #             except:
        #                 continue
        #     except:
        #         continue
                
        # logs.append(json_res)

        # print(json_res)
    
    # with open('result1.json', 'w', encoding='utf-8') as fp:
    #     fp.write(json.dumps(logs, ensure_ascii=False))
    #     fp.close()
                

