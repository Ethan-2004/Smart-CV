
def prompt_template_format_resume(resume_text):
  # print(resume_text)
  prompt1 = """
你是一位专业的简历分析师，请对以下简历文本进行结构化提取、智能分析和合理推理，完成以下任务：

---
📄 以下是简历原文内容：

{}
""".format(resume_text)

  prompt2 = """
🎯 **目标输出**：请将简历信息提取并按如下字段返回一个**标准 JSON 对象**（无需注释、不带多余文本），包括：


"{
  "name": "",                           // 姓名，如无法明确请留空
  "gender": "",                         // 性别（男/女），如无法明确请合理推断
  "age": 0,                             // 年龄，若未明确请根据毕业年份或学历合理推测
  "phone": "",                          // 手机号，仅数字
  "email": "",                          // 邮箱地址
  "education": "",                      // 最高学历：高中、大专、本科、硕士、博士
  "school": "",                         // 毕业院校
  "major": "",                          // 所学专业
  "skills": [],                         // 技能关键词列表，如：["Python", "C++", "数据分析"]
  "certifications": [],                // 所获证书，如：["英语四级", "计算机二级", "华为HCIA"]
  "experience": "",                     // 项目或实习/工作经验（文本摘要）
  "personal_qualities": [],            // 品质关键词，如 ["认真", "踏实", "沟通能力强"]
  "honors": [],                        // 获奖情况，如 ["三等奖学金", "挑战杯二等奖"]
  "languages": [],                     // 语言能力，如 ["英语四级", "日语N2"]
  "tools": [],                         // 熟练工具/平台，如 ["Linux", "Flask", "MySQL", "Vue"]
  "expected_salary": "",               // 期望薪资（如有），若无请返回 "面议"
  "region": "",                        // 求职区域，如简历中有提及（如：江苏、上海）
  "position_direction": ""             // 模型自动推断候选人适合的岗位方向，如：“后端开发工程师”、“数据分析师”、“测试工程师”等
}
"
🔍 注意事项：
如果简历中没有明确写出某项，请根据上下文推断，若无迹可循则设为默认值或空。
请根据技能、经历、工具等自动判断候选人适合的岗位方向 position_direction。
返回的 JSON 必须符合格式规范，可被 Python json.loads() 正确解析。

          """
  prompt=f"{prompt1}{prompt2}"
  return prompt


def prompt_template_format_jobrequire(job_requirements):
  prompt = f"""
你是一名招聘专家，请根据以下职位名称和职位描述，提取并生成该职位切实需要的技能（skills）、证书要求（certifications）以及期望的个人品质（personal_qualities）。 

请输出JSON格式，包含以下字段：
{{
  "required_skills": [...],             
  "required_certifications": [...],     
  "desired_personal_qualities": [...]   
}}

职位名称+职位描述：

{job_requirements}

请根据职位描述，详细罗列每个字段中的条目，确保切实反映岗位需求，不要遗漏关键内容。
只输出符合JSON格式的内容，不要额外说明。
"""
  return prompt

def prompt_template_format_resume_job_score(structured_resume, structured_job):
    prompt = f"""
你是一名人力资源与数据分析专家，任务是根据**应聘者简历信息**和**岗位要求**，从以下几个维度为该简历进行100分制评分：

评分维度包括：
1. education_score：教育程度匹配程度（满分100分）；
2. skills_score：岗位所需技能匹配程度（满分100分）；
3. experience_score：从工作经历匹配程度主观判断经验匹配程度（满分100分）。
4. certifications_score：岗位要求证书的匹配程度（满分100分）；
5. personal_qualities_score：岗位理想人格特质与简历人格特质的匹配程度（满分100分）；


请你通读简历与岗位信息后，进行合理分析并输出一个JSON字典结构：
{{
  "education_score": 85,
  "skills_score": 90,
  "experience_score": 95,
  "certifications_score": 70,
  "personal_qualities_score": 60
  
}}

注意：
- 不要输出除 JSON 以外的任何内容；
- 请严格基于简历与岗位需求进行客观评价，不要随意满分；
- 不要遗漏任一评分字段。

以下是结构化后的简历信息：
{structured_resume}

以下是结构化后的岗位要求：
{structured_job}
"""
    return prompt
