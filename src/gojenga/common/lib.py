import curses.ascii


class lib:
    @staticmethod
    def detect_special_characters(block: str) -> bool:
        if any(not c.isalnum() for c in block):
            return True
        else:
            return False
