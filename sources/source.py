from tools import *

class source(object):
    # region Definitions
    ProjectSourcePath = os.path.dirname(__file__) + "\\"
    ProjectTablesPath = ProjectSourcePath + "\\tables\\"

    config = json.loads(open(ProjectSourcePath + "sourceConfig.json").read())["sourceConfig"]
    # endregion

    def getTable(self, tableName):
        options = { "ShortDateString": getShortDateString() }

        return self.getSourceTable(tableName, options)
    def getSourceTable(self, tableName, options):
        tableConfig = self.config["tables"][tableName]

        tableConfig["path"] = tableConfig["path"].replace("%ProjectTablesPath%", self.ProjectTablesPath)
        tableConfig["name"] = tableConfig["name"].replace("%SortDateTimeString%", options["ShortDateString"])
        tableConfig["tableFileFullPath"] = tableConfig["path"] + tableConfig["name"]
        tableConfig["newCode"] = getCode(tableConfig["codeFormat"])

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

    def saveTable(self, table):
        file = open(table["config"]["tableFileFullPath"], 'w')
        file.write(str(table["rows"]).replace("'", "\"").replace("u\"", "\""))

        return

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