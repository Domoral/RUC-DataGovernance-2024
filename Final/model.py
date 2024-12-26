from openai import OpenAI
import aiohttp
import asyncio
import numpy as np
import random
from config.apikey import full_api_key

model_name = None
total_prompt_tokens = 0
total_completion_tokens = 0
call_count = 0
semaphore = asyncio.Semaphore(5)
session = None  # 全局会话变量


async def get_session():
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    return session


async def llm_gen(
    prompt,
    # model="gpt-3.5-turbo-0125",
    # model="gpt-4o",
    model="gpt-4o",
    system_prompt=None,
    format="json",
    temperature=None,
):
    global total_prompt_tokens
    global total_completion_tokens
    global call_count
    global model_name

    model_name = model
    call_count += 1

    if "gpt-3.5" or "gpt-4o" in model:
        api_key = random.choice(full_api_key)
        base_url = "https://api2.aigcbest.top/v1"
    else:
        api_key = full_api_key
        base_url = "https://api2.aigcbest.top/v1"
    message = []

    if system_prompt:
        message.append({"role": "system", "content": system_prompt})
    message.append({"role": "user", "content": prompt})

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": message}

    if format == "json":
        data["response_format"] = {"type": "json_object"}
    if temperature is not None:
        data["temperature"] = temperature

    global semaphore, session
    max_retries = 10
    retries = 0
    es = []
    while retries < max_retries:
        retries += 1
        try:
            async with semaphore:  # 使用信号量限制并发
                session = await get_session()  # 获取或创建会话
                async with session.post(
                    f"{base_url}/chat/completions", headers=headers, json=data
                ) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        total_prompt_tokens += response.get("usage", {}).get(
                            "prompt_tokens", 0
                        )
                        total_completion_tokens += response.get("usage", {}).get(
                            "completion_tokens", 0
                        )
                        await close_session()
                        return response["choices"][0]["message"]["content"]
                    else:
                        resp.raise_for_status()  # 如果响应状态不是200，抛出异常
        except aiohttp.ClientResponseError as e:
            if e.status == 500:
                # print(f"HTTP Error: 500, retrying {retries}/{max_retries}")
                es.append(f"HTTP Error: 500")
                await asyncio.sleep(0.1)  # 等待一段时间后重试
            else:
                # print(Exception(f"HTTP Error: {e.status}, retrying {retries}/{max_retries}"))
                es.append(f"HTTP Error: {e.status}")
                await asyncio.sleep(0.1)  # 等待一段时间后重试
        except Exception as e:
            es.append(f"Error: {e}")
            # print(f"Error: {e}, retrying {retries}/{max_retries}")
            await asyncio.sleep(0.1)  # 等待一段时间后重试
    print(
        "Failed to get response after {} retries\nError log:{}".format(max_retries, es)
    )


# 在程序结束时关闭会话
async def close_session():
    global session
    if session:
        await session.close()