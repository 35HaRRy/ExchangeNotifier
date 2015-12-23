
from tools import *

class source(object):

    def getTable(self, tableName):
        options = { "ShortDateString": getShortDateString() }

        return self.getSourceTable(tableName, options)
    def getSourceTable(self, tableName, options):
        tableConfig = SourceConfig["tables"][tableName]

        tableConfig["path"] = tableConfig["path"].replace("%ProjectTablesPath%", ProjectTablesPath)
        tableConfig["name"] = tableConfig["name"].replace("%SortDateTimeString%", options["ShortDateString"])
        tableConfig["tableFileFullPath"] = tableConfig["path"] + tableConfig["name"]

        table = { "isTableFull": False, "error": False, "config": tableConfig }
        try:
            content = "[]"

            if os.path.isfile(tableConfig["tableFileFullPath"]):
                content = open(tableConfig["tableFileFullPath"]).read()
                if not content:
                    content = "[]"
            else:
                open(tableConfig["tableFileFullPath"], 'a')

            table["rows"] = json.loads(content)
            table["isTableFull"] = len(table["rows"]) > 0
        except StandardError as s:
            table["error"] = "True"
            table["errorMessage"] = s
            # log koy

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
        file = open(table["config"]["tableFileFullPath"], 'w')
        file.write(str(table["rows"]).replace("'", "\"").replace("u\"", "\""))

        return

    def getNewCode(self, table):
        format = table["config"]["codeFormat"]

        if format["type"] == "code":
            return  getCodeFromDate(datetime.now(), format)
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