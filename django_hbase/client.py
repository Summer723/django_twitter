from django.conf import settings
import happybase


class HBaseClient:
    conn = None

    @classmethod
    def get_connection(cls):
        if cls.conn:
            return cls.conn
        cls.conn = happybase.Connection(
            host=settings.HBASE_HOST, port=9090,
            table_prefix=None,
            compat='0.92',
            table_prefix_separator=b'_',
            timeout=None,
            autoconnect=True,
            transport='framed',  # Default: 'buffered'  <---- Changed.
            protocol='compact'   # Default: 'binary'    <---- Changed.
    )
        return cls.conn