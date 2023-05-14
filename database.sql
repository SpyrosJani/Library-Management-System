-----------------------------------------Create Database----------------------------------------
CREATE DATABASE librarydbms;
use librarydbms;

-----------------------------------------Tables----------------------------------------
--administrator(admin_id, login_id, passwd, first_name, last_name, sex, birth_date)
CREATE TABLE administrator(
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
);

--school(school_id, school_name, city, phone_number, email, addrss, admin_id)
CREATE TABLE school(
    school_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    school_name VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    phone_number INT NOT NULL,
    email VARCHAR(50) NOT NULL,
    addrss VARCHAR(50) NOT NULL,
    admin_id INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (school_id),
    CONSTRAINT fk_school_administrator
        FOREIGN KEY (admin_id) REFERENCES administrator (admin_id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    UNIQUE (school_name),
    UNIQUE (phone_number),
    UNIQUE (addrss),
    UNIQUE (email)
);

--school_admin(scadmin_id, login_id, passwd, first_name, last_name, sex, birth_date, scadmin_status, school_id, admin_id)
CREATE TABLE school_admin(
    scadmin_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(50) NOT NULL,
    passwd VARCHAR(100) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    sex ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL,
    school_id INT UNSIGNED NOT NULL,
    admin_id INT UNSIGNED DEFAULT NULL,
    scadmin_status ENUM('Declined', 'Waiting', 'Approved') NOT NULL DEFAULT 'Waiting',
    PRIMARY KEY (scadmin_id),
    CONSTRAINT fk_school_admin_school
        FOREIGN KEY (school_id) REFERENCES school(school_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_school_admin_administrator
        FOREIGN KEY (admin_id) REFERENCES administrator(admin_id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE, 
    UNIQUE (login_id),
    CHECK (birth_date < '2000-01-01')
);

--user(user_id, login_id, passwd, first_name, last_name, birth_date, job, books_borrowed, user_status)
CREATE TABLE user(
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(50) NOT NULL,
    passwd VARCHAR(100) NOT NULL, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    job ENUM('Student', 'Teacher') NOT NULL,
    books_borrowed INT UNSIGNED NOT NULL DEFAULT 0,
    user_status ENUM('Waiting', 'Approved', 'Declined') NOT NULL DEFAULT 'Waiting',
    PRIMARY KEY (user_id),
    UNIQUE (login_id),
    CHECK ((birth_date <= '2018-01-01' AND job = 'Student') OR (birth_date <= '2000-01-01' AND job = 'Teacher'))
);


--book(ISBN, book_title, publisher, no_pages, summary, available, img, sprache, school_id, scadmin_id)
CREATE TABLE book(
    ISBN INT UNSIGNED NOT NULL AUTO_INCREMENT,
    book_title VARCHAR(100) NOT NULL,
    publisher VARCHAR(50) NOT NULL,
    no_pages INT UNSIGNED NOT NULL,
    summary TEXT NOT NULL,
    available INT UNSIGNED NOT NULL DEFAULT 1,
    img LONGBLOB, 
    sprache VARCHAR(50) DEFAULT 'English',
    school_id INT UNSIGNED NOT NULL,
    scadmin_id INT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (ISBN),
    CONSTRAINT fk_book_school
        FOREIGN KEY (school_id) REFERENCES school(school_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_book_administrator 
        FOREIGN KEY (scadmin_id) REFERENCES school_admin(scadmin_id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
);

--review(review_id, ISBN, user_id, review_date, txt, likert, review_status)
CREATE TABLE review(
    review_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    review_date DATE NOT NULL,
    txt TEXT NOT NULL,
    likert VARCHAR(50) DEFAULT NULL,
    review_status ENUM('Waiting', 'Approved', 'Declined') NOT NULL DEFAULT 'Waiting',
    PRIMARY KEY (review_id),
    CONSTRAINT fk_review_book
        FOREIGN KEY (ISBN) REFERENCES book(ISBN) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_review_user 
        FOREIGN KEY (user_id) REFERENCES user(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CHECK(CAST(review_date AS DATETIME)< NOW())
);

--author(author_id, first_name, last_name, ISBN)
CREATE TABLE author(
    author_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY (author_id), 
    CONSTRAINT fk_author_book
        FOREIGN KEY (ISBN) REFERENCES book(ISBN) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

--category(category_id, category, ISBN)
CREATE TABLE category(
    category_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    category VARCHAR(50) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY (category_id),
    CONSTRAINT fk_category_book
        FOREIGN KEY (ISBN) REFERENCES book(ISBN) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

--keyword(keyword_id, keyword, ISBN)
CREATE TABLE keywords(
    keyword_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    keyword VARCHAR(20) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY (keyword_id),
    CONSTRAINT fk_keywords_book
        FOREIGN KEY (ISBN) REFERENCES book(ISBN) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

--reservation(reservation_id, ISBN, user_id, reservation_date, reservation_status)
CREATE TABLE reservation(
    reservation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_status ENUM('Waiting', 'Approved', 'Declined') NOT NULL DEFAULT 'Waiting',
    PRIMARY KEY (reservation_id),
    CONSTRAINT fk_reservation_book
        FOREIGN KEY (ISBN) REFERENCES book(ISBN) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_reservation_user
        FOREIGN KEY (user_id) REFERENCES user(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CHECK(CAST(reservation_date AS DATETIME) < NOW())
);

--borrowing(borrowing_id, ISBN, user_id, borrowing_date, borrowing_status, scadmin_id)
CREATE TABLE borrowing(
    borrowing_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    borrowing_date DATE NOT NULL,
    borrowing_status ENUM('Waiting', 'Approved', 'Declined', 'Completed') DEFAULT 'Waiting',
    scadmin_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (borrowing_id),
    CONSTRAINT fk_borrowing_book
        FOREIGN KEY (ISBN) REFERENCES book(ISBN) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_borrowing_user
        FOREIGN KEY (user_id) REFERENCES user(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_borrowing_scadmin 
        FOREIGN KEY (scadmin_id) REFERENCES school_admin(scadmin_id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CHECK(CAST(borrowing_date AS DATETIME) < NOW())
);

-----------------------------------------Indexes-------------------------------------------------------
--Gonna add some indexes here
CREATE INDEX idx_author ON author (first_name, last_name, ISBN);
CREATE INDEX idx_category ON category (category, ISBN);
CREATE INDEX idx_user ON user (first_name, last_name, job, user_status, books_borrowed);
CREATE INDEX idx_school ON school (school_id, school_name);
CREATE INDEX idx_borrowing ON borrowing (ISBN, user_id, borrowing_date, borrowing_status, scadmin_id);
CREATE INDEX idx_book ON book (ISBN, book_title, school_id, scadmin_id);
CREATE INDEX idx_school_admin ON scadmin (scadmin_id, first_name, last_name);
-----------------------------------------Triggers-----------------------------------------
DELIMITER// 
--Approving or declining a user
CREATE TRIGGER user_state AFTER UPDATE ON user FOR EACH ROW
BEGIN
    IF NEW.user_status = 'Approved' THEN 
        UPDATE user
            SET user_status = NEW.user_status
        WHERE user_id = OLD.user_id;
    ELSEIF NEW.user_status = 'Declined' THEN 
        DELETE FROM librarydbms.user WHERE user_id = OLD.user_id;
    END IF;
END;//

DELIMETER ;

DELIMITER// 
--Approving or declining a school admin
CREATE TRIGGER scadmin_state AFTER UPDATE ON school_admin FOR EACH ROW
BEGIN
    IF NEW.scadmin_status = 'Approved'  THEN 
        UPDATE school_admin
            SET scadmin_status = NEW.scadmin_status
        WHERE scadmin_id = OLD.scadmin_id;
    ELSEIF (NEW.scadmin_status = 'Declined')  THEN 
        DELETE FROM librarydbms.school_admin WHERE scadmin_id = OLD.scadmin_id;
    END IF;
END;//

DELIMETER ;

DELIMITER// 
--Approving or declining a review
CREATE TRIGGER review_state AFTER UPDATE ON review FOR EACH ROW
BEGIN
    IF NEW.review_status = 'Approved'  THEN 
        UPDATE review
            SET review_status = NEW.review_status
        WHERE review_id = OLD.review_id;
    ELSEIF NEW.review_status = 'Declined'  THEN
        DELETE FROM librarydbms.review WHERE review_id = OLD.review_id;
    END IF;
END;//

DELIMETER ;

DELIMITER// 
--reservation handler
CREATE TRIGGER reservation_state AFTER UPDATE ON reservation FOR EACH ROW
BEGIN
    IF (NEW.reservation_status = 'Approved') THEN
        INSERT INTO borrowing(borrowing_id, ISBN, user_id, borrowing_date, borrowing_status)
        VALUES (NEW.reservation_id, OLD.ISBN, OLD.user_id, CURRENT_TIMESTAMP, 'Approved');
        UPDATE user 
            SET user.books_borrowed = user.books_borrowed+1
        WHERE user.user_id = OLD.user_id;
        UPDATE book
            SET book.available = book.available-1
        WHERE book.ISBN = OLD.ISBN;
        DELETE FROM reservation WHERE reservation_id = OLD.reservation_id;
    ELSEIF (NEW.reservation_status = 'Declined') THEN 
        DELETE FROM reservation WHERE reservation_id = OLD.reservation_id;
    END IF;
END;//

DELIMETER ;

DELIMITER// 
--borrowing handler
CREATE TRIGGER borrowing_state AFTER UPDATE ON borrowing FOR EACH ROW 
BEGIN
    IF NEW.borrowing_status = 'Approved' THEN
        UPDATE user 
            SET user.books_borrowed = user.books_borrowed+1
        WHERE user.user_id = OLD.user_id;
        UPDATE book
            SET book.available = book.available-1
        WHERE book.ISBN = OLD.ISBN;
    ELSEIF NEW.borrowing_status = 'Completed' THEN 
        UPDATE user 
            SET user.books_borrowed = user.books_borrowed-1
        WHERE user.user_id = OLD.user_id;
        UPDATE book
            SET book.available = book.available+1
        WHERE book.ISBN = OLD.ISBN;
    ELSEIF NEW.borrowing_status = 'Declined' THEN
        DELETE FROM borrowing WHERE borrowing_id = OLD.borrowing_id;
    END IF; 
END;//

DELIMETER ;
-----------------------------------------Views-----------------------------------------
CREATE VIEW administrator_view AS
    SELECT admin_id, login_id, first_name, last_name, birth_date 
    FROM administrator; 

CREATE VIEW school_admin_view AS 
    SELECT scadmin_id, login_id, first_name, last_name, birth_date, school_id
    FROM school_admin; 

CREATE VIEW school_view AS 
    SELECT school_id, school_name, city, phone_number, email, addrss 
    FROM school; 

CREATE VIEW user_view AS
    SELECT user_id, login_id, first_name, last_name, birth_date, job, books_borrowed
    FROM user; 

CREATE VIEW book_view AS 
    SELECT school_id, book_title, publisher, no_pages, summary, available, sprache
    FROM book; 

CREATE VIEW author_view AS
    SELECT first_name, last_name 
    FROM author; 

CREATE VIEW category_view AS
    SELECT category 
    FROM category;

CREATE VIEW keywords_view AS
    SELECT keyword 
    FROM keywords; 

--Erasing every day the too delayed reservations
CREATE EVENT too_delayed
ON SCHEDULE EVERY 1 DAY
DO
    DELETE FROM librarydbms.reservation 
    WHERE (DATEDIFF(NOW(), CAST(reservation_date AS DATETIME)) >= 7 AND reservation_status = 'Waiting');


------------------------Extras that occured while builidng the app--------------------------

