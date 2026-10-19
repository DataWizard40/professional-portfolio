-- Example MySQL queries against the library database.
-- Load sql/sample_data.sql first, then run these in the MySQL shell or a GUI.


-- 1. Books with at least one copy on the shelf
SELECT title, author, available_copies
FROM books
WHERE available_copies > 0
ORDER BY title;


-- 2. Everything a member currently has borrowed (JOIN)
SELECT m.name, b.title, l.borrowed_at, l.due_date
FROM loans l
JOIN books b   ON b.id = l.book_id
JOIN members m ON m.id = l.member_id
WHERE m.email = 'ada@example.com'
  AND l.returned_at IS NULL;


-- 3. Overdue loans and how many days late they are
--    (the same logic as GET /reports/overdue)
SELECT b.title,
       m.name,
       m.email,
       l.due_date,
       DATEDIFF(CURDATE(), l.due_date) AS days_overdue
FROM loans l
JOIN books b   ON b.id = l.book_id
JOIN members m ON m.id = l.member_id
WHERE l.returned_at IS NULL
  AND l.due_date < CURDATE()
ORDER BY days_overdue DESC;


-- 4. Most borrowed books (GROUP BY + COUNT)
--    (the same logic as GET /reports/popular-books)
SELECT b.title, b.author, COUNT(l.id) AS times_borrowed
FROM books b
JOIN loans l ON l.book_id = b.id
GROUP BY b.id, b.title, b.author
ORDER BY times_borrowed DESC, b.title
LIMIT 5;


-- 5. Members who have borrowed more than one book in total (HAVING)
SELECT m.name, COUNT(*) AS total_loans
FROM members m
JOIN loans l ON l.member_id = m.id
GROUP BY m.id, m.name
HAVING COUNT(*) > 1
ORDER BY total_loans DESC;


-- 6. Books that have never been borrowed (LEFT JOIN ... IS NULL)
SELECT b.title, b.author
FROM books b
LEFT JOIN loans l ON l.book_id = b.id
WHERE l.id IS NULL;


-- 7. Check the copy counts are consistent: available copies should equal
--    total copies minus the copies currently on loan. Returns no rows if all is well.
SELECT b.title,
       b.total_copies,
       b.available_copies,
       COUNT(l.id) AS on_loan
FROM books b
LEFT JOIN loans l ON l.book_id = b.id AND l.returned_at IS NULL
GROUP BY b.id, b.title, b.total_copies, b.available_copies
HAVING b.available_copies <> b.total_copies - COUNT(l.id);
