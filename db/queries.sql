---------------------------------------USER_BOOKSEARCH--------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE search_book(
        IN which_title VARCHAR(50),
        IN which_author_name VARCHAR(50),
        IN which_category VARCHAR(50),
        IN schoolid INT
    )
        READS SQL DATA
        COMMENT 'Search Book'
    BEGIN
        SELECT book.ISBN, book.book_title, author.first_name, author.last_name, book.publisher, book.no_pages, book.available, book.sprache, book.img, category.category
        FROM book
        INNER JOIN author ON book.ISBN = author.ISBN
        INNER JOIN category ON book.ISBN = category.ISBN
        INNER JOIN keywords ON book.ISBN = keywords.ISBN
        WHERE ((which_title = '' OR book.book_title LIKE CONCAT('%', which_title, '%')) AND
                (which_author_name = '' OR
                (author.first_name LIKE CONCAT('%', which_author_name, '%')) OR
                (author.last_name LIKE CONCAT('%', which_author_name, '%')) OR
                (CONCAT(author.first_name, ' ', author.last_name) LIKE CONCAT('%', which_author_name, '%'))) AND
                (which_category = '' OR
                EXISTS (SELECT * FROM category WHERE (category.ISBN = book.ISBN AND category.category = which_category))) AND
                (book.school_id = schoolid))
        ORDER BY book.book_title;
    END;

//
DELIMITER ;

-- -------------------------------------SCADMIN_BOOKLIST--------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE booklist(
        IN which_title VARCHAR(50),
        IN which_author_name VARCHAR(50),
        IN which_category VARCHAR(50),
        IN which_availabiliity INT,
        IN schoolid INT
    )   
        READS SQL DATA
        COMMENT 'Booklist'
    BEGIN
        SELECT book.ISBN, book.book_title, author.first_name, author.last_name, book.publisher, book.no_pages, book.available, book.sprache, book.img 
        FROM book 
        INNER JOIN author ON book.ISBN = author.ISBN
        WHERE ((which_title = '' OR book.book_title LIKE CONCAT('%', which_title, '%')) AND
                (which_author_name = '' OR
                (author.first_name LIKE CONCAT('%', which_author_name, '%')) OR
                (author.last_name LIKE CONCAT('%', which_author_name, '%')) OR
                (CONCAT(author.first_name, ' ', author.last_name) LIKE CONCAT('%', which_author_name, '%'))) AND
                 (which_availabiliity = -1 OR book.available = which_availabiliity) AND
                 (which_category = '' OR 
                  EXISTS(SELECT * FROM category WHERE (category.ISBN = book.ISBN AND category.category = which_category))) AND
                  (book.school_id = schoolid))
        ORDER BY book.title;
    END;
//
DELIMITER ;

-------------------------------------BOOK DETAILS----------------------------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE details(
        IN ISBN INT,
        IN school_id INT
    )
        READS SQL DATA
        COMMENT 'Details'
    BEGIN 
        SELECT book.book_title, author.first_name, author.last_name, book.publisher, book.summary, book.no_pages, category.category, keywords.keywords, book.sprache, book.ISBN, book.img
        FROM book 
        INNER JOIN author ON author.ISBN = book.ISBN
        INNER JOIN category ON category.ISBN = book.ISBN 
        INNER JOIN keywords ON keywords.ISBN = book.ISBN 
        WHERE ( (book.ISBN = ISBN) AND (book.school_id = school_id) );
    END;
//
DELIMITER ;

-------------------------------------USERS LIST---------------------------------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE userlist(
        IN which_user VARCHAR(50),
        IN schoolid INT,
        IN user_status VARCHAR(50)
    )   
        READS SQL DATA
        COMMENT 'Userlist'
    BEGIN
        SELECT user.first_name, user.last_name, user.job, user.birth_date, user.books_borrowed, user.user_status, user.user_id
        FROM user 
        WHERE ( (which_user = '' OR
                (user.first_name LIKE CONCAT('%', which_user, '%')) OR
                (user.last_name LIKE CONCAT('%', which_user, '%')) OR
                (CONCAT(user.first_name, ' ', user.last_name) LIKE CONCAT('%', which_user, '%'))) AND
                (user.school_id = schoolid) AND 
                (user.user_status = user_status))
        ORDER BY user.last_name;
    END;
//
DELIMITER ;



