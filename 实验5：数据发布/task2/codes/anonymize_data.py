import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class KACAAnonymizer:
    def __init__(self, k=3):
        self.k = k
        
    def calculate_information_gain(self, data, attribute):
        """计算信息增益"""
        total_records = len(data)
        if total_records == 0:
            return 0
        
        # 对于数值型属性，先进行离散化
        if data[attribute].dtype in ['int64', 'float64']:
            # 使用10个分箱
            data_discretized = pd.qcut(data[attribute], q=10, duplicates='drop')
            value_counts = data_discretized.value_counts()
        else:
            value_counts = data[attribute].value_counts()
            
        probabilities = value_counts / total_records
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy
    
    def determine_attribute_weights(self, data, quasi_identifiers):
        """确定属性权重"""
        weights = {}
        total_gain = 0
        
        for attribute in quasi_identifiers:
            gain = self.calculate_information_gain(data, attribute)
            weights[attribute] = gain
            total_gain += gain
        
        if total_gain > 0:
            for attribute in weights:
                weights[attribute] /= total_gain
        else:
            # 如果总增益为0，则平均分配权重
            for attribute in weights:
                weights[attribute] = 1.0 / len(quasi_identifiers)
                
        return weights
    
    def anonymize_numeric(self, group, attribute):
        """对数值型属性进行匿名化"""
        min_val = group[attribute].min()
        max_val = group[attribute].max()
        return f"[{min_val:.1f}-{max_val:.1f}]"
    
    def anonymize_categorical(self, group, attribute):
        """对分类型属性进行匿名化"""
        values = group[attribute].unique()
        if len(values) == 1:
            return values[0]
        return "|".join(sorted(values))
    
    def anonymize(self, data, quasi_identifiers):
        """主要的匿名化过程"""
        # 数据预处理
        numeric_columns = ['年龄', '身高(cm)', '体重(kg)']
        categorical_columns = ['性别', '住址']
        
        # 创建用于聚类的数据副本
        clustering_data = data.copy()
        
        # 标准化数值型属性
        scaler = StandardScaler()
        clustering_data[numeric_columns] = scaler.fit_transform(data[numeric_columns])
        
        # 对分类属性进行标签编码
        for col in categorical_columns:
            clustering_data[col] = pd.Categorical(clustering_data[col]).codes
        
        # 计算属性权重
        weights = self.determine_attribute_weights(data, quasi_identifiers)
        
        # 应用权重到聚类数据
        for col in quasi_identifiers:
            clustering_data[col] = clustering_data[col].astype(float) * weights[col]
        
        # 使用KMeans进行聚类
        n_clusters = max(len(data) // self.k, 1)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(clustering_data[quasi_identifiers])
        
        # 对每个簇进行匿名化
        data['cluster'] = clusters
        anonymized_data = data.copy()
        
        for cluster_id in range(n_clusters):
            cluster_group = data[data['cluster'] == cluster_id]
            
            if len(cluster_group) < self.k:
                continue
                
            # 对数值型属性进行范围替换
            for col in numeric_columns:
                anonymized_value = self.anonymize_numeric(cluster_group, col)
                anonymized_data.loc[cluster_group.index, col] = anonymized_value
            
            # 对分类型属性进行泛化
            for col in categorical_columns:
                anonymized_value = self.anonymize_categorical(cluster_group, col)
                anonymized_data.loc[cluster_group.index, col] = anonymized_value
        
        anonymized_data = anonymized_data.drop('cluster', axis=1)
        return anonymized_data

def main():
    # 定义输入输出文件路径
    input_file = "./data/医院A/InpatientData_masked.csv"
    output_file = "./data/医院A\InpatientData_anonymized.csv"
    
    try:
        # 读取CSV文件
        print("正在读取数据...")
        data = pd.read_csv(input_file, encoding='utf-8')
        print(f"成功读取数据，共 {len(data)} 条记录")
        
        # 定义准标识符
        quasi_identifiers = ['年龄', '身高(cm)', '体重(kg)', '性别', '住址']
        
        # 检查数据中是否包含所有必要的列
        missing_columns = [col for col in quasi_identifiers if col not in data.columns]
        if missing_columns:
            raise ValueError(f"数据中缺少以下列: {missing_columns}")
        
        # 数据预处理
        # 确保数值型列的数据类型正确
        data['年龄'] = pd.to_numeric(data['年龄'], errors='coerce')
        data['身高(cm)'] = pd.to_numeric(data['身高(cm)'], errors='coerce')
        data['体重(kg)'] = pd.to_numeric(data['体重(kg)'], errors='coerce')
        
        # 去除包含空值的行
        initial_rows = len(data)
        data = data.dropna(subset=quasi_identifiers)
        dropped_rows = initial_rows - len(data)
        if dropped_rows > 0:
            print(f"警告：删除了 {dropped_rows} 行包含空值的数据")
        
        # 创建匿名器并执行匿名化
        print("开始执行匿名化...")
        anonymizer = KACAAnonymizer(k=3)
        anonymized_data = anonymizer.anonymize(data, quasi_identifiers)
        
        # 保存结果
        anonymized_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"匿名化完成，结果已保存到: {output_file}")
        
        # 输出匿名化效果统计
        print("\n匿名化效果统计:")
        print("-" * 50)
        for col in quasi_identifiers:
            original_unique = len(data[col].unique())
            anonymized_unique = len(anonymized_data[col].unique())
            print(f"{col}:")
            print(f"  原始唯一值数量: {original_unique}")
            print(f"  匿名化后唯一值数量: {anonymized_unique}")
            print(f"  信息损失率: {((original_unique - anonymized_unique) / original_unique * 100):.2f}%")
        
        # 显示部分匿名化结果
        print("\n匿名化结果样例（前5行）:")
        print("-" * 50)
        print(anonymized_data[quasi_identifiers].head())
        
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
    except Exception as e:
        print(f"错误：{str(e)}")

if __name__ == "__main__":
    main()