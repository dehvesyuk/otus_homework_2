
class Field:
    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable


class CharField(Field):
    pass


class DigitField(Field):
    pass


class DateField(Field):
    pass


class ArgumentsField(CharField):
    pass


class EmailField(CharField):
    pass


class PhoneField(DigitField):
    pass


class BirthDayField(DateField):
    pass


class GenderField(CharField):
    pass


class ClientIDsField(CharField):
    pass
