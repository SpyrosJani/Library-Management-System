CREATE DATABASE LibraryDBMS
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
    UNIQUE (login_id)
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--school_admin(scadmin_id, login_id, passwd, first_name, last_name, sex, birth_date, school_id, ISBN)
CREATE TABLE [IF NOT EXISTS] school_admin {
    scadmin_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(50) NOT NULL,
    passwd VARCHAR(100) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    sex ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL,
    school_id INT UNSIGNED NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY (scadmin_id),
    FOREIGN KEY (school_id) REFERENCES school(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(login_id)
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--school(school_id, school_name, city, phone_number, email, addrss)
CREATE TABLE [IF NOT EXISTS] school {
    school_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    school_name VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL,
    addrss VARCHAR(50) NOT NULL,
    PRIMARY KEY(school_id),
    UNIQUE(school_name),
    UNIQUE(phone_number),
    UNIQUE(addrss),
    UNIQUE(email)
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--registration(registartion_id, admin_id, school_id, scadmin_id)
CREATE TABLE [IF NOT EXISTS] registration {
    registration_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    admin_id INT UNSIGNED NOT NULL,
    school_id INT UNSIGNED NOT NULL,
    scadmin_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (registration_id),
    FOREIGN KEY (admin_id) REFERENCES administrator(admin_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (school_id) REFERENCES school(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (scadmin_id) REFERENCES school_admin(scadmin_id) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--user(user_id, login_id, passwd, first_name, last_name, birthday, job, books_borrowed, user_status)
CREATE TABLE [IF NOT EXISTS] user {
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    login_id VARCHAR(50) NOT NULL,
    passwd VARCHAR(100) NOT NULL, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birthday DATE NOT NULL,
    job ENUM('Student', 'Teacher') NOT NULL,
    books_borrowed INT UNSIGNED NOT NULL,
    user_status ENUM('Waiting', 'Approved', 'Declined'),
    PRIMARY KEY(user_id),
    UNIQUE(login_id)
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--review(review_id, book_title, user_id, review_date, txt, likert, review_status)
CREATE TABLE [IF NOT EXISTS] review {
    review_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN INT UNSIGNED NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    review_date DATE NOT NULL,
    txt TEXT(1000) NOT NULL,
    likert VARCHAR(50) NOT NULL,
    review_status ENUM('Waiting', 'Approved', 'Declined'),
    PRIMARY KEY(review_id),
    FOREIGN KEY(ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--book(ISBN, book_title, publisher, no_pages, summary, available, img, sprache, school_id)
CREATE TABLE [IF NOT EXISTS] book {
    ISBN INT UNSIGNED NOT NULL AUTO_INCREMENT,
    book_title VARCHAR(100) NOT NULL,
    publisher VARCHAR(50) NOT NULL,
    no_pages INT UNSIGNED NOT NULL,
    summary TEXT(1000) NOT NULL,
    available INT UNSIGNED NOT NULL,
    img BLOB,
    sprache VARCHAR(50) NOT NULL,
    school_id INT UNSIGNED NOT NULL,
    PRIMARY KEY(ISBN),
    FOREIGN KEY (school_id) REFERENCES school(school_id) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--author(author_id, first_name, last_name, ISBN)
CREATE TABLE [IF NOT EXISTS] author {
    author_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY(author_id), 
    FOREIGN KEY(ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

--category(category_id, category, ISBN)
CREATE TABLE [IF NOT EXISTS] category {
    category_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    category VARCHAR(50) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY(category_id),
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE [IN NOT EXISTS] keywords {
    keyword_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    keyword VARCHAR(20) NOT NULL,
    ISBN INT UNSIGNED NOT NULL,
    PRIMARY KEY(category_id),
    FOREIGN KEY(ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE [IF NOT EXISTS] reservation {
    reservation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ISBN INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_status ENUM ('Waiting', 'Approved', 'Declined'),
    PRIMARY KEY (reservation_id),
    FOREIGN KEY (ISBN) REFERENCES book(ISBN) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
}ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE [IF NOT EXISTS] borrowing {
    borrowing_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    reservation_id INT UNSIGNED NOT NULL,
    borrowing_date DATE NOT NULL,
    PRIMARY KEY(borrowing_id),
    FOREIGN KEY(reservation_id) REFERENCES reservation(reservation_id) ON DELETE CASCADE ON UPDATE RESTRICT    
}ENGINE=InnoDB DEFAULT CHARSET=utf8;


