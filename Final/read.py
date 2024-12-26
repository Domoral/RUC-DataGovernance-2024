import pandas as pd
import random
import numpy as np

df = pd.read_csv('dataTemp/archive/Student.csv')

df['性别'] = df['性别'].replace({
    'M': '男',
    'F': '女'
})

print(df[['姓名', '性别']])
df.to_csv('dataTemp/archive/Student.csv', index=False)

# df = pd.read_csv('data/archive/FStudent2.csv')
# def generate_chinese_names(count=900):
#     # 常见姓氏
#     surnames = [
#         '张', '王', '李', '赵', '陈', '刘', '杨', '黄', '周', '吴',
#         '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
#         '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
#         '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕',
#         '苏', '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎'
#     ]
    
#     # 常见名字用字
#     name_chars = [
#         '伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
#         '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
#         '平', '刚', '桂英', '玲', '桂兰', '芬', '文', '云', '建华', '建国',
#         '建军', '建平', '建华', '国强', '国庆', '国华', '国平', '国文', '子豪', '子轩',
#         '浩然', '浩轩', '浩宇', '浩天', '宇轩', '志强', '志国', '志华', '志平', '志文',
#         '雨涵', '雨轩', '雨欣', '雨泽', '雨晴', '语晨', '语涵', '语蝶', '欣怡', '欣然',
#         '欣欣', '欣慧', '欣宜', '欣诺', '欣悦', '梦涵', '梦琪', '梦璐', '梦婷', '梦茜'
#     ]
    
#     names = []
#     used_names = set()  # 用于确保名字不重复
    
#     while len(names) < count:
#         surname = random.choice(surnames)
#         # if random.random() < 0.3:  # 30%概率生成单字名
#         name = surname + random.choice(name_chars)
#         # else:  # 70%概率生成双字名
#         #     name = surname + random.choice(name_chars) + random.choice(name_chars)
        
#         if name not in used_names:
#             used_names.add(name)
#             names.append(name)
    
#     return names

# COUNT = 1000
# columns = ['姓名', '学号', '挂科次数', 'gpa']
# df = pd.read_csv('data/archive/Student.csv')
# name = df['姓名'].tolist()
# sid = df['学号'].tolist()
# failure = [random.randint(0, 4) for _ in range(COUNT)]
# gpa = [round(random.uniform(3.0, 4.0), 2) for _ in range(COUNT)]

# df = pd.DataFrame(columns=columns, data=zip(name, sid, failure, gpa))
# print(df)
# df.to_csv('data/edu_admin/Student.csv', index=False)


# name = generate_chinese_names(COUNT)
# sid = ['2022'+str(i).zfill(6) for i in range(COUNT)]
# id = [str(random.randint(100000, 599999)) + 
#       random.choice(['2002', '2003', '2004', '2005']) +
#       random.choice(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']) +
#       random.choice(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28']) +
#       str(random.randint(0, 9999)).zfill(4)
#       for _ in range(COUNT)
#       ]
# school = ['RUC' for _ in range(COUNT)]
# sex = [random.choice(['M', 'F']) for _ in range(COUNT)]
# age = [2024-int(it[6:10]) for it in id]
# resident = [random.choice(['城市', '农村']) for _ in range(COUNT)]
# family_size = [random.choice(['LE3', 'GT3']) for _ in range(COUNT)]
# marry = [random.choice(['T', 'A']) for _ in range(COUNT)]
# M_edu = [random.randint(0, 4) for _ in range(COUNT)]
# F_edu = [random.randint(0, 4) for _ in range(COUNT)]
# jobs = [
#     'teacher',      # 教师
#     'doctor',       # 医生
#     'engineer',     # 工程师
#     'businessman',  # 商人
#     'civil_servant',# 公务员
#     'lawyer',       # 律师
#     'accountant',   # 会计
#     'manager',      # 经理
#     'worker',       # 工人
#     'self_employed', # 个体经营者
#     'at_home'
# ]
# M_job = [random.choice(jobs) for _ in range(COUNT)]
# F_job = [random.choice(jobs) for _ in range(COUNT)]

# df = pd.DataFrame(columns=columns, data=zip(name, sid, id, school, sex, age, resident, family_size, marry, M_edu, F_edu, M_job, F_job))
# print(df)
# df.to_csv('data/archive/Student.csv', index=False)


