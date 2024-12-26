# gpt调用
from openai import OpenAI
client = OpenAI()

def chatgpt(modelname,sys_txt,task):
    response = client.chat.completions.create(
        model=modelname,
        #response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": sys_txt},
            {"role": "user", "content": task}
        ]
    )

    return response