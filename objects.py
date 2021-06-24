class Schema(dict):

    def __init__(self, dictionary):
        super().__init__(**dictionary)

    def safe_pop(self, key, default=None):
        if key in self:
            return super().pop(key, default)
        else:
            return default
