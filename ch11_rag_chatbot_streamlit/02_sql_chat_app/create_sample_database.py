import sqlite3

# Path to your new SQLite database file
db_path = "bookstore.db"

# Multi-statement SQL for SQLite (adapted from MySQL)
sql_script = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS genres (
    GenreID INTEGER PRIMARY KEY AUTOINCREMENT,
    GenreName TEXT,
    Description TEXT
);

INSERT INTO genres (GenreID, GenreName, Description) VALUES
(1, 'Science Fiction', 'Futuristic and scientific themes'),
(2, 'Fantasy', 'Magical worlds and creatures'),
(3, 'Mystery', 'Detective and crime stories'),
(4, 'Non-Fiction', 'Based on real events and facts'),
(5, 'Romance', 'Love and relationships');

CREATE TABLE IF NOT EXISTS clients (
    ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientName TEXT,
    ContactEmail TEXT,
    Street TEXT,
    Town TEXT,
    ZipCode TEXT,
    Country TEXT
);

INSERT INTO clients (ClientID, ClientName, ContactEmail, Street, Town, ZipCode, Country) VALUES
(1, 'Page Turners', 'info@pageturners.com', '12 Elm St', 'Springfield', '12345', 'USA'),
(2, 'Readers Haven', 'contact@readershaven.org', '45 Oak Ave', 'Mapleton', '54321', 'USA'),
(3, 'Book Nook', 'hello@booknook.net', '78 Pine Rd', 'Lakeside', '67890', 'Canada');

CREATE TABLE IF NOT EXISTS staff (
    StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
    Surname TEXT,
    GivenName TEXT,
    HireDate TEXT,
    ProfilePic TEXT,
    Bio TEXT
);

INSERT INTO staff (StaffID, Surname, GivenName, HireDate, ProfilePic, Bio) VALUES
(1, 'Smith', 'Alice', '2010-05-12', 'staff1.jpg', 'Alice is an avid reader and manages the fiction section.'),
(2, 'Johnson', 'Bob', '2012-09-23', 'staff2.jpg', 'Bob specializes in non-fiction and biographies.');

CREATE TABLE IF NOT EXISTS deliveries (
    DeliveryID INTEGER PRIMARY KEY AUTOINCREMENT,
    DeliveryCompany TEXT,
    ContactNumber TEXT
);

INSERT INTO deliveries (DeliveryID, DeliveryCompany, ContactNumber) VALUES
(1, 'QuickShip', '(555) 123-4567'),
(2, 'BookCourier', '(555) 987-6543');

CREATE TABLE IF NOT EXISTS authors (
    AuthorID INTEGER PRIMARY KEY AUTOINCREMENT,
    AuthorName TEXT,
    Bio TEXT
);

INSERT INTO authors (AuthorID, AuthorName, Bio) VALUES
(1, 'Jane Starling', 'Jane writes science fiction novels.'),
(2, 'Mark Rivers', 'Mark is known for his fantasy adventures.');

CREATE TABLE IF NOT EXISTS books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT,
    AuthorID INTEGER,
    GenreID INTEGER,
    Format TEXT,
    Price REAL,
    FOREIGN KEY (GenreID) REFERENCES genres(GenreID),
    FOREIGN KEY (AuthorID) REFERENCES authors(AuthorID)
);

INSERT INTO books (BookID, Title, AuthorID, GenreID, Format, Price) VALUES
(5, 'The Lost Galaxy', 1, 1, 'Hardcover', 22.99),
(10, 'Mystic River', 2, 2, 'Paperback', 15.50);

CREATE TABLE IF NOT EXISTS sales (
    SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientID INTEGER,
    StaffID INTEGER,
    SaleDate TEXT,
    DeliveryID INTEGER,
    FOREIGN KEY (ClientID) REFERENCES clients(ClientID),
    FOREIGN KEY (StaffID) REFERENCES staff(StaffID),
    FOREIGN KEY (DeliveryID) REFERENCES deliveries(DeliveryID)
);

INSERT INTO sales (SaleID, ClientID, StaffID, SaleDate, DeliveryID) VALUES
(1001, 1, 2, '2023-01-15', 1),
(1002, 2, 1, '2023-02-20', 2);

CREATE TABLE IF NOT EXISTS sale_items (
    SaleItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    SaleID INTEGER,
    BookID INTEGER,
    Quantity INTEGER,
    FOREIGN KEY (SaleID) REFERENCES sales(SaleID),
    FOREIGN KEY (BookID) REFERENCES books(BookID)
);

INSERT INTO sale_items (SaleItemID, SaleID, BookID, Quantity) VALUES
(1, 1001, 10, 2),
(2, 1002, 5, 1);
"""


def main():
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql_script)
        print("Database created and populated successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
