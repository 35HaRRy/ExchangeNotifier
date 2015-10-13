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
        table = self.config["tables"][tableName]

        tableFilePath = table["path"].replace("%ProjectTablesPath%", self.ProjectTablesPath)
        fileName = table["name"].replace("%SortDateTimeString%", getSortDateString())
        tableFileFullPath = tableFilePath + fileName

        jsTable = json.loads("{\"isTableFull\": \"False\", \"error\": \"False\"}");

        try:
            jsTable["rows"] = json.loads(open(tableFileFullPath, 'a').read())
            jsTable["isTableFull"] = len(jsTable["rows"]) > 0
        except StandardError:
            jsTable["error"] = "True"
            # log koy

        jsTable["name"] = fileName
        return jsTable
