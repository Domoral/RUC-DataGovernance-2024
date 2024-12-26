import pandas as pd

# 读取CSV文件
df = pd.read_csv('./data/医院A/InpatientData.csv')

# 定义脱敏函数
def mask_name(name):
    return name[0] + '*' * (len(name) - 1)

def mask_id(id_number):
    return str(id_number)[:4] + '*' * (len(str(id_number)) - 8) + str(id_number)[-4:]

def mask_address(address):
    return '*' * len(address)

# 应用脱敏函数
df['姓名'] = df['姓名'].apply(mask_name)
df['身份证号'] = df['身份证号'].apply(mask_id)
df['住址'] = df['住址'].apply(mask_address)

# 保存脱敏后的数据到新文件
df.to_csv('data/医院A/InpatientData_masked.csv', index=False)

