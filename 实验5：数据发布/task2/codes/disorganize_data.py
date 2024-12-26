import pandas as pd
import numpy as np
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

class DifferentialPrivacy:
    def __init__(self, epsilon: float = 1.0):
        """
        初始化差分隐私类
        :param epsilon: 隐私预算参数，较小的值提供更强的隐私保护但降低数据效用
        """
        self.epsilon = epsilon
        
    def add_laplace_noise(self, value: float, sensitivity: float) -> float:
        """
        添加拉普拉斯噪声
        :param value: 原始值
        :param sensitivity: 敏感度
        :return: 添加噪声后的值
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def perturb_categorical(self, values: pd.Series, categories: List[str] = None) -> pd.Series:
        """
        对分类数据进行扰动
        :param values: 原始分类数据
        :param categories: 可能的分类列表
        :return: 扰动后的数据
        """
        if categories is None:
            categories = values.unique().tolist()
            
        # 计算每个值被替换的概率
        prob_matrix = np.zeros((len(categories), len(categories)))
        keep_prob = 0.7  # 保持原值的概率
        change_prob = (1 - keep_prob) / (len(categories) - 1)  # 改变为其他值的概率
        
        for i in range(len(categories)):
            for j in range(len(categories)):
                if i == j:
                    prob_matrix[i][j] = keep_prob
                else:
                    prob_matrix[i][j] = change_prob
        
        # 对每个值进行扰动
        result = values.copy()
        for idx in result.index:
            original_cat = result[idx]
            if original_cat in categories:
                orig_idx = categories.index(original_cat)
                result[idx] = np.random.choice(categories, p=prob_matrix[orig_idx])
                
        return result
    
    def perturb_numeric(self, values: pd.Series, sensitivity: float) -> pd.Series:
        """
        对数值数据进行扰动
        :param values: 原始数值数据
        :param sensitivity: 敏感度
        :return: 扰动后的数据
        """
        return values.apply(lambda x: self.add_laplace_noise(x, sensitivity))

class DataPerturber:
    def __init__(self, epsilon: float = 1.0):
        self.dp = DifferentialPrivacy(epsilon)
        
    def get_numeric_sensitivity(self, data: pd.Series) -> float:
        """
        计算数值型数据的敏感度
        """
        return (data.max() - data.min()) * 0.01  # 使用数据范围的1%作为敏感度
        
    def perturb_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        对数据进行扰动
        :param data: 原始数据框
        :return: 扰动后的数据框
        """
        result = data.copy()
        
        # 定义需要扰动的字段及其类型
        numeric_fields = ['年龄', '身高(cm)', '体重(kg)', '医疗费用']
        categorical_fields = ['性别', '科室', '诊断结果']
        
        # 处理数值型字段
        for field in numeric_fields:
            if field in result.columns:
                # 将区间格式的数据转换为数值
                if result[field].dtype == 'object' and result[field].str.contains('-').any():
                    # 提取区间的中间值
                    result[field] = result[field].apply(lambda x: 
                        float(x.replace('[', '').replace(']', '').split('-')[0]) 
                        if isinstance(x, str) and '-' in x 
                        else float(x))
                
                # 确保数据为数值类型
                result[field] = pd.to_numeric(result[field], errors='coerce')
                
                # 计算敏感度并添加噪声
                sensitivity = self.get_numeric_sensitivity(result[field])
                result[field] = self.dp.perturb_numeric(result[field], sensitivity)
                
                # 对年龄进行取整
                if field == '年龄':
                    result[field] = result[field].round().astype(int)
        
        # 处理分类型字段
        for field in categorical_fields:
            if field in result.columns:
                result[field] = self.dp.perturb_categorical(result[field])
        
        return result

def main():
    # 文件路径
    input_file = "./data/医院A/InpatientData_masked.csv"
    output_file = "./data/医院A\InpatientData_anonymized.csv"
    try:
        # 读取数据
        print("正在读取数据...")
        data = pd.read_csv(input_file, encoding='utf-8')
        print(f"成功读取数据，共 {len(data)} 条记录")
        
        # 创建数据扰动器
        perturber = DataPerturber(epsilon=1.0)
        
        # 执行数据扰动
        print("正在进行差分隐私处理...")
        perturbed_data = perturber.perturb_data(data)
        
        # 保存结果
        perturbed_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"差分隐私处理完成，结果已保存到: {output_file}")
        
        # 输出统计信息
        numeric_fields = ['年龄', '身高(cm)', '体重(kg)', '医疗费用']
        categorical_fields = ['性别', '科室', '诊断结果']
        
        print("\n数据扰动效果统计:")
        print("-" * 50)
        
        print("\n数值型字段统计:")
        for field in numeric_fields:
            if field in data.columns:
                original_mean = pd.to_numeric(data[field], errors='coerce').mean()
                perturbed_mean = perturbed_data[field].mean()
                print(f"\n{field}:")
                print(f"  原始平均值: {original_mean:.2f}")
                print(f"  扰动后平均值: {perturbed_mean:.2f}")
                print(f"  相对变化: {abs(perturbed_mean - original_mean) / original_mean * 100:.2f}%")
        
        print("\n分类型字段统计:")
        for field in categorical_fields:
            if field in data.columns:
                original_unique = len(data[field].unique())
                perturbed_unique = len(perturbed_data[field].unique())
                print(f"\n{field}:")
                print(f"  原始唯一值数量: {original_unique}")
                print(f"  扰动后唯一值数量: {perturbed_unique}")
        
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
    except Exception as e:
        print(f"错误：{str(e)}")

if __name__ == "__main__":
    main()