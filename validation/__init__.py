from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    def error(self):
        """
        Get first form error

        :return: error message
        :rtype: str or None
        """
        if self.validate():
            return None

        for e in self.errors:
            for err in self.errors[e]:
                if len(err) == 0:
                    continue

                if type(err) == list:
                    return err[0]
                return err

        return None

    def error_group(self):
        """
        Get form errors

        :return: list of errors
        :rtype: list[str]
        """
        if self.validate():
            return []

        errors = []
        for es in self.errors:
            for e in self.errors[es]:
                if type(e) == list:
                    errors.append(e[0])
                else:
                    errors.append(e)

        return errors
