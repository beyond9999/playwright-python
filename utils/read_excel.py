import openpyxl


class ExcelDataReader:
    def __init__(self, file_path, sheet_name):
        self.file_path = file_path
        self.sheet_name = sheet_name

    def read_data(self):
        try:
            workbook = openpyxl.load_workbook(self.file_path)
            sheet = workbook[self.sheet_name]
            test_data = []

            first_row_skipped = False  # 用于跳过第一行的标志变量

            for row in sheet.iter_rows(values_only=True):
                if not first_row_skipped:
                    first_row_skipped = True
                    continue  # 跳过第一行

                # 将 None 值替换为 ''
                cleaned_row = tuple('' if cell is None else cell for cell in row)
                test_data.append(cleaned_row)

            workbook.close()
            return test_data
        except Exception as e:
            print(f"读取 Excel 数据时发生错误：{e}")
            return []
