﻿
from tools import *

class source(object):

    def __init__(self, auths):
        self.auths = auths

    def getTable(self, tableName):
        return self.getSourceTable(tableName, { "ShortDateString": getShortDateString() })

    def getSourceTable(self, tableName, options):
        tableConfig = SourceConfig["tables"][tableName]

        tableConfig["path"] = tableConfig["path"].replace("%ProjectTablesPath%", ProjectTablesPath)
        tableConfig["name"] = tableConfig["name"].replace("%SortDateTimeString%", options["ShortDateString"])
        tableConfig["tableFileFullPath"] = tableConfig["path"] + tableConfig["name"]

        table = { "isTableFull": False, "error": False, "config": tableConfig, "rows": [] }
        try:
            table["rows"] = json.loads(getFileContent(self.auths, tableConfig["tableFileFullPath"]))
            table["isTableFull"] = len(table["rows"]) > 0
        except StandardError as s:
            table["error"] = "True"
            table["errorMessage"] = s

            # self.insertTable("logs", { "date": str(datetime.now(tz)), "description": "error at getSourceTable", "error": str(s) })

        return table

    def insertTable(self, tableName, insertValue):
        table = self.getTable(tableName)
        format = table["config"]["codeFormat"]

        if format["type"] == "code":
            insertValue["code"] = self.getNewCode(table)
        elif format["type"] == "id":
            insertValue["id"] = self.getNewCode(table)

        table["rows"].append(insertValue)
        self.saveTable(table)

        return table

    def updateTable(self, table, updateValue):
        codeType = table["config"]["codeFormat"]["type"]

        for i in range(len(table["rows"])):
            if table["rows"][i][codeType] == updateValue[codeType]:
                table["rows"][i] = updateValue
                break

        self.saveTable(table)

        return

    def saveTable(self, table):
        if WebConfig["UseProjectEngine"]:
            insertStorageTable(self.auths, table)
        else:
            file = open(table["config"]["tableFileFullPath"], 'w')
            file.write(str(table["rows"]).replace("'", "\"").replace("u\"", "\""))

    def getNewCode(self, table):
        format = table["config"]["codeFormat"]

        if format["type"] == "code":
            return  getCodeFromDate(datetime.now(tz), format)
        elif format["type"] == "id":
            return getMaxId(table["rows"]) + 1

    def getRows(self, rows, columnNames, values):
        clauses = []
        for i in range(len(columnNames)):
            clauses.append("equal")

        return self.getRowsByClause(rows, columnNames, values, clauses)
    def getRowsByClause(self, rows, columnNames, values, clauses):
        returnRows = []

        if len(columnNames) != len(values) and len(columnNames) != len(clauses):
            raise ValueError("columnNames in uzunlugu ile values un ve clauses un uzunlugu ayni olmali")

        for row in rows:
            control = True

            for i in range(len(columnNames)):
                if not isThisRow(clauses[i], row[columnNames[i]], values[i]):
                    control = False
                    break

            if control:
                returnRows.append(row)

        return  returnRows