------------------------------------------------3.1------------------------------------------------------
---------------------------3_1_1-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_1(
        IN which_year YEAR,
        IN which_month MEDIUMINT
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.1'
    BEGIN
        SELECT school.school_name, COUNT(borrowing_id)
        FROM school
        INNER JOIN book ON school.school_id = book.school_id
        INNER JOIN borrowing ON (book.ISBN = borrowing.ISBN AND
                                (which_year = 0 OR YEAR(borrowing.borrowing_date) = which_year)
                                AND (which_month = 0 OR MONTH(borrowing.borrowing_date) = which_month)
                                AND (borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Completed')) 
        GROUP BY school.school_id, school.school_name 
        ORDER BY school.school_name DESC;   
    END;
//
DELIMITER ;
---------------------------3_1_2_1-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_2_1(
        IN which_category VARCHAR(50)
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.2.1'
    BEGIN
        SELECT DISTINCT author.first_name, author.last_name 
        FROM author 
        WHERE (which_category = '' OR EXISTS (SELECT * FROM category 
                    WHERE (author.ISBN = category.ISBN AND category.category = which_category)))
        ORDER BY author.last_name, author.first_name DESC;
    END;
//
DELIMITER ;
---------------------------3_1_2_2------------------------------- 
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_2_2(
        IN which_category VARCHAR(50)
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.2.2'
    BEGIN
        SELECT DISTINCT user.first_name, user.last_name
        FROM user 
        RIGHT JOIN borrowing ON user.user_id = borrowing.user_id
        WHERE (which_category = '' OR (user.job = 'Teacher' AND DATEDIFF(NOW(), CAST(borrowing.borrowing_date AS DATETIME)) < 365 AND 
              (borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Completed') 
              AND EXISTS (SELECT * FROM category 
              WHERE (borrowing.ISBN = category.ISBN AND category.category = which_category))))
        ORDER BY user.last_name, user.first_name DESC;
    END;
//
DELIMITER ;
---------------------------3_1_3-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_3()
        READS SQL DATA
        COMMENT 'Exercise 3.1.3'
    BEGIN
            SELECT COUNT(borrowing.borrowing_id), user.first_name, user.last_name
            FROM user 
            INNER JOIN borrowing ON user.user_id = borrowing.user_id
            WHERE (user.job = 'Teacher' AND DATEDIFF(NOW(), CAST(user.birth_date AS DATETIME)) < 14600 AND 
                    (borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Completed'))
            GROUP BY user.user_id 
            ORDER BY COUNT(borrowing.borrowing_id) DESC;
    END;
//
DELIMITER ;
---------------------------3_1_4-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_4()
        READS SQL DATA
        COMMENT 'Exercise 3.1.4'
    BEGIN
        SELECT author.first_name, author.last_name
        FROM author 
        LEFT JOIN borrowing ON author.ISBN = borrowing.ISBN 
        WHERE (borrowing.ISBN IS NULL OR borrowing.borrowing_status = 'Waiting' OR borrowing.borrowing_status = 'Declined')
        ORDER BY author.first_name DESC;
    END;
//
DELIMITER ;
---------------------------3_1_5-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_5(
        IN which_year YEAR
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.5'
    BEGIN
        SELECT COUNT(borrowing.borrowing_id), school_admin.first_name, school_admin.last_name
        FROM school_admin 
        INNER JOIN borrowing ON school_admin.scadmin_id = borrowing.scadmin_id 
        WHERE ((which_year = 0 OR YEAR(borrowing.borrowing_date) = which_year) AND 
                (borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Completed'))
        GROUP BY school_admin.scadmin_id
        ORDER BY COUNT(borrowing.borrowing_id) DESC;
    END
//
DELIMITER ;

---------------------------3_1_6-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_6()
        READS SQL DATA
        COMMENT 'Exercise 3.1.6'
    BEGIN
        SELECT COUNT(borrowing.ISBN) AS best_3, category1.category AS first_cat, category2.category AS second_cat
        FROM category AS category1
        INNER JOIN category AS category2 ON category1.category < category2.category
        INNER JOIN borrowing ON (borrowing.ISBN = category1.ISBN AND borrowing.ISBN = category2.ISBN)
        GROUP BY category1.category, category2.category
        ORDER BY COUNT(borrowing.ISBN) DESC LIMIT 3;   
END;
//
DELIMITER ;

---------------------------3_1_7-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_7()
        READS SQL DATA
        COMMENT 'Exercise 3.1.7'
    BEGIN
        SELECT COUNT(author.ISBN) AS how_many, author.first_name, author.last_name 
        FROM author
        GROUP BY author.first_name, author.last_name
        HAVING (MAX(how_many) - how_many >= 5)
        ORDER BY author.first_name, author.last_name;
    END;
//
DELIMITER ;
------------------------------------------------3.2------------------------------------------------------
------------------------------------------------3.2.1------------------------------------------------------
/*DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_2_1(
        IN which_title VARCHAR(50),
        IN which_author_name VARCHAR(50),
        IN which_category VARCHAR(50),
        IN which_availabiliity INT
    )
        READS SQL DATA
        COMMENT 'Exercise 3.2.1'
    BEGIN
        SELECT author.first_name, author.last_name, book.book_title
        FROM book 
        INNER JOIN author ON book.ISBN = author.ISBN
        WHERE ((which_title = '' OR book.book_title LIKE CONCAT('%', which_title, '%')) AND
                (which_author_name = '' OR
                (author.first_name LIKE CONCAT('%', which_author_name, '%')) OR
                (author.last_name LIKE CONCAT('%', which_author_name, '%'))) AND
                 (which_availabiliity = -1 OR book.available = which_availabiliity) AND
                 (which_category = '' OR 
                  EXISTS(SELECT * FROM category WHERE (category.ISBN = book.ISBN AND category.category = which_category))))
        ORDER BY author.first_name;
    END;
//
DELIMITER ;*/

------------------------------------------------3.2.2------------------------------------------------------
DELIMITER //
CREATE DEFINER='root'@'localhost' PROCEDURE question_3_2_2(
    IN delaying INT UNSIGNED,
    IN which_user_firstname VARCHAR(50),
    IN which_user_lastname VARCHAR(50)
)
    READS SQL DATA
    COMMENT 'Exercise 3.2.2'
BEGIN
    SELECT user.first_name, user.last_name
    FROM user
    RIGHT JOIN borrowing ON user.user_id = borrowing.user_id
    WHERE (((which_user_firstname = '' AND which_user_firstname = '') OR
            (user.first_name = which_user_firstname AND user.last_name = which_user_lastname)) AND
            (DATEDIFF(NOW(), CAST(borrowing.borrowing_date AS DATETIME)) >= 7 AND borrowing.borrowing_status = 'Approved') AND 
            (delaying = 0 OR DATEDIFF(NOW(), CAST(borrowing.borrowing_date AS DATETIME)) = delaying))
    ORDER BY user.first_name DESC;
END;
//
DELIMITER ;

------------------------------------------------3.2.3------------------------------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_2_3()
        READS SQL DATA
        COMMENT 'Exercise 3.2.3'
    BEGIN
        -- The fuck is this
    END;
//
DELIMITER ;
------------------------------------------------3.3------------------------------------------------------
------------------------------------------------3.3.1------------------------------------------------------
--It's the same as 3.2.1, just default setting availability to -1.
------------------------------------------------3.3.2------------------------------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_3_2(
        IN which_user MEDIUMINT UNSIGNED
    )
        READS SQL DATA
        COMMENT 'Exercise 3.3.2'
    BEGIN
        SELECT book.book_title 
        FROM borrowing 
        LEFT JOIN book ON borrowing.ISBN = book.ISBN 
        WHERE (borrowing.user_id = which_user AND (borrowing.borrowing_status = 'Completed' OR borrowing.borrowing_status = 'Approved'))
        ORDER BY book.book_title;
    END;
//
DELIMITER ;

------------------------Extras that occured while builidng the app--------------------------
--Checking borrowing
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE borrowing_approve(
        IN id INT,
        IN job NVARCHAR(50),
        IN bookISBN INT,
        IN schoolid INT
    )   
        READS SQL DATA
        COMMENT 'Borrow check'
    BEGIN
        SET @checker = 1;

        SELECT books_borrowed INTO @booksborrowed FROM user WHERE user_id = id;

        SELECT borrowing_id INTO @bookoverdue FROM borrowing 
        WHERE borrowing_status = 'Approved' AND 
                DATEDIFF(CURRENT_TIMESTAMP, CAST(borrowing_date AS DATETIME)) >= 7 AND 
                user_id = id;
        SELECT FOUND_ROWS() INTO @bookoverdue;

        SELECT COUNT(borrowing_id) INTO @booksborrowed_perweek FROM borrowing 
        WHERE (borrowing_status = 'Approved' OR borrowing_status = 'Completed') AND 
        DATEDIFF(CURRENT_TIMESTAMP, CAST(borrowing_date AS DATETIME)) < 7 AND 
        user_id = id
        GROUP BY user_id;

        SELECT * INTO @againcheck_borrowing
        FROM borrowing 
        INNER JOIN book ON (book.ISBN = bookISBN AND borrowing.ISBN = bookISBN 
                            AND book.school_id = schoolid AND borrowing.school_id = schoolid)
        WHERE borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Waiting';
        SELECT FOUND_ROWS() INTO @againcheck_borrowing;

        SELECT * INTO @againcheck_reserving
        FROM reservation 
        INNER JOIN book ON (book.ISBN = bookISBN AND reservation.ISBN = bookISBN 
                            AND book.school_id = schoolid AND reservation.school_id = schoolid)
        WHERE reservation.reservation_status = 'Waiting';
        SELECT FOUND_ROWS() INTO @againcheck_reserving;

        IF job = 'Student' THEN
            IF (@booksborrowed = 2 OR @bookoverdue > 0 OR @booksborrowed_perweek = 2 OR 
                @againcheck_borrowing > 0 OR @againcheck_reserving > 0) THEN 
                    SET @checker = 0;
            END IF;
        ELSEIF job = 'Teacher' THEN 
            IF (@booksborrowed = 1 OR @bookoverdue > 0 OR @booksborrowed_perweek = 1 OR 
                @againcheck_borrowing > 0 OR @againcheck_reserving > 0) THEN 
                    SET @checker = 0;
            END IF;
        END IF;
    END;
//
DELIMITER ;