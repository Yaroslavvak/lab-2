class Display:
    def PrintMessage(self, msg):
        print(msg)

    def PrintTable(db_handler, table_data):
        headers = table_data['headers']
        data = table_data['data']
        row_format = "{:<30}" * len(headers)
        print(row_format.format(*headers))
        print("-" * (30 * len(headers)))
        for row in data:
            print(row_format.format(*map(str, row)))

    def ShowMainMenu(self):
        print("\nMenu options:")
        print("1. View table\n2. Insert record\n3. Modify record\n4. Remove record\n5. Exit")
        choice = input("Select an option: ")
        return choice

    def PromtTableName(self):
        tableName = input("Enter the table name: ")
        return tableName

    def PromtID(self):
        id = input("Enter the ID: ")
        return id

    def PromtValues(self):
        enteries = input("Enter values (comma-separated): ")
        return enteries