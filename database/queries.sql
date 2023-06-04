--The following 3 questions are answered inside the python "routes.py" code in the respective lines that are being referred:
---question 3_2_2->2050-2092
--question 3_2_3->2178-2244
--question 3_3_2->Lines 616-644

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
        FROM borrowing
        INNER JOIN school_admin ON borrowing.scadmin_id = school_admin.scadmin_id 
        INNER JOIN school ON school.school_id = school_admin.school_id 
        WHERE ((which_year = 0 OR YEAR(borrowing.borrowing_date) = which_year) AND     
                (which_month = 0 OR MONTH(borrowing.borrowing_date) = which_month) AND 
                (borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Completed'))
        GROUP BY school.school_id 
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
        ORDER BY author.last_name DESC, author.first_name DESC;
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
        INNER JOIN borrowing ON user.user_id = borrowing.user_id 
        WHERE (user.job = 'Teacher' AND DATEDIFF(NOW(), CAST(borrowing.borrowing_date AS DATETIME)) < 365 AND 
                (borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Completed')
                AND (which_category = '' OR EXISTS (SELECT * FROM category 
                    WHERE (borrowing.ISBN = category.ISBN AND category.category = which_category))))
        GROUP BY user.user_id
        ORDER BY user.last_name DESC, user.first_name DESC;
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
        SELECT DISTINCT author.first_name, author.last_name
        FROM author 
        WHERE NOT EXISTS (SELECT * FROM borrowing 
                            WHERE (borrowing_status = 'Approved' OR borrowing_status = 'Completed') AND 
                            author.ISBN = borrowing.ISBN)
        ORDER BY author.first_name DESC, author.last_name DESC;
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
        HAVING COUNT(borrowing.borrowing_id) >= 20
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
        INNER JOIN category AS category2 ON category1.category_id < category2.category_id
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

------------------------Extras that occured while builidng the app--------------------------
------------------------Check to see if the borrowing can be approved and do the corresponding actions
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE borrowing_approve(
        IN borrowid INT,
        IN id INT,
        IN job NVARCHAR(50),
        IN bookISBN VARCHAR(50),
        IN schoolid INT,
        OUT checked INT,
        OUT availing INT
    )   
        READS SQL DATA
        COMMENT 'Borrow check'
    BEGIN
        SET @checker = 1;

        SELECT books_borrowed INTO @booksborrowed FROM user WHERE user_id = id;

        SELECT borrowing_id INTO @bookoverdue FROM borrowing 
        WHERE borrowing_status = 'Approved' AND 
                DATEDIFF(CURRENT_TIMESTAMP, CAST(borrowing_date AS DATETIME)) >= 7 AND 
                user_id = id
        LIMIT 1;
        SELECT FOUND_ROWS() INTO @bookoverdue;

        SELECT COUNT(borrowing_id) INTO @booksborrowed_perweek FROM borrowing 
        WHERE (borrowing_status = 'Approved' OR borrowing_status = 'Completed') AND 
        DATEDIFF(CURRENT_TIMESTAMP, CAST(borrowing_date AS DATETIME)) < 7 AND 
        user_id = id
        GROUP BY user_id;

        SELECT borrowing_id INTO @againcheck_borrowing
        FROM borrowing
        WHERE ((borrowing_status = 'Approved' OR borrowing_status = 'Waiting')
                AND ISBN = bookISBN AND user_id = id AND 
                schoolid = (SELECT school_id FROM school_admin WHERE scadmin_id = borrowing.scadmin_id) AND
                borrowing_id != borrowid)
        LIMIT 1;
        SELECT FOUND_ROWS() INTO @againcheck_borrowing;

        SELECT reservation_id INTO @againcheck_reserving
        FROM reservation 
        WHERE ((reservation_status = 'Waiting' OR reservation_status = 'Approved') AND ISBN = bookISBN AND user_id = id
               AND schoolid = (SELECT school_id FROM school_admin WHERE scadmin_id = reservation.scadmin_id))
        LIMIT 1;
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
        SELECT @checker AS checked;

        IF @checker = 0 THEN 
            DELETE FROM borrowing WHERE borrowing_id = borrowid;
        ELSEIF @checker = 1 THEN  
            SELECT available INTO @avail FROM book WHERE (book.ISBN = bookISBN AND school_id = schoolid);
            SELECT scadmin_id INTO @helper FROM borrowing WHERE borrowing_id = borrowid;
            IF @avail = 0 THEN
                INSERT INTO reservation(ISBN, user_id, reservation_date, reservation_to_date, reservation_status, scadmin_id)
                VALUES (bookISBN, id, CAST(CURRENT_TIMESTAMP AS DATE), CAST(CURRENT_TIMESTAMP AS DATE), 'Waiting Queue', @helper);
                DELETE FROM borrowing WHERE borrowing_id = borrowid;
            ELSEIF @avail > 0 THEN 
                UPDATE user 
                SET books_borrowed = books_borrowed + 1
                WHERE user_id = id;

                UPDATE borrowing 
                SET borrowing_date = CAST(CURRENT_TIMESTAMP AS DATE), borrowing_status = 'Approved' 
                WHERE borrowing_id = borrowid;

                UPDATE book 
                SET available = available - 1
                WHERE ISBN = bookISBN AND school_id = schoolid;
            END IF;
            SELECT @avail AS availing;
        END IF;
    END;
//
DELIMITER ;

-------------------Function to call when a book is returned
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE returnable(
        IN borrowid INT,
        IN id INT,
        IN bookISBN VARCHAR(50),
        IN schoolid INT
    )   
        READS SQL DATA
        COMMENT 'Borrow check'
    BEGIN
        UPDATE user 
        SET books_borrowed = books_borrowed - 1
        WHERE user_id = id;

        UPDATE borrowing 
        SET borrowing_status = 'Completed' 
        WHERE borrowing_id = borrowid;

        UPDATE book 
        SET available = available + 1
        WHERE book.ISBN = bookISBN AND book.school_id = schoolid;
    END;
//
DELIMITER ;

------------------------Check to see if the reservation can be approved and do the corresponding actions
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE reservation_approve(
        IN userId INT,
        IN bookISBN VARCHAR(50),
        IN job NVARCHAR(50),
        IN schoolid INT,
        IN reserveId INT,
        OUT checked INT,
        OUT availing INT
    )
        READS SQL DATA
        COMMENT 'Reserve Check'
    BEGIN 
        SET @flag = 1; 
        
        SELECT COUNT(reservation_id)
        INTO @books_reserved
        FROM reservation 
        WHERE (user_id = userId AND reservation_id = reserveId AND reservation_status = 'Approved')
        GROUP BY user_id; 

        SELECT borrowing_id
        INTO @books_overdue
        FROM borrowing
        WHERE (borrowing_status = 'Approved' AND 
               DATEDIFF(CURRENT_TIMESTAMP, CAST(borrowing_date AS DATETIME)) > 6 AND
               user_id = userId)
        LIMIT 1;
        SELECT FOUND_ROWS() INTO @books_overdue;

        SELECT borrowing_id
        INTO @borrowed_samebook
        FROM borrowing
        WHERE (ISBN = bookISBN AND
              (borrowing_status = 'Approved' OR borrowing_status = 'Waiting') AND
              user_id = userId AND
              schoolid = (SELECT school_admin.school_id FROM school_admin WHERE scadmin_id = borrowing.scadmin_id)
              )
        LIMIT 1;
        SELECT FOUND_ROWS() INTO @borrowed_samebook;

        SELECT reservation_id
        INTO @reserved_samebook
        FROM reservation
        WHERE (ISBN = bookISBN AND
               (reservation_status = 'Waiting' OR reservation_status = 'Approved') AND 
               user_id = userId AND 
               schoolid = (SELECT school_admin.school_id FROM school_admin WHERE scadmin_id = reservation.scadmin_id) AND
               reservation_id != reserveId)
        LIMIT 1;
        SELECT FOUND_ROWS() INTO @reserved_samebook;

        IF job = 'Student' THEN 
            IF (@books_reserved = 2) THEN
                SET @flag = 0;
            END IF;
        ELSEIF job = 'Teacher' THEN 
            IF (@books_reserved = 1) THEN 
                SET @flag = 0; 
            END IF; 
        END IF; 

        IF (@books_overdue > 0 OR @borrowed_samebook > 0 OR @reserved_samebook > 0) THEN 
            SET @flag = 0; 
        END IF; 
        SELECT @flag AS checked;

        IF (@flag = 0) THEN 
            DELETE FROM reservation
            WHERE reservation_id = reserveId;
        ELSEIF (@flag = 1) THEN 
            SELECT available INTO @avail
            FROM book
            WHERE ISBN = bookISBN AND school_id = schoolid;
            IF (@avail = 0) THEN 
                UPDATE reservation
                SET reservation_status = 'Waiting Queue'
                WHERE reservation_id = reserveId;
            ELSEIF (@avail > 0) THEN 
                SELECT scadmin_id INTO @schooladmin
                FROM reservation
                WHERE reservation_id = reserveId;

                UPDATE reservation
                SET reservation_status = 'Approved'
                WHERE reservation_id = reserveId;
            END IF;
        END IF; 
        SELECT @avail AS availing;
    END;
//
DELIMITER ;
---------------------------------------USER BOOKLIST, , question_3_3_1--------------------------------
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
        SELECT book.ISBN, book.book_title, author.first_name, author.last_name, book.publisher, book.no_pages, book.available, book.sprache, book.img
        FROM book
        INNER JOIN author ON book.ISBN = author.ISBN
        WHERE ((which_title = '' OR book.book_title LIKE CONCAT('%', which_title, '%')) AND
                (which_author_name = '' OR
                (author.first_name LIKE CONCAT('%', which_author_name, '%')) OR
                (author.last_name LIKE CONCAT('%', which_author_name, '%')) OR
                (CONCAT(author.first_name, ' ', author.last_name) LIKE CONCAT('%', which_author_name, '%'))) AND
                (which_category = '' OR
                EXISTS (SELECT * FROM category WHERE (category.ISBN = book.ISBN AND category.category = which_category))) AND
                (book.school_id = schoolid))
        GROUP BY book.ISBN
        ORDER BY book.book_title;
    END;

//
DELIMITER ;

---------------------------------------SCADMIN_BOOKLIST, question_3_2_1--------------------------------
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
        GROUP BY book.ISBN
        ORDER BY book.book_title;
    END;
//
DELIMITER ;

-------------------------------------BOOK DETAILS----------------------------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE details(
        IN ISBN VARCHAR(50),
        IN school_id INT
    )
        READS SQL DATA
        COMMENT 'Details'
    BEGIN 
        SELECT book.book_title, author.first_name, author.last_name, book.publisher, book.summary, book.no_pages, category.category, keywords.keyword, book.sprache, book.ISBN, book.img
        FROM book 
        INNER JOIN author ON author.ISBN = book.ISBN
        INNER JOIN category ON category.ISBN = book.ISBN 
        INNER JOIN keywords ON keywords.ISBN = book.ISBN 
        WHERE ( (book.ISBN = ISBN) AND (book.school_id = school_id) )
        GROUP BY book.ISBN;
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
        SELECT first_name, last_name, job, birth_date, books_borrowed, user_status, user_id
        FROM user 
        WHERE ( (which_user = '' OR
                (user.first_name LIKE CONCAT('%', which_user, '%')) OR
                (user.last_name LIKE CONCAT('%', which_user, '%')) OR
                (CONCAT(user.first_name, ' ', user.last_name) LIKE CONCAT('%', which_user, '%'))) AND
                (user.school_id = schoolid) AND 
                (user.user_status = user_status))
        ORDER BY user.last_name, user.first_name;
    END;
//
DELIMITER ;

