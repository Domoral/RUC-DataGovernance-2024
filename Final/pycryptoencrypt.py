from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import csv
import os

def generate_key():
    return get_random_bytes(32)

def encrypt_aes(plain_text, key):
    """
    AES加密函数
    :param plain_text: 明文字符串
    :param key: 16位、24位或32位密钥
    :return: 加密后的base64字符串
    """
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plain_text.encode('utf-8'), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def decrypt_aes(encrypted_text, key):
    """
    AES解密函数
    :param encrypted_text: 加密后的base64字符串
    :param key: 16位、24位或32位密钥
    :return: 解密后的明文
    """
    # base64解码
    encrypted_data = base64.b64decode(encrypted_text)
    # 提取IV和密文
    iv = encrypted_data[:AES.block_size]
    cipher_text = encrypted_data[AES.block_size:]
    # 创建cipher对象
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 解密
    padded_data = cipher.decrypt(cipher_text)
    # 去除填充
    return unpad(padded_data, AES.block_size).decode('utf-8')

def encrypt_csv(input_file, output_file, columns_to_encrypt, key):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            for col in columns_to_encrypt:
                row[col] = encrypt_aes(row[col], key)
            writer.writerow(row)

def encrypt_csv_files():
    # 使用固定密钥
    key = generate_key()
    
    # 保存密钥到文件
    with open('crypto_key.bin', 'wb') as f:
        f.write(key)
    
    # 定义需要处理的文件和对应的加密列
    files_config = {
        'archive': {
            'path': 'dataTemp/archive',
            'columns': ['学号', '证件号', '姓名']
        },
        'college': {
            'path': 'dataTemp/college', 
            'columns': ['学号', '姓名']
        },
        'edu_admin': {
            'path': 'dataTemp/edu_admin',
            'columns': ['学号', '姓名']
        }
    }
    
    for folder, config in files_config.items():
        base_path = config['path']
        columns = config['columns']
        
        # 处理Student.csv
        input_path = f"{base_path}/Student.csv"
        output_path = f"{base_path}/Student_encrypted.csv"
        if os.path.exists(input_path):
            encrypt_csv(input_path, output_path, columns, key)
            
        # 处理FStudent.csv 
        input_path = f"{base_path}/FStudent.csv"
        output_path = f"{base_path}/FStudent_encrypted.csv"
        if os.path.exists(input_path):
            
            f_columns = ['学号', '证件号', '姓名'] if folder == 'archive' else ['学号', '姓名']
            encrypt_csv(input_path, output_path, f_columns, key)

if __name__ == '__main__':
    encrypt_csv_files()