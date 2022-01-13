class ScreenSize:
    SHORT = (720, 480)
    SQUARE = (720, 720)
    TALL = (720, 960)

    @staticmethod
    def from_type(value):
        """
        Get screem size by using value

        :param int value: screen size identity
        :return: screen size
        :rtype: (int, int)
        """
        if value == 1:
            return ScreenSize.SHORT
        elif value == 2:
            return ScreenSize.SQUARE
        elif value == 3:
            return ScreenSize.TALL
        else:
            return None
