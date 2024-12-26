import random
import time
import json
import http.client
from config.apikey import full_api_key

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