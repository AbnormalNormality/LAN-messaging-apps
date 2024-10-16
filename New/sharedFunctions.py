class Validate:
    @staticmethod
    def port(chars):
        return not ((not chars.isdigit() and chars != "") or len(chars) > 5)

    @staticmethod
    def ip(chars):
        return not len(chars) > 15

    @staticmethod
    def username(chars):
        return not (len(chars) > 8 or (not chars.isalnum() and chars != "_") and chars != "")
