from llm import llm_gen
import json
import os
import pandas as pd

def prompt(attrs):
    template = """As a medical data expert, please help me categorize the following patient attributes into meaningful clusters. Each attribute should be grouped based on its nature and relevance to patient care.
The attributes are: {attrs}
Please format your output as following JSON format(All cluster names should be in Chinese):
```json
{{
    '<cluster name 1>': ['<attribute 1>', '<attribute 2>', ...],
    '<cluster name 2>': ['<attribute 3>', '<attribute 4>', ...],
    ...
    'reason': '<Briefly explain why these attributes belong its cluster>'
}}
```

Here is an example:
Input:
    attributes: ['姓名', '住院时长', '所患疾病', '性别', '身份证号', '参保人', '参保ID', '赔付比例']
Output:
```json
{{
    '基本信息': ['姓名', '性别', '身份证号'],
    '诊疗信息': ['住院时长', '所患疾病'],
    '保险信息': ['参保人', '参保ID', '赔付比例'],
    'reason': '<You need analyse by yourself so I don't give you an example here>'
}}
```
"""
    return template.format(attrs=attrs)


def prompt_given(attrs, clusters):
    template = """As a medical data expert, please help me categorize the following patient attributes into clusters. Each attribute should be grouped based on its nature and relevance to patient care.
The attributes are: {attrs}
The clusters are: {clusters}
Please format your output as following JSON format(All cluster names should be in Chinese):
```json
{{
    '<cluster name 1>': ['<attribute 1>', '<attribute 2>', ...],
    '<cluster name 2>': ['<attribute 3>', '<attribute 4>', ...],
    ...
    'reason': '<Briefly explain why these attributes belong its cluster>'
}}
```

Here is an example:
Input:
    attributes: ['姓名', '住院时长', '所患疾病', '性别', '身份证号', '参保人', '参保ID', '赔付比例']
    clusters: ['基本信息', '诊疗信息', '保险信息']
Output:
```json
{{
    '基本信息': ['姓名', '性别', '身份证号'],
    '诊疗信息': ['住院时长', '所患疾病'],
    '保险信息': ['参保人', '参保ID', '赔付比例'],
    'reason': '<You need analyse by yourself so I don't give you an example here>'
}}
```
"""
    return template.format(attrs=attrs, clusters=clusters)

def main():
    attrs = []
    clusters = ['个人基本信息', '诊疗信息', '保单信息', '保险产品信息']
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    attrs += df.columns.tolist()
                except:
                    print(f"Reading {file_path} error")
    attrs = list(set(attrs))
    print(attrs)
    print(prompt_given(attrs=attrs, clusters=clusters))
    llm_res = llm_gen(
        prompt=prompt_given(attrs=attrs, clusters=clusters),
        format='json',
        model='gpt-4o'
    )
    json_res = json.loads(llm_res)
    del json_res['reason']
    print(json_res)
    with open('task3_given.json', 'w') as f:
        f.write(json.dumps(json_res, ensure_ascii=False))

if __name__ == '__main__':
    ''' test
    llm_res = llm_gen(
        prompt=prompt(attrs=['姓名','挂号时间','身份证号','负责科室'])
    )
    print(llm_res)
    '''
    main()