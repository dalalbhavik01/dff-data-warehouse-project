import os

script_dir = "/Users/bhavikdalal/Documents/data warehouse/project/report_3"
md_path = os.path.join(script_dir, "Integrated_Report_3.md")
sql_dir = os.path.join(script_dir, "sql")

sql_files = sorted([f for f in os.listdir(sql_dir) if f.endswith('.sql')])

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Appendix A section
app_a_header = "### Appendix A: Complete SQL Scripts"
app_b_header = "### Appendix B: Mapping Tables (Excel)"

# Extract before and after Appendix A
before_app_a = content[:content.find(app_a_header) + len(app_a_header)]
after_app_b = content[content.find(app_b_header):]

new_app_a = "\n\nThe complete SQL logic for the implementation is provided below.\n\n"

for sql_file in sql_files:
    file_path = os.path.join(sql_dir, sql_file)
    with open(file_path, 'r', encoding='utf-8') as sf:
        sql_content = sf.read()
    new_app_a += f"#### {sql_file}\n"
    new_app_a += "```sql\n"
    new_app_a += sql_content.strip() + "\n"
    new_app_a += "```\n\n"

new_content = before_app_a + new_app_a + after_app_b

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
