import streamlit as st
import pyodbc
import pandas as pd

# Функція для підключення до бази даних
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=your_server;'
        'DATABASE=Library;'
        'UID=your_username;'
        'PWD=your_password'
    )
    return conn

# Функції для зчитування даних з таблиць
def fetch_authors():
    conn = get_db_connection()
    query = "SELECT * FROM Authors"
    authors = pd.read_sql(query, conn)
    conn.close()
    return authors

def fetch_publishing():
    conn = get_db_connection()
    query = "SELECT * FROM Publishing"
    publishing = pd.read_sql(query, conn)
    conn.close()
    return publishing

def fetch_books():
    conn = get_db_connection()
    query = "SELECT * FROM Books"
    books = pd.read_sql(query, conn)
    conn.close()
    return books

def fetch_genres():
    conn = get_db_connection()
    query = "SELECT * FROM Genres"
    genres = pd.read_sql(query, conn)
    conn.close()
    return genres

# Функції для додавання, редагування та видалення даних
def add_author(name, genre, country, language):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Authors (Name, Genre, Country, Language) VALUES (?, ?, ?, ?)",
                   (name, genre, country, language))
    conn.commit()
    conn.close()

def update_author(id_author, name, genre, country, language):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Authors SET Name = ?, Genre = ?, Country = ?, Language = ? WHERE ID_Author = ?",
                   (name, genre, country, language, id_author))
    conn.commit()
    conn.close()

def delete_author(id_author):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Authors WHERE ID_Author = ?", (id_author,))
    conn.commit()
    conn.close()

# Головна функція для відображення Streamlit додатку
def main():
    st.title("Library Database Viewer")

    st.sidebar.title("Select Table")
    option = st.sidebar.selectbox("Which table would you like to view?", ("Authors", "Publishing", "Books", "Genres"))

    if option == "Authors":
        st.header("Authors")
        authors = fetch_authors()
        st.dataframe(authors)

        st.subheader("Add a new author")
        with st.form("add_author_form"):
            name = st.text_input("Name")
            genre = st.text_input("Genre")
            country = st.text_input("Country")
            language = st.text_input("Language")
            submitted = st.form_submit_button("Add Author")
            if submitted:
                add_author(name, genre, country, language)
                st.success("Author added successfully")

        st.subheader("Update an author")
        with st.form("update_author_form"):
            id_author = st.number_input("Author ID", min_value=1, step=1)
            name = st.text_input("Name")
            genre = st.text_input("Genre")
            country = st.text_input("Country")
            language = st.text_input("Language")
            submitted = st.form_submit_button("Update Author")
            if submitted:
                update_author(id_author, name, genre, country, language)
                st.success("Author updated successfully")

        st.subheader("Delete an author")
        with st.form("delete_author_form"):
            id_author = st.number_input("Author ID", min_value=1, step=1)
            submitted = st.form_submit_button("Delete Author")
            if submitted:
                delete_author(id_author)
                st.success("Author deleted successfully")

    elif option == "Publishing":
        st.header("Publishing")
        publishing = fetch_publishing()
        st.dataframe(publishing)

    elif option == "Books":
        st.header("Books")
        books = fetch_books()
        st.dataframe(books)

    elif option == "Genres":
        st.header("Genres")
        genres = fetch_genres()
        st.dataframe(genres)

if __name__ == "__main__":
    main()
