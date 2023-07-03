class HBaseField:
    field_type = None

    def __init__(self, *args, **kwargs):
        # reverse 主要是 为了让服务器均匀使用
        self.reverse = reverse
        self.column_family = column_family


class IntegerField(HBaseField):
    field_type = 'int'

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TimestampField(HBaseField):
    field_type = 'timestamp'

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


