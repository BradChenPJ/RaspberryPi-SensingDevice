class container:
    def __init__(self,a):
        self.resourceName = a
    def setConBody(self):
        return "{\"m2m:cnt\":{\"rn\":\""+self.resourceName+"\"}}"
