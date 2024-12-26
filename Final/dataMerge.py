import os
import asyncio
import sys
import fire
import pandas as pd
import json
from model import llm_gen

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def create_api_config(api_key):
    try:
        if not os.path.exists('config1'):
            os.makedirs('config1')
            with open('config1/apikey.py', 'w') as f:
                f.write(f'full_api_key = [\"{api_key}\"]')
            return True
        return True
    except Exception as e:
        print(f"Error creating API config: {e}")
        return False
    
class DataMergePrompt:
    def __init__(self):
        pass

    def attributeMatch(self, en_attr, cn_attr):
        template = """你是一个专业的数据库专家。我会给你两组数据：
1. 一个英文属性列表，这是我的表中现有的属性
2. 一个中文属性列表，这是可能的目标属性（可能包含一些与表无关的属性）

请你将英文属性与最匹配的中文属性进行配对，要求：
1. JSON的键为英文属性，值为对应的中文属性
2. 必须为每个英文属性都找到对应的中文属性
3. 如果某个英文属性没有完全匹配的中文属性，选择最接近的含义
4. 返回的JSON数量必须与英文属性数量相同
5. 严格返回JSON，不要其他解释

返回格式:
```json
{{
    "en_attr1": "cn_attr1",
    "en_attr2": "cn_attr2",
    ...
    "cause": "匹配原因"
}}
```

下面是个例子:
英文属性：[name, age, gender, Mjob, Fjob]
中文属性：[姓名, 年龄, 性别, 身高, 体重, 父亲工作, 母亲工作]
你应该返回：
{{
    "name": "姓名",
    "age": "年龄",
    "gender": "性别",
    "Mjob": "母亲工作",
    "Fjob": "父亲工作",
    "cause": "name的含义是姓名，age的含义是年龄，gender的含义是性别; Mjob结合中文属性猜测为Mother_Job, 含义为母亲工作; Fjob结合中文属性猜测为Father_Job, 含义为父亲工作"
}}

现在我给出我的英文属性列表和中文属性列表，请你返回配对结果:
英文属性：{en_attr}
中文属性：{cn_attr}
"""
        return template.format(en_attr=en_attr, cn_attr=cn_attr)
    
    def attributeChoose(self, tableCn, tableEn):
        template = """你是一个专业的数据库专家。我会给你两张表,两张表的属性匹配,其中一张表的属性可能稍多一些.你需要考虑的是:
两张表的相同属性下的数据项可能存在中英文结构化对应的关系,比如表A和表B的属性'性别'下,表A的项只有'男'和'女',而表B的项只有'M'和'F',那么两张表的'性别'属性是有中英文结构化对应的关系的.
而另一些属性,
1.如'姓名',虽然表A全为中文,表B全为英文,然而是没有结构化对应关系的还有一些属性
2.如'受教育水平',两张表的项都是较小的阿拉伯数字,也是没有这种关系的.
你需要做的是:
1. 观察发现两张表可以构成结构化对应关系的属性
2. 返回这些属性的列表

请严格按下面的JSON格式返回,不要返回任何无关内容:
```json
{{
    "selected": ["attr1", "attr2", ...],
    "cause": "选择原因"
}}
```

下面是一个例子:
表A:
姓名,性别,年龄,居住地,已婚,受教育水平
周建华,男,20,城市,否,3
彭勇,男,21,城市,否,3
董建平,男,22,农村,是,2
曾语涵,女,23,农村,否,1

表B:
姓名,性别,年龄,居住地,已婚,受教育水平
Alice,F,25,U,yes,3
Bob,M,26,R,yes,3
Carol,F,26,U,no,2

你应该返回:
```json
{{
    "selected": ["性别", "居住地"],
    "cause": "性别的项目在表A中为'男'和'女',在表B中为'M'和'F',存在中英文结构化对应关系; 居住地的项目在表A中为'城市'和'农村',在表B中为'U'和'R',存在中英文结构化对应关系;而其他属性都是没有这种关系的"
}}
```

现在我给出两张表,请你返回配对结果:
表A:
{tableCn}
表B:
{tableEn}
"""
        return template.format(tableCn=tableCn, tableEn=tableEn)

    def attrDetailMatch(self, attr, attrDetail1, attrDetail2):
        template = """你是一个专业的数据库专家。我会给你一个属性，以及两张表的该属性下的数据项。你需要做的是：
1. 观察发现两张表的该属性下的数据项的中英文结构化对应的关系, 如性别属性下的'男'和'女'与'M'和'F'存在中英文结构化对应关系
2. 返回你观察得到的中英文结构化对应字典

请严格按下面的JSON格式返回,不要返回任何无关内容:
```json
{{
    "dict": {{"attrDetail1": "attrDetail2", ...}},
    "cause": "观察到中英文结构化对应关系的原因"
}}
```

下面是一个例子:
属性: 性别
A表性别属性项细节: [男,女,女,女,男]
B表性别属性项细节: [M,F,M,M,F]

你应该返回:
```json
{{
    "dict": {{"男": "M", "女": "F"}},
    "cause": "观察到性别属性下的'男'和'女'与'M'(man)和'F'(female)存在中英文结构化对应关系"
}}
```

现在我给出属性,以及两张表的该属性下的数据项,请你返回配对结果:
属性: {attr}
A表{attr}属性项细节: {attrDetail1}
B表{attr}属性项细节: {attrDetail2}
"""
        return template.format(attr=attr, attrDetail1=attrDetail1, attrDetail2=attrDetail2)
    

