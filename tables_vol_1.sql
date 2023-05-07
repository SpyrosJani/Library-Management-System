--Changes that i have done (apart from those i proposed in discord):
--Line 21: I added a check (i need him to be at least 23 years old)
--Line 39: The same as above
--Line 78: I added a default to 0, so as not it is necessary to put something
--Line 82: Just a check on the age whether there is a student (>=8) or a Teacher (>=23)
--Line 92: Default null, not necessary to answer the questionaire
--Line 108: Book availability defaults to 0
--Line 110: Language defaults to English
--Line 149: Reservation date defaults to the date when the reservation is done
--Line 162: Pretty much the same as in line 149
--Line 166: Checking if the borrowing date is later than the respective reservation date.
--This is necessary because we convert the reservation to a borrowing, so the respective borrowing can not be
--before the respective reservation.
--Lines ?:Wherever we have a status, i default it at Waiting
--See later comments for further changes 
-----------------------------------------Database----------------------------------------
CREATE DATABASE [IF NOT EXISTS] LibraryDBMS
use LibraryDBMS;

--administrator(admin_id, login_id, passwd, first_name, last_name, sex, birth_date)
CREATE TABLE [IF NOT EXISTS] administrator {
    admin_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(50) NOT NULL,
    passwd VARCHAR(100) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    sex ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL,
    PRIMARY KEY (admin_id),
    UNIQUE (login_id),
    CHECK (birth_date < '2000-01-01')
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--school_admin(scadmin_id, login_id, passwd, first_name, last_name, sex, birth_date, school_id, admin_id)
CREATE TABLE [IF NOT EXISTS] school_admin {
    scadmin_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(50) NOT NULL,
    passwd VARCHAR(100) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    sex ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL,
    school_id INT UNSIGNED NOT NULL,
    amdin_id INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (scadmin_id),
    FOREIGN KEY (school_id) REFERENCES school(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES administrator(admin_id) ON DELETE SET NULL ON UPDATE CASCADE, 
    UNIQUE (login_id),
    CHECK (birth_date < '2000-01-01')
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--school(school_id, school_name, city, phone_number, email, addrss, admin_id)
CREATE TABLE [IF NOT EXISTS] school {
    school_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    school_name VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL,
    addrss VARCHAR(50) NOT NULL,
    admin_id INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (school_id),
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE (school_name),
    UNIQUE (phone_number),
    UNIQUE (addrss),
    UNIQUE (email)
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--user(user_id, login_id, passwd, first_name, last_name, birth_date, job, books_borrowed, user_status)
CREATE TABLE [IF NOT EXISTS] user {
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(50) NOT NULL,
    passwd VARCHAR(100) NOT NULL, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    job ENUM('Student', 'Teacher') NOT NULL,
    books_borrowed INT UNSIGNED NOT NULL DEFAULT 0,
    user_status ENUM('Waiting', 'Approved', 'Declined') DEFAULT 'Waiting',
    PRIMARY KEY (user_id),
    UNIQUE (login_id),
    CHECK ((birthday <= '2015-01-01' AND job = 'Student') OR (birthday <= '2000-01-01' AND job = 'Teacher'))
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--review(review_id, ISBN, user_id, review_date, txt, likert, review_status)
CREATE TABLE [IF NOT EXISTS] review {
    review_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN INT UNSIGNED NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    review_date DATE NOT NULL,
    txt TEXT(1000) NOT NULL,
    likert VARCHAR(50) DEFAULT NULL,
    review_status ENUM('Waiting', 'Approved', 'Declined') DEFAULT 'Waiting',
    PRIMARY KEY (review_id),
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--book(ISBN, book_title, publisher, no_pages, summary, available, img, sprache, school_id, scadmin_id)
CREATE TABLE [IF NOT EXISTS] book {
    ISBN INT UNSIGNED NOT NULL AUTO_INCREMENT,
    book_title VARCHAR(100) NOT NULL,
    publisher VARCHAR(50) NOT NULL,
    no_pages INT UNSIGNED NOT NULL,
    summary TEXT(1000) NOT NULL,
    available INT UNSIGNED NOT NULL DEFAULT 1,
    img BLOB,
    sprache VARCHAR(50) DEFAULT 'English',
    school_id INT UNSIGNED NOT NULL,
    scadmin_id INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (ISBN),
    FOREIGN KEY (school_id) REFERENCES school(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (scadmin_id) REFERENCES school_admin(scadmin_id) ON DELETE SET NULL ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--author(author_id, first_name, last_name, ISBN)
CREATE TABLE [IF NOT EXISTS] author {
    author_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY (author_id), 
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--category(category_id, category, ISBN)
CREATE TABLE [IF NOT EXISTS] category {
    category_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    category VARCHAR(50) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY (category_id),
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--keyword(keyword_id, keyword, ISBN)
CREATE TABLE [IN NOT EXISTS] keywords {
    keyword_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    keyword VARCHAR(20) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY (category_id),
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE,
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--reserv_borrow(reserv_borrow_id, ISBN, user_id, reserv_borrow_date, reserv_borrow_status)
CREATE TABLE [IF NOT EXISTS] reserv_borrow {
    reser_borrow_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    reserv_borrow_date DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reserv_borrow_status ENUM ('Waiting', 'Approved', 'Declined', 'Returned') DEFAULTS 'Waiting',
    PRIMARY KEY (reserv_borrow_id),
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--The code from here and below is new, i wrote it today (7-5-2023):
--Let's see about the indexes. We will definitely need the book_title (in many staff). Then, it is easier to call admin, school admin, school, author
--and user with their names rather than with their ids. So we are gonna index them to. In the end, book categories and keywords are also easier to find
--with their description, so i am gonna index them too. We also dont want duplicate values (for example when we need a book, we will need it's title, i
--dont want to have 2 books with the same title, the whole indexing point is lost this way). So i will use the UNIQUE keyword

--book_title index
CREATE UNIQUE INDEX index_book ON book(book_title);
--admin name index
CREATE UNIQUE INDEX index_admin ON administrator(first_name, last_name);
--school admin name index
CREATE UNIQUE INDEX index_school_admin ON school_admin(first_name, last_name);
--school name index
CREATE UNIQUE INDEX index_school ON school(school_name);
--author name index
CREATE UNIQUE INDEX index_author ON author(first_name, last_name);
--user name index
CREATE UNIQUE INDEX index_user ON user(first_name, last_name);
--category index
CREATE UNIQUE INDEX index_category ON category(category);
--keywords index
CREATE UNIQUE INDEX index_keyword ON keywords(keyword);

-----------------------------------------Database-----------------------------------------

--I also wrote the next code (it is about the triggers, those are the triggers i thought we should use, we talk about it):
--So, we will deal with 'borrowing' and the relation between 'borrowing' and 'reservation'. The reason for that
--is that in whichever other entity, if we do an UPDATE, DELETE, INSERT, the database is created in such a way that we dont have to do something.
--Only when the status of the respctive entity is invoked i will deal with it through triggers (for example if the status is declined then i will delete
--the respective entities).The cascades will do it for us. Data is also added in the database manually, so that's why i chose these to be the triggers
--In the end i am just gonna need a function which deletes all reservations (every time the database is activated) if more than two weeks have passed and
--nothing happened

-----------------------------------------Triggers and functions-----------------------------------------
DELIMITER $$

--Approving or declining a user
CREATE TRIGGER 'user_state' AFTER UPDATE ON 'user' FOR EACH ROW
    BEGIN
        IF (NEW.user_status = 'Approved')
        THEN 
            UPDATE user
                SET user_status = NEW.user_status
            WHERE user_id = OLD.user_id;
        END IF;
        IF (NEW.user_status = 'Declined')
        THEN 
            DELETE FROM LibraryDBMS user WHERE user_id = OLD.user_id;
        END IF;
    END $$

--Approving or declining a review
CREATE TRIGGER 'review_state' AFTER UPDATE ON 'review' FOR EACH ROW
    BEGIN
        IF (NEW.review_status = 'Approved')
        THEN 
            UPDATE review
                SET review_status = NEW.review_status
            WHERE review_id = OLD.review_id;
        END IF;
        IF (NEW.review_status = 'Declined')
        THEN
            DELETE FROM LibraryDBMS review WHERE review_id = OLD.review_id;
        END IF;
    END $$

--Checking the reservation-borrowing relation
CREATE TRIGGER 'reservation_borrowing' AFTER UPDATE ON 'reserv_borrow' FOR EACH ROW
    BEGIN
        IF (NEW.reserv_borrow_status = 'Approved')
        THEN
            UPDATE reserv_borrow 
                SET reserv_borrow_status = NEW.reserv_borrow_status, reserv_borrow_date = CURRENT_TIMESTAMP
            WHERE reserv_borrow_id = OLD.reserv_borrow_id;
            UPDATE user 
                SET books_borrowed += 1
            WHERE user_id = OLD.reserv_borrow.user_id;
            UPDATE book
                SET available -= 1
            WHERE ISBN = OLD.reserv_borrow.ISBN;
        END IF;
        IF (NEW.reservation_status = 'Returned')
        THEN
            UPDATE reserv_borrow 
                SET reserv_borrow_status = 'Declined'
            WHERE reserv_borrow_id = OLD.reserv_borrow_id;
            UPDATE user 
                SET books_borrowed -= 1
            WHERE user_id = OLD.reserv_borrow.user_id;
            UPDATE book
                SET available += 1
            WHERE ISBN = OLD.reserv_borrow.ISBN;
        END IF;
        IF (NEW.reservation_status = 'Declined')
        THEN 
            DELETE FROM LibraryDBMS reservation WHERE reserv_borrow_id = OLD.reserv_borrow_id
        END IF;
    END $$

DELIMETER ;
-----------------------------------------Triggers and functions-----------------------------------------

-----------------------------------------Views-----------------------------------------
--Pretty much gonna build the matrixes, i propose we should insert them all
CREATE VIEW [administrator_view] AS
SELECT admin_id, login_id, first_name, last_name, sex, birth_date 
FROM administrator 

CREATE VIEW [school_admin_view] AS 
SELECT scadmin_id, login_id, first_name, last_name, sex, birth_date
FROM school_admin 

CREATE VIEW [school_view] AS 
SELECT school_id, school_name, city, phone_number, email, addrss 
FROM school 

CREATE VIEW [user_view] AS
SELECT user_id, login_id, first_name, last_name, birth_date, job, books_borrowed
FROM user 

CREATE VIEW [book_view] AS 
SELECT ISBN, book_title, publisher, no_pages, summary, available, sprache
FROM book 

CREATE VIEW [author_view] AS
SELECT author_id, first_name, last_name, ISBN 
FROM author 

CREATE VIEW [category_view] AS
SELECT category_id, category, ISBN 
FROM category

CREATE VIEW [keywords_view] AS
SELECT keyword_id, keyword, ISBN 
FROM keywords 
