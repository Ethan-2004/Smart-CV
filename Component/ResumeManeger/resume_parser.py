import re
from docx import Document
from PyPDF2 import PdfReader

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_fields_from_text(text):
    name = re.search(r"姓名[:\s]*([\u4e00-\u9fa5]{2,5})", text)
    phone = re.search(r"\d{11}", text)
    school = re.search(r"[\u4e00-\u9fa5]+大学", text)
    edu = re.search(r"(本科|大专|硕士|博士)", text)
    salary = re.search(r"期望薪资[:：\s]*(\d+[kK]?)", text)
    age = re.search(r"\d{2}岁", text)
    region = re.search(r"现居[:：\s]*([\u4e00-\u9fa5]+)", text)
    gender = re.search(r"性别[:：\s]*(男|女)", text)
    return {
        "name": name.group(1) if name else None,
        "phone": phone.group(0) if phone else None,
        "school": school.group(0) if school else None,
        "education": edu.group(1) if edu else None,
        "expected_salary": salary.group(1) if salary else None,
        "age": age.group(0).replace("岁", "") if age else None,
        "region": region.group(1) if region else None,
        "gender": gender.group(1) if gender else None
    }