# english_names = [
#     'Aaron', 'Abigail', 'Adam', 'Adrian', 'Aidan', 'Alan', 'Albert', 'Alex', 'Alexander', 'Alice',
#     'Alicia', 'Allison', 'Alyssa', 'Amanda', 'Amber', 'Amy', 'Andrea', 'Andrew', 'Angela', 'Anna',
#     'Anthony', 'Antonio', 'April', 'Aria', 'Ariana', 'Arthur', 'Ashley', 'Audrey', 'Austin', 'Autumn',
#     'Ava', 'Avery', 'Bailey', 'Barbara', 'Benjamin', 'Beth', 'Bethany', 'Blake', 'Bradley', 'Brandon',
#     'Brandy', 'Brenda', 'Brian', 'Brittany', 'Brooke', 'Bruce', 'Bryan', 'Caitlin', 'Caleb', 'Cameron',
#     'Carl', 'Carmen', 'Carol', 'Caroline', 'Carolyn', 'Casey', 'Cassandra', 'Catherine', 'Cathy', 'Chad',
#     'Charles', 'Charlotte', 'Chelsea', 'Cheryl', 'Christian', 'Christina', 'Christine', 'Christopher', 'Claire', 'Clara',
#     'Claude', 'Claudia', 'Cody', 'Cole', 'Colin', 'Colton', 'Connie', 'Connor', 'Corey', 'Courtney',
#     'Craig', 'Crystal', 'Cynthia', 'Daisy', 'Dale', 'Daniel', 'Danielle', 'Danny', 'Darren', 'David',
#     'Dawn', 'Dean', 'Deborah', 'Debra', 'Dennis', 'Derek', 'Destiny', 'Diana', 'Diane', 'Donald',
#     'Donna', 'Dorothy', 'Douglas', 'Dylan', 'Earl', 'Edward', 'Edwin', 'Elaine', 'Elizabeth', 'Ellen',
#     'Emily', 'Emma', 'Eric', 'Erica', 'Erik', 'Erin', 'Ethan', 'Eugene', 'Eva', 'Evelyn',
#     'Faith', 'Felix', 'Florence', 'Frances', 'Francis', 'Frank', 'Franklin', 'Fred', 'Gabriel', 'Gary',
#     'George', 'Gerald', 'Gloria', 'Grace', 'Gregory', 'Hannah', 'Harold', 'Harry', 'Heather', 'Helen',
#     'Henry', 'Holly', 'Howard', 'Hunter', 'Ian', 'Irene', 'Isaac', 'Isabella', 'Jack', 'Jackson',
#     'Jacob', 'Jacqueline', 'Jade', 'James', 'Jamie', 'Jane', 'Janet', 'Janice', 'Jason', 'Jay',
#     'Jean', 'Jeffrey', 'Jennifer', 'Jeremy', 'Jerry', 'Jesse', 'Jessica', 'Jill', 'Jim', 'Jimmy',
#     'Joan', 'Joanne', 'Joe', 'John', 'Johnny', 'Jonathan', 'Jordan', 'Joseph', 'Joshua', 'Joyce',
#     'Juan', 'Judith', 'Judy', 'Julia', 'Julian', 'Julie', 'Justin', 'Karen', 'Katherine', 'Kathleen',
#     'Kathryn', 'Kathy', 'Katie', 'Keith', 'Kelly', 'Kenneth', 'Kevin', 'Kim', 'Kimberly', 'Kyle',
#     'Laura', 'Lauren', 'Lawrence', 'Leah', 'Lee', 'Leonard', 'Leslie', 'Linda', 'Lisa', 'Logan',
#     'Lois', 'Lori', 'Louis', 'Lucas', 'Lucy', 'Luke', 'Lynn', 'Madison', 'Malcolm', 'Manuel',
#     'Marcus', 'Margaret', 'Maria', 'Marie', 'Marilyn', 'Mark', 'Martha', 'Martin', 'Mary', 'Matthew',
#     'Megan', 'Melanie', 'Melissa', 'Michael', 'Michelle', 'Mike', 'Miranda', 'Mitchell', 'Molly', 'Monica',
#     'Nancy', 'Natalie', 'Nathan', 'Nicholas', 'Nicole', 'Nina', 'Noah', 'Nora', 'Norman', 'Oliver',
#     'Olivia', 'Oscar', 'Pamela', 'Patricia', 'Patrick', 'Paul', 'Paula', 'Peggy', 'Peter', 'Philip',
#     'Phillip', 'Rachel', 'Ralph', 'Randy', 'Raymond', 'Rebecca', 'Regina', 'Richard', 'Robert', 'Robin',
#     'Roger', 'Ronald', 'Rose', 'Roy', 'Ruby', 'Russell', 'Ruth', 'Ryan', 'Sabrina', 'Sally',
#     'Sam', 'Samantha', 'Samuel', 'Sandra', 'Sara', 'Sarah', 'Scott', 'Sean', 'Sharon', 'Shawn',
#     'Sheila', 'Shirley', 'Sidney', 'Simon', 'Sophia', 'Stephanie', 'Stephen', 'Steve', 'Steven', 'Stuart',
#     'Susan', 'Sydney', 'Sylvia', 'Tammy', 'Tanya', 'Taylor', 'Teresa', 'Terry', 'Theodore', 'Thomas',
#     'Timothy', 'Tina', 'Todd', 'Tom', 'Tony', 'Tracy', 'Travis', 'Trevor', 'Tyler', 'Valerie',
#     'Vanessa', 'Veronica', 'Victor', 'Victoria', 'Vincent', 'Virginia', 'Walter', 'Wanda', 'Warren', 'Wayne',
#     'Wendy', 'William', 'Willie', 'Zachary', 'Zoe','Adelaide', 'August', 'Aurora', 'Axel', 'Beatrice', 'Bennett', 
#     'Blair', 'Blaine', 'Byron', 'Carter', 
#     'Chase', 'Clayton', 'Cora', 'Damian', 'Daphne', 
#     'Dexter', 'Drake', 'Eden', 'Elena', 'Eliza', 
#     'Elliott', 'Emmett', 'Esther', 'Felix', 'Fletcher', 
#     'Gavin', 'Gemma', 'Grant', 'Griffin', 'Harper', 
#     'Hazel', 'Hugo', 'Iris', 'Ivy', 'Jasper', 
#     'June', 'Knox', 'Lance', 'Leo', 'Liam', 
#     'Luna', 'Maddox', 'Magnus', 'Mason', 'Maxwell', 
#     'Morgan', 'Nash', 'Owen', 'Paige', 'Parker', 
#     'Phoenix', 'Quinn', 'Reed', 'River', 'Sage', 
#     'Silas', 'Stella', 'Thea', 'Violet', 'Xavier'
# ]



