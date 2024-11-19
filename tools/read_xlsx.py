import pandas as pd

# 讀取 Excel 檔案中的所有工作表
file_path = "三工三.xlsx"
excel_file = pd.ExcelFile(file_path)

# 開啟文字檔進行寫入
with open("output.txt", "w", encoding="utf-8") as f:
    # 迭代每個工作表
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        f.write(f"### 工作表名稱: {sheet_name} ###\n")
        
        # 寫入每列數據
        for index, row in df.iterrows():
            f.write(" ".join(map(str, row.values)) + "\n")
        f.write("\n")  # 添加空行分隔工作表

print("所有工作表的資料匯出完成！")
