from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData(schema="marketing")
MarketingBase = declarative_base(metadata=metadata)
