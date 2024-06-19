import os
import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, exc
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
import pandas as pd

# URL бази даних, якщо не передано інше значення, використовується за замовчуванням
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///Showroom.db")

# Налаштування SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Створення сесії
Session = sessionmaker(bind=engine)
session = Session()

# Додаток Streamlit
st.title("Управління Базою Даних Авто")

menu = ["Створити Таблицю", "Переглянути Таблиці", "Додати Дані", "Редагувати Дані", "Видалити Дані", "Видалити Таблицю", "Додати Стовпець"]
choice = st.sidebar.selectbox("Меню", menu)

def create_table(table_name, columns):
    columns_list = [Column('id', Integer, primary_key=True, autoincrement=True)]
    for col in columns.split('\n'):
        col_name, col_type = col.split()
        if col_type.lower() == 'string':
            col_type = String(250)
        elif col_type.lower() == 'integer':
            col_type = Integer
        elif col_type.lower() == 'datetime':
            col_type = DateTime
        else:
            st.error(f"Непідтримуваний тип даних: {col_type}")
            continue
        columns_list.append(Column(col_name, col_type))
    new_table = Table(table_name, metadata, *columns_list)
    try:
        metadata.create_all(engine)
        st.success(f"Таблиця '{table_name}' створена успішно!")
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при створенні таблиці: {e}")

def view_tables():
    try:
        metadata.reflect(bind=engine)
        table_names = metadata.tables.keys()
        selected_table = st.selectbox("Оберіть Таблицю", list(table_names))
        if selected_table:
            table = Table(selected_table, metadata, autoload_with=engine)
            query = table.select()
            result = session.execute(query).fetchall()
            df = pd.DataFrame(result, columns=table.columns.keys())
            st.dataframe(df)
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при отриманні таблиць: {e}")

def add_data_to_table(table_name, data):
    try:
        metadata.reflect(bind=engine)
        if table_name in metadata.tables:
            table = metadata.tables[table_name]
            columns = [col.name for col in table.columns if col.name != 'id']
            if set(data.keys()) == set(columns):
                query = table.insert().values(**data)
                session.execute(query)
                session.commit()
                st.success("Дані додано успішно")
            else:
                st.error("Перевірте введені дані. Деякі поля можуть бути пропущені або введені невірно.")
        else:
            st.error(f"Таблиці '{table_name}' не існує")
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при додаванні даних: {e}")

def edit_data_in_table():
    try:
        metadata.reflect(bind=engine)
        table_names = metadata.tables.keys()
        selected_table = st.selectbox("Оберіть Таблицю", list(table_names))
        if selected_table:
            table = Table(selected_table, metadata, autoload_with=engine)
            columns = [col.name for col in table.columns if col.name != 'id']
            selected_id = st.number_input("ID Рядка для Оновлення", step=1)
            if selected_id:
                query = table.select().where(table.c.id == selected_id)
                result = session.execute(query).fetchone()
                if result:
                    result_dict = {col: result[idx] for idx, col in enumerate(table.columns.keys())}
                    data = {}
                    for col in columns:
                        data[col] = st.text_input(col, value=result_dict[col])
                    if st.button("Оновити Дані"):
                        query = table.update().where(table.c.id == selected_id).values(**data)
                        session.execute(query)
                        session.commit()
                        st.success("Дані оновлено успішно")
                else:
                    st.error("Рядок з таким ID не знайдено")
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при оновленні даних: {e}")

def delete_data_from_table():
    try:
        metadata.reflect(bind=engine)
        table_names = metadata.tables.keys()
        selected_table = st.selectbox("Оберіть Таблицю", list(table_names))
        if selected_table:
            table = Table(selected_table, metadata, autoload_with=engine)
            selected_id = st.number_input("ID Рядка для Видалення", step=1)
            if selected_id:
                query = table.select().where(table.c.id == selected_id)
                result = session.execute(query).fetchone()
                if result:
                    if st.button("Видалити Дані"):
                        delete_query = table.delete().where(table.c.id == selected_id)
                        session.execute(delete_query)
                        session.commit()
                        st.success("Дані видалено успішно")
                else:
                    st.error("Рядок з таким ID не знайдено")
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при видаленні даних: {e}")

def delete_table():
    try:
        metadata.reflect(bind=engine)
        table_names = metadata.tables.keys()
        selected_table = st.selectbox("Оберіть Таблицю для Видалення", list(table_names))
        if selected_table:
            if st.button("Видалити Таблицю"):
                table = Table(selected_table, metadata, autoload_with=engine)
                table.drop(engine)
                st.success(f"Таблиця '{selected_table}' успішно видалена")
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при видаленні таблиці: {e}")

def add_column_to_table():
    try:
        metadata.reflect(bind=engine)
        table_names = metadata.tables.keys()
        selected_table = st.selectbox("Оберіть Таблицю", list(table_names))
        if selected_table:
            table = Table(selected_table, metadata, autoload_with=engine)
            new_column_name = st.text_input("Назва Нового Стовпця")
            new_column_type = st.selectbox("Тип Нового Стовпця", ["string", "integer", "datetime"])
            if st.button("Додати Стовпець"):
                if new_column_name and new_column_type:
                    if new_column_type == "string":
                        new_column = Column(new_column_name, String(250))
                    elif new_column_type == "integer":
                        new_column = Column(new_column_name, Integer)
                    elif new_column_type == "datetime":
                        new_column = Column(new_column_name, DateTime)
                    else:
                        st.error("Непідтримуваний тип стовпця")
                        return
                    try:
                        alter_query = text(f"ALTER TABLE {selected_table} ADD COLUMN {new_column.compile(dialect=engine.dialect)}")
                        with engine.connect() as conn:
                            conn.execute(alter_query)
                        st.success(f"Стовпець '{new_column_name}' додано до таблиці '{selected_table}'")
                    except exc.SQLAlchemyError as e:
                        st.error(f"Помилка при додаванні стовпця: {e}")
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при додаванні стовпця: {e}")

if choice == "Створити Таблицю":
    st.subheader("Створити Нову Таблицю")
    table_name = st.text_input("Назва Таблиці")
    columns = st.text_area("Стовпці (формат: ім'я тип, один на рядок)")

    if st.button("Створити Таблицю"):
        if table_name and columns:
            create_table(table_name, columns)
        else:
            st.error("Будь ласка, введіть назву таблиці та стовпці")

elif choice == "Переглянути Таблиці":
    st.subheader("Переглянути Таблиці")
    view_tables()

elif choice == "Додати Дані":
    st.subheader("Додати Дані до Таблиці")
    try:
        metadata.reflect(bind=engine)
        table_names = metadata.tables.keys()
        selected_table = st.selectbox("Оберіть Таблицю", list(table_names))
        if selected_table:
            table = Table(selected_table, metadata, autoload_with=engine)
            columns = [col.name for col in table.columns if col.name != 'id']
            data = {}
            for col in columns:
                data[col] = st.text_input(col)
            if st.button("Додати Дані"):
                add_data_to_table(selected_table, data)
    except exc.SQLAlchemyError as e:
        st.error(f"Помилка при додаванні даних: {e}")

elif choice == "Редагувати Дані":
    st.subheader("Редагувати Дані в Таблиці")
    edit_data_in_table()

elif choice == "Видалити Дані":
    st.subheader("Видалити Дані з Таблиці")
    delete_data_from_table()

elif choice == "Видалити Таблицю":
    st.subheader("Видалити Таблицю")
    delete_table()

elif choice == "Додати Стовпець":
    st.subheader("Додати Стовпець до Таблиці")
    add_column_to_table()
