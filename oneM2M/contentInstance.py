import json
class contentInstance:
    def __init__(self,b,c):
        self.resourceName = b
        self.con = c
    def setCinBody(self):
        body = {}
        mainObj = {}
        body["cnf"] = self.resourceName
        body["rn"] = self.resourceName
        body["con"] = self.con
        mainObj["m2m:cin"] = body
        return json.dumps(mainObj)
