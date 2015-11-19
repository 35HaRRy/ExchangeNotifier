from tools import *

class source(object):
    # region Definitions
    ProjectSourcePath = os.path.dirname(__file__) + "\\"
    ProjectTablesPath = ProjectSourcePath + "\\tables\\"

    config = json.loads(open(ProjectSourcePath + "sourceConfig.json").read())["sourceConfig"]
    # endregion

    def getTable(self, tableName):
        options = { "ShortDateString", getSortDateString() }

        return self.getTable(tableName, options)

    def getTable(self, tableName, options):
        tableConfig = self.config["tables"][tableName]

        tableConfig["path"] = tableConfig["path"].replace("%ProjectTablesPath%", self.ProjectTablesPath)
        tableConfig["name"] = tableConfig["name"].replace("%SortDateTimeString%", options["SortDateString"])
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
        except StandardError:
            table["error"] = "True"
            # log koy

        return table

    def saveTable(self, table):
        file = open(table["config"]["tableFileFullPath"], 'w')
        file.write(str(table["rows"]).replace("'", "\"").replace("u\"", "\""))

        return

    def getRows(self, rows, columnNames, values):
        clauses = []
        for i in len(columnNames):
            clauses.append("equal")

        return self.getRows(rows, columnNames, values, clauses)

    def getRows(self, rows, columnNames, values, clauses):
        returnRows = []

        if len(columnNames) != len(values) and len(columnNames) != len(clauses):
            raise ValueError("columnNames in uzunluğu ile values un ve clauses un uzunluğu aynı olmalı")

        for row in rows:
            control = True

            for i in len(columnNames):
                if not isThisRow(clauses[i], row[columnNames[i]], values[i]):
                    control = False
                    break

            if control:
                returnRows.append(row)

        return  returnRows