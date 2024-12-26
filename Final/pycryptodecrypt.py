from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import csv
import os

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

def decrypt_csv(input_file, output_file, columns_to_decrypt, key):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            for col in columns_to_decrypt:
                row[col] = decrypt_aes(row[col], key)
            writer.writerow(row)

def decrypt_csv_files():
    
    with open('crypto_key.bin', 'rb') as f:
        key = f.read()
    
    
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
        input_path = f"{base_path}/Student_encrypted.csv"
        output_path = f"{base_path}/Student_decrypted.csv"
        if os.path.exists(input_path):
            decrypt_csv(input_path, output_path, columns, key)
            
        # 处理FStudent.csv
        input_path = f"{base_path}/FStudent_encrypted.csv"
        output_path = f"{base_path}/FStudent_decrypted.csv"
        if os.path.exists(input_path):
            # FStudent可能使用不同的列名
            f_columns = ['学号', '证件号', '姓名'] if folder == 'archive' else ['学号', '姓名']
            decrypt_csv(input_path, output_path, f_columns, key)

if __name__ == '__main__':
    decrypt_csv_files()