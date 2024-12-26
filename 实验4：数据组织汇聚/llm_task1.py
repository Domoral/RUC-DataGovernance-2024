
# encoding:utf-8

import requests
import http.client
import random
import json
import time
from config.apikey import half_api_key, full_api_key
import pandas as pd
from datetime import datetime
import os


def prompt(standard, columns):
    template = """You are a data mapping expert specialized in healthcare data standardization. You are working on aligning different hospitals' outpatient data formats with a standard data model. Each hospital may use different column names to represent the same information, so you need to map non-standard hospital data columns to standard data model columns.
The standard data model is {standard_data_model}.
The hospital's current data uses these column names: {hospital_data_columns}.

Please create a mapping dictionary where:
    - Keys are the hospital's current column names
    - Values are the matching standard column names
The size of standard data model may be not equal to the hospital's current data columns. You should try your best to map the hospital's current data columns to the standard data model. If no clear match exists, you can return the key as the value of the key.
The size of your output should be equal to the size of the hospital_data_columns.

Please format your output as following JSON format:
```json
{{
    '<hospital key 1>': '<standard key 1>',
    '<hospital key 2>': '<standard key 2>',
    ...
}}
```

Here is an example:
input:
    standard_data_model: ['医院名', '门诊ID', '病患姓名', '病患身份证号', '就诊日期', '就诊科室', '诊断结果', '处方信息']
    hospital_data_columns: ['医院名称', '就诊ID', '病人姓名', '病人身份证号', '就诊日期', '就诊科室', '诊断信息', '处方']

output:
```json
{{
    '医院名称': '医院名',
    '就诊ID': '门诊ID',
    '病人姓名': '病患姓名',
    '病人身份证号': '病患身份证号',
    '就诊日期': '就诊日期',
    '就诊科室': '就诊科室',
    '诊断信息': '诊断结果',
    '处方': '处方信息'
}}
```
"""
    return template.format(standard_data_model=standard, hospital_data_columns=columns)

def prompt_decide(standard, columns, results):
    template = """You are a data mapping expert specialized in healthcare data standardization. You are working on aligning different hospitals' outpatient data formats with a standard data model.
Some experts have did this work and created some mapping dictionaries. Your task is evaluating the best one of these mapping dictionaries.

The standard data model is: {standard_data_model}.
The hospital's current data uses these column names: {hospital_data_columns}.
The mapping dictionaries is: {results}

Please evaluate these dictionaries and select the best one.
Format your returns as following:
```json
{{
    'reason': '<Express your reason about why you choose this dictionary>'
    'result': <Fill in the index of the dictionary you choose from the given mapping dictionaries list>
}}
```

Example:
input:
    standard_data_model: ['医院名', '门诊ID', '病患姓名', '病患身份证号', '就诊日期', '就诊科室', '诊断结果', '处方信息']
    hospital_data_columns: ['医院名称', '就诊ID', '病人姓名', '病人身份证号', '就诊日期', '就诊科室', '诊断信息', '处方']
    results:[
        {{
            '医院名称': '医院名',
            '就诊ID': '门诊ID',
            '病人姓名': '病患姓名',
            '病人身份证号': '病患身份证号',
            '就诊日期': '就诊日期',
            '就诊科室': '就诊科室',
            '诊断信息': '诊断结果',
            '处方': '处方信息'
        }},
        {{
            '医院名称': '医院名',
            '就诊ID': '门诊ID',
            '病人姓名': '患者姓名',
            '病人身份证号': '患者身份证号',
            '就诊日期': '就诊时间',
            '就诊科室': '就诊科室',
            '诊断信息': '诊断结果',
            '处方': '处方信息'
        }},
    ]
output:
```json
{{
    'reason': '<You should analyze the mapping dictionaries and give your own reason so I don't give you this example>'
    'result': 0
}}
"""
    return template.format(
        standard_data_model=standard, 
        hospital_data_columns=columns,
        results=results
    )



def llm_gen(prompt, model='gpt-4o', format='json'):
    
    if  "gpt-4" in model or 'claude' in model:
        api_key = random.choice(full_api_key)
        base_url = "api2.aigcbest.top"
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
            "type": "json_object" if format == 'json' else "text"
        },
        "temperature": 0.7,
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

def main(dir='医院A', sample_time=2):
    # if dataType not in ['OutpatientData', 'InpatientData', 'ExaminationData', 'ExpenseData']:
    #     raise ValueError("dataType must be one of ['OutpatientData', 'InpatientData', 'ExaminationData', 'ExpenseData']")
    
    with open(f"task1_data/standard.json", "r", encoding='utf-8') as f:
        standard = json.loads(f.read())

    base_dir = f'data/{dir}'
    for i, file in enumerate(os.listdir(base_dir)):
        try:
            hospital_data = pd.read_csv(f'{base_dir}/{file}')
            columns = hospital_data.columns.tolist()
            
            dataType = file.split('.')[0]
            if dataType != 'InpatientData':
                continue
            if dataType not in ['OutpatientData', 'InpatientData', 'ExaminationData', 'ExpenseData']:
                continue
            
            # multi-sampling
            samples = []
            for _ in range(sample_time):
                prompt_text = prompt(standard[dataType], columns)
                res = json.loads(llm_gen(prompt_text))
                samples.append(res)
                # print(samples)
            # select best
            prompt_desion = prompt_decide(
                standard=standard[dataType],
                columns=columns,
                results=samples
            )
            res_best = json.loads(llm_gen(prompt_desion))
            print(res_best)
            res_best = samples[int(res_best['result'])]

            updated_data = hospital_data.rename(columns=res_best, errors='ignore')
            updated_data.to_csv(f'task1_data/Multi/{dir}-{dataType}-multi.csv', index=False)
        except Exception as e:
            print(f'Error:{e}')
        print(f"Turn {i}")
        
        
    



if __name__ == '__main__':
    main()
    
    '''  后续处理
    df = pd.read_csv('task1_data\Multi\医院B-OutpatientData-multi.csv')
    df[['就诊日期','就诊时间']] = df['就诊时间'].str.split(' ', expand=True)
    df.to_csv('task1_data/process/医院B-OutpatientData-multi.csv', index=False)
    '''
    
   


