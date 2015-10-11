import os
import simplejson

from datetime import *

class source(object):
    """description of class"""

    #init items
    ProjectSourcePath = os.path.dirname(__file__) + "\\"
    ProjectTablesPath = ProjectSourcePath + "\\tables\\"

    config = simplejson.loads(open(ProjectSourcePath + "sourceConfig.json").read())["sourceConfig"]

    def getTable(self, tableName):
        table = self.config["tables"][tableName]

        tableFilePath = table["path"].replace("%ProjectTablesPath%", self.ProjectTablesPath)
        fileName = table["name"].replace("%SortDateTimeString%", self.getSortDateString())
        tableFileFullPath = tableFilePath + fileName

        '''result = simplejson.loads("{}")
        try:
            file = open(tableFileFullPath, 'a+r')

            result = simplejson.loads(file.read())
        except:
            result = simplejson.loads("{\"error\":\"adasd\"}")
            #log koy'''

        file = open(tableFileFullPath, 'a')
        
        file.write("{\"error\":\"dosyaya yazdı\"}")
        file = open(tableFileFullPath)
        result = simplejson.loads(file.read())

        result["name"] = fileName
        return result

    def test(self):
        return simplejson.loads(open(self.ProjectSourcePath + "sourceConfig.json").read())["sourceConfig"]

    def getSortDateString(self):
        now = datetime.now()

        return "{0}-{1}-{2}".format(now.day, now.month, now.year)