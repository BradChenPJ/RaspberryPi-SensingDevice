class AE:
    def __init__(self, a, b):
        self.resourceName = a
        self.lbl = b
    def setAEBody(self):
        return "{\"m2m:ae\":{\"api\":\""+self.resourceName+"\",\"rr\":\"false\",\"lbl\":\""+self.lbl+"\",\"rn\":\""+self.resourceName+"\"}}"
