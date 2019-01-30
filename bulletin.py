class Bulletin:
    def __str__(self) -> str:
        return 'Bulletin. Valid: {}. Issued: {}. Type: {}. Fronts: {}.'.format(
            self.valid,
            self.issued,
            self.type,
            self.fronts
        )

    def __init__(self, valid, issued, fronts, type):
        self.valid = valid
        self.issued = issued
        self.fronts = fronts
        self.type = type
