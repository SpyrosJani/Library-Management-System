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
        WHERE EXISTS (SELECT * FROM category 
                    WHERE (author.ISBN = category.ISBN AND category.category = which_category))
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
        WHERE (user.job = 'Teacher' AND DATEDIFF(NOW(), CAST(borrowing.borrowing_date AS DATETIME)) < 365 AND 
              (borrowing.borrowing_status = 'Approved' OR borrowing.borrowing_status = 'Completed') 
              AND EXISTS (SELECT * FROM category 
              WHERE (borrowing.ISBN = category.ISBN AND category.category = which_category)))
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
        SELECT COUNT(A.ISBN) AS best_3, A.category1 AS first_cat, A.category2 AS second_cat
        FROM category1.category AS category1
        INNER JOIN category AS category2 ON category1.category < category2.category
        INNER JOIN borrowing ON (borrowing.ISBN = category1.ISBN AND borrowing.ISBN = category2.ISBN)
        GROUP BY category1, category2
        ORDER BY COUNT(A.ISBN) DESC LIMIT 3;   
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