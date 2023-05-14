------------------------------------------------3.1------------------------------------------------------
---------------------------3_1_1-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_1(
        IN which_year YEAR,
        IN which_month MEDIUMINT,
        OUT out_question_3_1_1 INT
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.1'
    proc: BEGIN
        SELECT COUNT(borrowing.borrowing_id) AS total_borrowings, school.school_name 
        INTO out_question_3_1_1
        FROM 
        (SELECT A.borrowing_id, school.school_name 
            FROM 
            (SELECT book.school_id, borrowing.borrowing_id
                FROM book 
                INNER JOIN borrowing ON book.ISBN = borrowing.ISBN
                WHERE ((which_year = 0 OR YEAR(borrowing.borrowing_date) = which_year)
                        AND (which_month = 0 OR MONTH(borrowing.borrowing_date) = which_month))) AS A 
            INNER JOIN school ON school.school_id = A.school_id)
        GROUP BY school.school_name
        ORDER BY school.school_name DESC; 
    END;//
DELIMITER;
---------------------------3_1_2_1-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_2_1(
        IN which_category VARCHAR(50),
        OUT question_3_1_2_1
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.2.1'
    proc: BEGIN
        SELECT DISTINCT author.first_name, author.last_name 
        INTO question_3_1_2_1
        FROM author 
        WHERE EXISTS (SELECT * FROM category 
                    WHERE (author.ISBN = category.ISBN AND category.category = which_category))
        ORDER BY author.first_name DESC;
    END;//
DELIMITER;
---------------------------3_1_2_2-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_2_2(
        IN which_category VARCHAR(50),
        OUT question_3_1_2_1
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.2.2'
    proc: BEGIN
        SELECT DISTINCT user.first_name, user.last_name 
        INTO question_3_1_2_1
        FROM user 
            INNER JOIN borrowing ON user.user_id = borrowing.borrowing_id
            WHERE (user.job = 'Teacher' AND DATEDIFF(NOW(), CAST(borrowing.borrowing_date AS DATETIME)) < 365)
            AND EXISTS (SELECT * FROM category 
                    WHERE (borrowing.ISBN = category.ISBN AND category.category = which_category))
        ORDER BY user.first_name DESC;
    END;//
DELIMITER;
---------------------------3_1_3-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_3(
        OUT question_3_1_3
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.3'
    proc: BEGIN
        SELECT COUNT(borrowing_id) AS total_borrowings, user.first_name, user.last_name
        INTO question_3_1_3 
        FROM 
        (SELECT user.first_name, user.last_name, borrowing_id
            FROM user 
            INNER JOIN borrowing ON user.user_id = borrowing.user_id 
            WHERE (user.job = 'Teacher' AND DATEDIFF(NOW(), CAST(user.birth_date AS DATETIME)) < 14600)) 
        GROUP BY user.first_name, user.last_name
        ORDER BY COUNT(borrowing_id) DESC;
    END;//
DELIMITER;
---------------------------3_1_4-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_4()
        READS SQL DATA
        COMMENT 'Exercise 3.1.4'
    BEGIN
        SELECT author.first_name, author.last_name
        FROM author 
        LEFT JOIN borrowing ON author.ISBN = borrowing.ISBN 
        WHERE borrowing.ISBN IS NULL
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
        WHERE (which_year = 0 OR YEAR(borrowing.borrowing_date) = which_year)
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
        SELECT COUNT(A.ISBN) AS best_3, A.category1 AS first_cat, A.category2 AS second_cat
        FROM
        (SELECT category1.category AS category1, category2.category AS category2, category1.ISBN 
            FROM category category1
            INNER JOIN category category2 ON category1.category < category2.category
            WHERE EXISTS(SELECT * FROM borrowing 
                    WHERE (borrowing.ISBN = category1.ISBN AND borrowing.ISBN = category2.ISBN))) AS A
        GROUP BY A.category1, A.category2
        ORDER BY COUNT(A.ISBN) DESC LIMIT 3;
END;
//
DELIMITER ;

---------------------------3_1_7-------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_1_7(
    )
        READS SQL DATA
        COMMENT 'Exercise 3.1.7'
    proc: BEGIN
        SELECT author.first_name, author.last_name
        FROM 
        (SELECT COUNT(ISBN), author.first_name, author.last_name 
            FROM author
            GROUP BY author.first_name, author.last_name) AS A 
        WHERE ((MAX(COUNT(ISBN)) FROM A)-COUNT(ISBN) >= 5); 
    END;
//
DELIMITER ;
------------------------------------------------3.2------------------------------------------------------
------------------------------------------------3.2.1------------------------------------------------------
DELIMITER //
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_2_1(
        IN which_title VARCHAR(50),
        IN which_author_firstname VARCHAR(50),
        IN which_author_lastname VARCHAR(50),
        IN which_category VARCHAR(50),
        IN which_availabiliity INT
    )
        READS SQL DATA
        COMMENT 'Exercise 3.2.1'
    BEGIN
        SELECT author.first_name, author.last_name, book.book_title
        FROM book 
        INNER JOIN author ON book.ISBN = author.ISBN
        WHERE ((which_title = '' OR book.book_title = which_title) AND 
                ((which_author_firstname = '' AND which_author_lastname = '') OR 
                 (author.first_name = which_author_firstname AND author.last_name = which_author_lastname)) AND
                 (which_availabiliity = -1 OR book.available = which_availabiliity) AND
                 (which_category = '' OR 
                  EXISTS(SELECT * FROM category WHERE (category.ISBN = book.ISBN AND category.category = which_category))))
        ORDER BY author.first_name;
    END;
//
DELIMITER ;

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
    CREATE DEFINER='root'@'localhost' PROCEDURE question_3_2_3(
        IN which_user_firstname VARCHAR(50),
        IN which_user_lastname VARCHAR(50),
        IN delayed INT,
        OUT question_3_2_3,
    )
        READS SQL DATA
        COMMENT 'Exercise 3.2.3'
    proc: BEGIN
        --The fuck is this
    END;//
DELIMITER;
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
        FROM 
        (SELECT borrowing.ISBN
         FROM borrowing 
         WHERE borrowing.user_id = which_user) AS A 
         LEFT JOIN book ON A.ISBN = book.ISBN
         ORDER BY book.book_title;
    END;
//
DELIMITER;

------------------------Extras that occured while builidng the app--------------------------