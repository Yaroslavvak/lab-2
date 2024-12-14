from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    books = relationship("Book", back_populates="owner")
    requests = relationship("Request", back_populates="user")
class Book(Base):
    __tablename__ = 'Book'
    book_id = Column(Integer, primary_key=True)
    title = Column(String(30), nullable=False)
    author = Column(String(20), nullable=False)
    genre = Column(String(40), nullable=False)
    condition = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    owner = relationship("User", back_populates="books")
    listings = relationship("Listing", back_populates="book")
class Listing(Base):
    __tablename__ = 'Listing'
    listing_id = Column(Integer, primary_key=True)
    created_date = Column(Date, nullable=False)
    book_id = Column(Integer, ForeignKey('Book.book_id'), nullable=False)
    status = Column(String(30), nullable=False)
    book = relationship("Book", back_populates="listings")
    requests = relationship("Request", back_populates="listing")
class Request(Base):
    __tablename__ = 'Request'
    request_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    listing_id = Column(Integer, ForeignKey('Listing.listing_id'), nullable=False)
    user = relationship("User", back_populates="requests")
    listing = relationship("Listing", back_populates="requests")

class Database:
    def __init__(self):
        self.engine = create_engine('postgresql+psycopg2://postgres:1234@localhost/vakulchuk')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def GetTable(self, table_name):
        with self.Session() as session:
            entity_map = {cls.__tablename__: cls for cls in Base.__subclasses__()}
            if table_name not in entity_map:
                raise ValueError(f"'{table_name}' is not a valid table.")
            entity = entity_map[table_name]
            results = session.query(entity).all()
            if not results:
                raise ValueError(f"No entries found in '{table_name}'.")
            headers = [col.name for col in entity.__table__.columns]
            data = [[getattr(record, col) for col in headers] for record in results]
            return {"headers": headers, "data": data}

    def ValidateInput(self, model, data):
        table_columns = model.__table__.columns
        for column in table_columns:
            col_name = column.name
            col_type = column.type.python_type
            if col_name not in data:
                continue
            if col_type == int:
                data[col_name] = int(data[col_name])
            elif col_type == str:
                data[col_name] = str(data[col_name])
            elif col_type == datetime.date:
                try:
                    data[col_name] = datetime.strptime(data[col_name], "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Invalid date format for column '{col_name}', expected 'YYYY-MM-DD'.")
        inspector = inspect(self.engine)
        foreign_keys = inspector.get_foreign_keys(model.__tablename__)
        for fk in foreign_keys:
            parent_table_name = fk['referred_table']
            parent_column_name = fk['referred_columns'][0]
            child_column_name = fk['constrained_columns'][0]
            parent_model = {cls.__tablename__: cls for cls in Base.__subclasses__()}.get(parent_table_name)
            if not parent_model:
                raise ValueError(f"Foreign key refers to non-existent table '{parent_table_name}'.")
            with self.Session() as session:
                if not session.query(parent_model).filter(
                        getattr(parent_model, parent_column_name) == data[child_column_name]).first():
                    raise ValueError(
                        f"No matching record in '{parent_table_name}' for value '{data[child_column_name]}'.")

    def AddRecord(self, table_name, values_str):
        with self.Session() as session:
            table_map = {cls.__tablename__: cls for cls in Base.__subclasses__()}
            if table_name not in table_map:
                raise ValueError(f"Table '{table_name}' does not exist.")
            model = table_map[table_name]
            values_list = [val.strip() for val in values_str.split(",")]
            table_columns = [column.name for column in model.__table__.columns]
            if len(values_list) != len(table_columns):
                raise ValueError(
                    f"The number of provided values ({len(values_list)}) does not match "
                    f"the number of columns in table '{table_name}' ({len(table_columns)})."
                )
            data = dict(zip(table_columns, values_list))
            self.ValidateInput(model, data)
            primary_keys = {col.name: data[col.name] for col in model.__table__.primary_key.columns}
            if session.query(model).filter_by(**primary_keys).first():
                raise ValueError(f"Record with primary keys {primary_keys} already exists.")
            new_record = model(**data)
            session.add(new_record)
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                raise ValueError(f"Failed to insert record: {e}")

    def UpdateRecord(self, table_name, values_str, record_id):
        with self.Session() as session:
            table_map = {cls.__tablename__: cls for cls in Base.__subclasses__()}
            if table_name not in table_map:
                raise ValueError(f"Table '{table_name}' does not exist.")
            model = table_map[table_name]
            primary_key = list(model.__table__.primary_key.columns)[0].name
            record = session.query(model).filter(getattr(model, primary_key) == record_id).first()
            if not record:
                raise ValueError(f"No record with ID {record_id} found in table '{table_name}'.")
            values_list = [val.strip() for val in values_str.split(",")]
            table_columns = [column.name for column in model.__table__.columns]
            if len(values_list) != len(table_columns):
                raise ValueError(
                    f"The number of provided values ({len(values_list)}) does not match "
                    f"the number of columns in table '{table_name}' ({len(table_columns)})."
                )
            data = dict(zip(table_columns, values_list))
            self.ValidateInput(model, data)
            for key, value in data.items():
                setattr(record, key, value)
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                raise ValueError(f"Failed to update record: {e}")

    def DeleteRecord(self, table_name, record_id):
        with self.Session() as session:
            table_map = {cls.__tablename__: cls for cls in Base.__subclasses__()}
            if table_name not in table_map:
                raise ValueError(f"Table '{table_name}' does not exist.")
            model = table_map[table_name]
            primary_key = list(model.__table__.primary_key.columns)[0].name
            record = session.query(model).filter(getattr(model, primary_key) == record_id).first()
            if not record:
                raise ValueError(f"No record with ID {record_id} found in table '{table_name}'.")
            inspector = inspect(self.engine)
            foreign_keys = inspector.get_foreign_keys(model.__tablename__)
            for fk in foreign_keys:
                child_table_name = fk['referred_table']
                child_column_name = fk['referred_columns'][0]
                child_model = table_map.get(child_table_name)
                if child_model:
                    child_column = getattr(child_model, child_column_name, None)
                    if not child_column:
                        raise ValueError(
                            f"Foreign key column '{child_column_name}' does not exist in table '{child_table_name}'."
                        )
                    dependent_record = session.query(child_model).filter(child_column == record_id).first()
                    if dependent_record:
                        raise ValueError(
                            f"Cannot delete record; dependent records exist in table '{child_table_name}'."
                        )
            try:
                session.delete(record)
                session.commit()
            except Exception as e:
                session.rollback()
                raise ValueError(f"Failed to delete record: {e}")