from view import Display
from model import Database

class Manager:
    def __init__(self):
        self.dbView = Display()
        self.dbModel = Database()

    def Run(self):
        while True:
            choice = self.dbView.ShowMainMenu()
            if choice == '1':
                self.ShowTableData()
            elif choice == '2':
                self.InsertNewRecord()
            elif choice == '3':
                self.ModifyRecord()
            elif choice == '4':
                self.RemoveRecord()
            elif choice == '5':
                return
            else:
                self.dbView.PrintMessage("Invalid option. Please try again.\n")

    def ShowTableData(self):
        tableName = self.dbView.PromtTableName()
        try:
            tableData = self.dbModel.GetTable(tableName)
            self.dbView.PrintTable(tableData)
        except ValueError as e:
            self.dbView.PrintMessage(str(e))

    def InsertNewRecord(self):
        tableName = self.dbView.PromtTableName()
        inputValues = self.dbView.PromtValues()
        try:
            self.dbModel.AddRecord(tableName, inputValues)
        except ValueError as e:
            self.dbView.PrintMessage(str(e))

    def ModifyRecord(self):
        tableName = self.dbView.PromtTableName()
        recordID = self.dbView.PromtID()
        inputValues = self.dbView.PromtValues()
        try:
            self.dbModel.UpdateRecord(tableName, inputValues, recordID)
        except ValueError as e:
            self.dbView.PrintMessage(str(e))

    def RemoveRecord(self):
        tableName = self.dbView.PromtTableName()
        recordID = self.dbView.PromtID()
        try:
            self.dbModel.DeleteRecord(tableName, recordID)
        except ValueError as e:
            self.dbView.PrintMessage(str(e))