import os
import simplejson as json

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