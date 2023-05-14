INSERT INTO administrator (login_id, passwd, first_name, last_name, sex, birth_date)
VALUES ('admin1', 'password1', 'John', 'Doe', 'Male', '1990-05-20'),
('admin2', 'password2', 'Jane', 'Doe', 'Female', '1995-01-12'),
('admin3', 'password3', 'Alice', 'Smith', 'Female', '1992-09-06'),
('admin4', 'password4', 'Bob', 'Johnson', 'Male', '1988-12-31'),
('admin5', 'password5', 'Chris', 'Lee', 'Other', '1998-07-15');

--
INSERT INTO school (school_name, city, phone_number, email, addrss, admin_id)
VALUES ('School A', 'New York', 1111111, 'schoola@example.com', '123 Main St', 1),
('School B', 'Los Angeles', 2222222, 'schoolb@example.com', '456 Oak Ave', 2),
('School C', 'Chicago', 333333333, 'schoolc@example.com', '789 Elm St', 3),
('School D', 'Houston', 44444444, 'schoold@example.com', '321 Maple St', 4),
('School E', 'Miami', 55555555, 'schoole@example.com', '654 Pine Ave', 5);

INSERT INTO school_admin (login_id, passwd, first_name, last_name, sex, birth_date, school_id, admin_id, scadmin_status)
VALUES ('sadmin1', 'password1', 'John', 'Doe', 'Male', '1990-05-20', 11, 1, 'Approved'),
('sadmin2', 'password2', 'Jane', 'Doe', 'Female', '1995-01-12', 12, 1, 'Waiting'),
('sadmin3', 'password3', 'Alice', 'Smith', 'Female', '1992-09-06', 13, 1, 'Declined'),
('sadmin4', 'password4', 'Bob', 'Johnson', 'Male', '1988-12-31', 14, 1, 'Waiting'),
('sadmin5', 'password5', 'Chris', 'Lee', 'Other', '1998-07-15', 15, 1, 'Approved');

INSERT INTO user (login_id, passwd, first_name, last_name, birth_date, job, books_borrowed, user_status)
VALUES ('user1', 'password1', 'Alice', 'Smith', '2005-01-01', 'Student', 1, 'Waiting'),
('user2', 'password2', 'Bob', 'Johnson', '1995-05-20', 'Teacher', 1, 'Approved'),
('user3', 'password3', 'Chris', 'Lee', '2003-09-06', 'Student', 1, 'Waiting'),
('user4', 'password4', 'David', 'Kim', '1998-12-31', 'Teacher', 1, 'Declined'),
('user5', 'password5', 'Emma', 'Wilson', '2002-07-15', 'Student', 1, 'Approved');

INSERT INTO book (book_title, publisher, no_pages, summary, available, sprache, school_id, scadmin_id)
VALUES ('Harry Potter and the Philosopher''s Stone', 'Bloomsbury Publishing', 223, 'The first book in the Harry Potter series.', 5, 'English', 11, 21),
('The Lord of the Rings', 'George Allen & Unwin', 1178, 'A trilogy that tells the story of a hobbit named Frodo Baggins and his quest to destroy the One Ring.', 5, 'English', 12, 23),
('To Kill a Mockingbird', 'J. B. Lippincott & Co.', 281, 'A novel set in the Southern United States during the Great Depression, and follows the story of a young girl named Scout Finch.', 5, 'English', 13, 23),
('The Catcher in the Rye', 'Little, Brown and Company', 277, 'A novel that tells the story of Holden Caulfield, a teenage boy who is expelled from his school and goes on a journey of self-discovery.', 5, 'English', 14, 22),
('The Great Gatsby', 'Charles Scribner''s Sons', 180, 'A novel set in the Roaring Twenties, and follows the story of a young man named Jay Gatsby and his obsession with a woman named Daisy Buchanan.', 5, 'English', 15, 25);

INSERT INTO review (ISBN, user_id, review_date, txt, likert, review_status)
VALUES (11, 1, '2022-04-15', 'Great book, loved the story and the characters!', 'Positive', 'Approved'),
(12, 2, '2022-03-22', 'One of my favorite books of all time, the world building is amazing.', 'Positive', 'Approved'),
(13, 3, '2022-05-10', 'This book was required reading in school and I hated it at the time, but looking back I can appreciate its message.', 'Neutral', 'Approved'),
(14, 1, '2022-01-05', 'This book was very boring and I didn''t enjoy it at all.', 'Negative', 'Declined'),
(15, 2, '2022-02-28', 'I loved the characters and the setting, but the ending was disappointing.', 'Neutral', 'Waiting');

INSERT INTO author (first_name, last_name, ISBN)
VALUES ('J.K.', 'Rowling', 11),
('J.R.R.', 'Tolkien', 12),
('Harper', 'Lee', 13),
('J.D.', 'Salinger', 14),
('F. Scott', 'Fitzgerald', 15);

INSERT INTO category (category, ISBN)
VALUES ('Fantasy', 11),
('Fantasy', 12),
('Classics', 13),
('Classics', 14),
('Classics', 15);

INSERT INTO keywords (keyword, ISBN)
VALUES ('Magic', 11),
('Adventure', 12),
('Racism', 13),
('Coming of Age', 13),
('Alienation', 14);

-- Insert data into the reservation table
INSERT INTO reservation (ISBN, user_id, reservation_date, reservation_status)
VALUES (11, 1, '2023-05-15', 'Waiting'),
(12, 2, '2023-05-16', 'Approved'),
(13, 3, '2023-05-17', 'Waiting'),
(13, 4, '2023-05-18', 'Declined'),
(14, 5, '2023-05-19', 'Waiting');

-- Insert data into the borrowing table
INSERT INTO borrowing (ISBN, user_id, borrowing_date, borrowing_status, scadmin_id)
VALUES (11, 1, '2023-05-20', 'Waiting', 21),
(13, 2, '2023-05-21', 'Approved', 22),
(12, 3, '2023-05-22', 'Waiting', 21),
(12, 4, '2023-05-23', 'Declined', 23),
(14, 5, '2023-05-24', 'Completed', 22);