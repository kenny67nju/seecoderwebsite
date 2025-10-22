import pandas as pd

def read_excel_data(file_path):
    """
    读取Excel文件中的成员信息
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None

def categorize_members(df):
    """
    将成员按类型分类
    """
    # 根据已有的网页信息，手动添加教师信息
    teachers = [
        {"姓名": "刘钦", "角色": "副教授", "研究方向": "软件工程、数据增强"},
        {"姓名": "冯桂焕", "角色": "副教授", "研究方向": "人机交互"},
        {"姓名": "刘峰", "角色": "高级工程师", "研究方向": "数据挖掘"},
        {"姓名": "赵凤山", "角色": "助理研究员", "研究方向": "待更新"}
    ]
    
    # 分离学生
    phd_students = []
    master_students = []
    undergraduate_students = []
    
    for _, row in df.iterrows():
        name = row['姓名']
        grade = row['年级']
        group = row['分组']
        
        # 根据年级判断学位类型
        if '博' in str(grade):
            phd_students.append({
                "姓名": name,
                "角色": "博士生",
                "研究方向": group if pd.notna(group) else "待更新",
                "年级": grade
            })
        elif '研' in str(grade):
            master_students.append({
                "姓名": name,
                "角色": "硕士生",
                "研究方向": group if pd.notna(group) else "待更新",
                "年级": grade
            })
        elif '大' in str(grade):
            undergraduate_students.append({
                "姓名": name,
                "角色": "本科生",
                "研究方向": group if pd.notna(group) else "待更新",
                "年级": grade
            })
    
    return teachers, phd_students, master_students, undergraduate_students

def generate_member_html(member, member_type="current"):
    """
    生成单个成员的HTML代码
    """
    html = "                <div class=\"team-member\">\n"
    html += f"                    <img src=\"personal.png\" alt=\"{member['姓名']}\">\n"
    html += f"                    <h3>{member['姓名']}</h3>\n"
    html += f"                    <span class=\"member-role\">{member['年级'] if '年级' in member else ''} {member['角色']}</span>\n"
    html += f"                    <p>研究方向：{member['研究方向']}</p>\n"
    
    # 如果是毕业生，添加去向信息
    if member_type == "graduate" and "去向" in member:
        html += f"                    <p>去向：{member['去向']}</p>\n"
    
    html += "                </div>\n"
    return html

def generate_section_html(section_title, members, section_class=""):
    """
    生成整个部分的HTML代码
    """
    if not members:
        return ""
    
    html = f"        <section>\n"
    html += f"            <h2>{section_title}</h2>\n"
    
    if section_class:
        html += f"            <div class=\"{section_class}\">\n"
    else:
        html += "            <div class=\"team-members\">\n"
    
    # 按年级排序（博士生、研三、研二、研一、大四、大三）
    def sort_key(member):
        grade = member.get('年级', '')
        if '博' in grade:
            return 0
        elif '研三' in grade:
            return 1
        elif '研二' in grade:
            return 2
        elif '研一' in grade:
            return 3
        elif '大四' in grade:
            return 4
        elif '大三' in grade:
            return 5
        else:
            return 6
    
    sorted_members = sorted(members, key=sort_key)
    
    for member in sorted_members:
        html += generate_member_html(member)
    
    html += "            </div>\n"
    html += "        </section>\n\n"
    return html

def update_members_html(excel_file, html_file):
    """
    根据Excel数据更新成员HTML文件
    """
    # 读取Excel数据
    df = read_excel_data(excel_file)
    if df is None:
        return False
    
    # 分类成员
    teachers, phd_students, master_students, undergraduate_students = categorize_members(df)
    
    # 读取原始HTML文件
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"读取HTML文件时出错: {e}")
        return False
    
    # 生成新的成员部分HTML
    new_members_content = ""
    
    # 添加教师部分
    if teachers:
        new_members_content += generate_section_html("实验室老师", teachers)
    
    # 添加博士生部分
    if phd_students:
        new_members_content += generate_section_html("博士生", phd_students)
    
    # 添加硕士生部分
    if master_students:
        new_members_content += generate_section_html("硕士生", master_students)
    
    # 添加本科生部分
    if undergraduate_students:
        new_members_content += generate_section_html("本科生", undergraduate_students)
    
    # 保留原有的毕业生部分（因为Excel中没有这些信息）
    # 在实际应用中，如果Excel包含毕业生信息，可以在这里处理
    
    # 替换HTML中的成员部分
    try:
        # 找到第一个<section>标签之前的内容
        header_end = html_content.find("<section>")
        if header_end == -1:
            print("未找到<section>标签")
            return False
            
        header_content = html_content[:header_end]
        
        # 找到最后一个</section>标签之后的内容
        footer_start = html_content.rfind("</section>")
        if footer_start == -1:
            print("未找到</section>标签")
            return False
            
        footer_content = html_content[footer_start + len("</section>"):]
        
        # 组合新的HTML内容
        new_html_content = header_content + new_members_content + footer_content
        
        # 写入更新后的HTML文件
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_html_content)
            
        print("成功更新成员页面")
        return True
        
    except Exception as e:
        print(f"更新HTML文件时出错: {e}")
        return False

if __name__ == "__main__":
    excel_file = "SEECODER2025成员.xlsx"
    html_file = "members.html"
    
    success = update_members_html(excel_file, html_file)
    if success:
        print("成员页面已成功更新")
    else:
        print("更新成员页面时出错")