class subscribe:
    def __init__(self,a,b):
        self.resourceName = a
        self.url = b
    def setSubBody(self):
        return "{\"m2m:sub\":{\"rn\":\""+self.resourceName+"\",\"nu\":\""+self.url+"\",\"nct\":2}}"
