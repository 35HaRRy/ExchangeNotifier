from tools import *

class source(object):
    # region Definitions
    ProjectSourcePath = os.path.dirname(__file__) + "\\"
    ProjectTablesPath = ProjectSourcePath + "\\tables\\"

    config = json.loads(open(ProjectSourcePath + "sourceConfig.json").read())["sourceConfig"]
    # endregion

    def getTable(self, tableName):
        tableConfig = self.config["tables"][tableName]

        tableConfig["path"] = tableConfig["path"].replace("%ProjectTablesPath%", self.ProjectTablesPath)
        tableConfig["name"] = tableConfig["name"].replace("%SortDateTimeString%", getSortDateString())
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
            isThisRow = True

            for i in len(columnNames):
                if clauses[i] == "equal":
                    if row[columnNames[i]] != values[i]:
                        isThisRow = False
                        break
                elif clauses[i] == "smaller":
                    if row[columnNames[i]] <= values[i]:
                        isThisRow = False
                        break
                elif clauses[i] == "bigger":
                    if row[columnNames[i]] >= values[i]:
                        isThisRow = False
                        break
                else:
                   raise ValueError("clause cümlesi hatalı")

            if isThisRow:
                returnRows.append(row)

        return  returnRows