-- Sample data for trying out the API and the example queries.
-- Run after `alembic upgrade head`, e.g.:
--   mysql -u app -p library < sql/sample_data.sql

INSERT INTO books (title, author, isbn, published_year, total_copies, available_copies) VALUES
    ('Clean Code',                  'Robert C. Martin', '9780132350884', 2008, 3, 2),
    ('Learning SQL',                'Alan Beaulieu',    '9781492057611', 2020, 2, 0),
    ('Python Crash Course',         'Eric Matthes',     '9781718502703', 2023, 2, 1),
    ('The Pragmatic Programmer',    'David Thomas',     '9780135957059', 2019, 1, 1),
    ('Designing Data-Intensive Applications', 'Martin Kleppmann', '9781449373320', 2017, 1, 1);

INSERT INTO members (name, email) VALUES
    ('Ada Lovelace',   'ada@example.com'),
    ('Alan Turing',    'alan@example.com'),
    ('Grace Hopper',   'grace@example.com'),
    ('Linus Torvalds', 'linus@example.com');

-- Dates are relative to today so the overdue report always has something to show.
INSERT INTO loans (book_id, member_id, borrowed_at, due_date, returned_at) VALUES
    -- returned on time
    (1, 1, NOW() - INTERVAL 40 DAY, CURDATE() - INTERVAL 26 DAY, NOW() - INTERVAL 30 DAY),
    (2, 1, NOW() - INTERVAL 35 DAY, CURDATE() - INTERVAL 21 DAY, NOW() - INTERVAL 25 DAY),
    (5, 3, NOW() - INTERVAL 30 DAY, CURDATE() - INTERVAL 16 DAY, NOW() - INTERVAL 20 DAY),
    -- still borrowed, not due yet
    (1, 2, NOW() - INTERVAL 3 DAY,  CURDATE() + INTERVAL 11 DAY, NULL),
    (2, 3, NOW() - INTERVAL 5 DAY,  CURDATE() + INTERVAL 9 DAY,  NULL),
    -- still borrowed and overdue
    (2, 4, NOW() - INTERVAL 20 DAY, CURDATE() - INTERVAL 6 DAY,  NULL),
    (3, 1, NOW() - INTERVAL 18 DAY, CURDATE() - INTERVAL 4 DAY,  NULL);