class DataMerge:
    def __init__(self):
        pass

    def extract_json(self, string):  # 从response中提取json数据，提取失败则返回错误信息
        try:  # json mode的output
            string = string.strip()
            json_data = json.loads(string)
            return json_data
        except Exception as e:
            return str(e)

    async def attrMatch(self, en_file, cn_file):
        while True:
            en_df = pd.read_csv(en_file)
            cn_df = pd.read_csv(cn_file)
            en_attr = en_df.columns.tolist()
            cn_attr = cn_df.columns.tolist()
            prompt = DataMergePrompt().attributeMatch(en_attr, cn_attr)
            res = await llm_gen(prompt=prompt, format='json')
            attr_json = self.extract_json(res)
            print(attr_json)
            en_df = en_df.rename(columns=attr_json)
            print(en_df.head())
            if input('OK?[y]/n').lower() == 'y':
                break
        en_df.to_csv(en_file, index=False)

    async def attrDetailMatch(self, attr, attrDetail1, attrDetail2):
        prompt = DataMergePrompt().attrDetailMatch(attr, attrDetail1, attrDetail2)
        res = await llm_gen(prompt=prompt, format='json')
        res_json = self.extract_json(res)
        print(res_json)
        d = res_json['dict']
        return {attr: d}
    
    async def attrDetailMatchFlow(self, cn_file, en_file):
        cn_df = pd.read_csv(cn_file)
        en_df = pd.read_csv(en_file)
        attrs = cn_df.columns.tolist()
        attrs1 = en_df.columns.tolist()
        assert set(attrs).issubset(set(attrs1)) or set(attrs1).issubset(set(attrs)), '两张表的属性不匹配'
        cn_smp = cn_df.sample(n=20)
        en_smp = en_df.sample(n=20)
        prompt = DataMergePrompt().attributeChoose(cn_smp.to_string(), en_smp.to_string())
        res = await llm_gen(prompt=prompt, format='json')
        res_json = self.extract_json(res)
        print(res_json)
        attrs = res_json['selected']
        callings = [self.attrDetailMatch(attr, cn_df[attr].tolist(), en_df[attr].tolist()) for attr in attrs]
        res = await asyncio.gather(*callings)
        for it in res:
            for attr, d in it.items():
                cn_df[attr] = cn_df[attr].replace(d)
        print(cn_df)
        # en_df.to_csv(en_file, index=False)
        cn_df.to_csv(cn_file, index=False)


async def llm():
    tableEn = pd.read_csv('data/archive/FStudent.csv').sample(n=20)
    tableCn = pd.read_csv('data/archive/Student.csv').sample(n=20)
    attr = '父母婚姻状况'
    attrDetail1 = tableCn['父母婚姻状况'].tolist()
    attrDetail2 = tableEn['Pstatus'].tolist()
    prompt = DataMergePrompt().attrDetailMatch(attr, attrDetail1, attrDetail2)
    print(prompt)
    res = await llm_gen(prompt=prompt, format='json')
    print(res)

def main(api_key=None):
    asyncio.run(DataMerge().attrMatch('dataTemp/edu_admin/FStudent.csv', 'dataTemp/edu_admin/Student.csv'))
    asyncio.run(DataMerge().attrDetailMatchFlow('dataTemp/edu_admin/Student.csv', 'dataTemp/edu_admin/FStudent.csv'))

if __name__ == '__main__':
    # api_key = 'sk-EVNW0dPB3noppWIm62076e39B4B7402998FcF0C6D007B72e'
    # create_api_config(api_key)

    # from config1.apikey import full_api_key
    # print(full_api_key)
    # fire.Fire(main)
    main()
    
    # main()
