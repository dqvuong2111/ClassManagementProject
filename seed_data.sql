-- ============================================
-- Reset and Seed Data Script for ClassManagementWebsite
-- Database: MS SQL Server
-- Schema: 15-Table Design (Admin, Teacher, Student separated)
-- ============================================

USE ClassManagementWebsite;
GO

-- ============================================
-- PART 1: RESET - Delete all existing data
-- ============================================

PRINT 'Resetting database...';

-- Disable foreign key checks temporarily
EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';

-- Delete all data
DELETE FROM core_contentreadstatus;
DELETE FROM core_attendance;
DELETE FROM core_attendancesession;
DELETE FROM core_assignmentsubmission;
DELETE FROM core_assignment;
DELETE FROM core_announcement;
DELETE FROM core_material;
DELETE FROM core_message;
DELETE FROM core_feedback;
DELETE FROM core_enrollment;
DELETE FROM core_clazz;
DELETE FROM core_classtype;
DELETE FROM core_admin;
DELETE FROM core_teacher;
DELETE FROM core_student;
DELETE FROM auth_user WHERE is_superuser = 0;

-- Re-enable foreign key checks
EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL';

PRINT 'Database reset complete.';
GO

-- ============================================
-- PART 2: SEED DATA
-- ============================================

PRINT 'Seeding data...';

-- --------------------------------------------
-- 2.1: auth_user (50 users for testing)
-- --------------------------------------------
PRINT 'Creating auth_user records...';

DECLARE @password NVARCHAR(128) = 'pbkdf2_sha256$720000$test$hashedpassword123';

-- Teachers (10)
DECLARE @i INT = 1;
WHILE @i <= 10
BEGIN
    INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
    VALUES (@password, NULL, 0, 'teacher' + CAST(@i AS NVARCHAR(10)), 'Teacher', CAST(@i AS NVARCHAR(10)), 'teacher' + CAST(@i AS NVARCHAR(10)) + '@edu.com', 0, 1, GETDATE());
    SET @i = @i + 1;
END;

-- Students (35)
SET @i = 1;
WHILE @i <= 35
BEGIN
    INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
    VALUES (@password, NULL, 0, 'student' + CAST(@i AS NVARCHAR(10)), 'Student', CAST(@i AS NVARCHAR(10)), 'student' + CAST(@i AS NVARCHAR(10)) + '@edu.com', 0, 1, GETDATE());
    SET @i = @i + 1;
END;

-- Admin (5)
SET @i = 1;
WHILE @i <= 5
BEGIN
    INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
    VALUES (@password, NULL, 0, 'admin' + CAST(@i AS NVARCHAR(10)), 'Admin', CAST(@i AS NVARCHAR(10)), 'admin' + CAST(@i AS NVARCHAR(10)) + '@edu.com', 0, 1, GETDATE());
    SET @i = @i + 1;
END;

PRINT 'Created 50 auth_user records.';
GO

-- --------------------------------------------
-- 2.2: core_teacher (10 teachers)
-- --------------------------------------------
PRINT 'Creating core_teacher records...';

DECLARE @i INT = 1;
DECLARE @user_id INT;

WHILE @i <= 10
BEGIN
    SELECT @user_id = id FROM auth_user WHERE username = 'teacher' + CAST(@i AS NVARCHAR(10));
    
    INSERT INTO core_teacher (user_id, full_name, dob, phone_number, email, address, qualification, created_at, updated_at)
    VALUES (
        @user_id,
        'Teacher ' + CAST(@i AS NVARCHAR(10)),
        DATEADD(YEAR, -30 - (@i % 15), GETDATE()),
        '090000000' + CAST(@i AS NVARCHAR(10)),
        'teacher' + CAST(@i AS NVARCHAR(10)) + '@edu.com',
        'Address ' + CAST(@i AS NVARCHAR(10)) + ', District ' + CAST((@i % 12) + 1 AS NVARCHAR(2)),
        CASE (@i % 3) WHEN 0 THEN 'PhD in Computer Science' WHEN 1 THEN 'Master in Mathematics' ELSE 'Bachelor in Physics' END,
        GETDATE(), GETDATE()
    );
    SET @i = @i + 1;
END;

PRINT 'Created 10 core_teacher records.';
GO

-- --------------------------------------------
-- 2.3: core_student (35 students)
-- --------------------------------------------
PRINT 'Creating core_student records...';

DECLARE @i INT = 1;
DECLARE @user_id INT;

WHILE @i <= 35
BEGIN
    SELECT @user_id = id FROM auth_user WHERE username = 'student' + CAST(@i AS NVARCHAR(10));
    
    INSERT INTO core_student (user_id, full_name, dob, phone_number, email, address, created_at, updated_at)
    VALUES (
        @user_id,
        'Student ' + CAST(@i AS NVARCHAR(10)),
        DATEADD(YEAR, -18 - (@i % 8), GETDATE()),
        '080000000' + RIGHT('00' + CAST(@i AS NVARCHAR(10)), 2),
        'student' + CAST(@i AS NVARCHAR(10)) + '@edu.com',
        'Address ' + CAST(@i AS NVARCHAR(10)) + ', District ' + CAST((@i % 12) + 1 AS NVARCHAR(2)),
        GETDATE(), GETDATE()
    );
    SET @i = @i + 1;
END;

PRINT 'Created 35 core_student records.';
GO

-- --------------------------------------------
-- 2.4: core_admin (5 admin)
-- --------------------------------------------
PRINT 'Creating core_admin records...';

DECLARE @i INT = 1;
DECLARE @user_id INT;

WHILE @i <= 5
BEGIN
    SELECT @user_id = id FROM auth_user WHERE username = 'admin' + CAST(@i AS NVARCHAR(10));
    
    INSERT INTO core_admin (user_id, full_name, dob, phone_number, email, address, position, created_at, updated_at)
    VALUES (
        @user_id,
        'Admin ' + CAST(@i AS NVARCHAR(10)),
        DATEADD(YEAR, -25 - (@i % 10), GETDATE()),
        '070000000' + CAST(@i AS NVARCHAR(10)),
        'admin' + CAST(@i AS NVARCHAR(10)) + '@edu.com',
        'Address ' + CAST(@i AS NVARCHAR(10)) + ', District ' + CAST((@i % 12) + 1 AS NVARCHAR(2)),
        CASE (@i % 3) WHEN 0 THEN 'Administrative Assistant' WHEN 1 THEN 'Registrar' ELSE 'IT Support' END,
        GETDATE(), GETDATE()
    );
    SET @i = @i + 1;
END;

PRINT 'Created 5 core_admin records.';
GO

-- --------------------------------------------
-- 2.5: core_classtype (10 class types)
-- --------------------------------------------
PRINT 'Creating core_classtype records...';

INSERT INTO core_classtype (code, description, created_at, updated_at) VALUES
('MATH', 'Mathematics Classes', GETDATE(), GETDATE()),
('ENG', 'English Language Classes', GETDATE(), GETDATE()),
('SCI', 'Science Classes', GETDATE(), GETDATE()),
('PROG', 'Programming Classes', GETDATE(), GETDATE()),
('ART', 'Art and Design Classes', GETDATE(), GETDATE()),
('MUSIC', 'Music Classes', GETDATE(), GETDATE()),
('PHYS', 'Physical Education', GETDATE(), GETDATE()),
('HIST', 'History Classes', GETDATE(), GETDATE()),
('CHEM', 'Chemistry Classes', GETDATE(), GETDATE()),
('BIO', 'Biology Classes', GETDATE(), GETDATE());

PRINT 'Created 10 core_classtype records.';
GO

-- --------------------------------------------
-- 2.6: core_clazz (20 classes)
-- --------------------------------------------
PRINT 'Creating core_clazz records...';

DECLARE @i INT = 1;
DECLARE @teacher_id INT;
DECLARE @admin_id INT;
DECLARE @class_type_id INT;

-- Get min IDs
DECLARE @min_teacher_id INT, @min_admin_id INT, @min_classtype_id INT;
SELECT @min_teacher_id = MIN(teacher_id) FROM core_teacher;
SELECT @min_admin_id = MIN(admin_id) FROM core_admin;
SELECT @min_classtype_id = MIN(type_id) FROM core_classtype;

WHILE @i <= 20
BEGIN
    SET @teacher_id = @min_teacher_id + ((@i - 1) % 10);
    SET @admin_id = @min_admin_id + ((@i - 1) % 5);
    SET @class_type_id = @min_classtype_id + ((@i - 1) % 10);
    
    INSERT INTO core_clazz (class_name, class_type_id, teacher_id, staff_id, start_date, end_date, price, room, image, day_of_week, start_time, end_time, created_at, updated_at)
    VALUES (
        'Class ' + CAST(@i AS NVARCHAR(10)),
        @class_type_id,
        @teacher_id,
        @admin_id,
        DATEADD(DAY, -30, GETDATE()),
        DATEADD(DAY, 90, GETDATE()),
        150000 + (@i * 10000),
        'Room ' + CAST(((@i % 10) + 1) AS NVARCHAR(3)),
        'class_images/default_class.png',
        CASE (@i % 3) WHEN 0 THEN 'Monday, Wednesday, Friday' WHEN 1 THEN 'Tuesday, Thursday' ELSE 'Saturday, Sunday' END,
        '08:00:00',
        '10:00:00',
        GETDATE(), GETDATE()
    );
    SET @i = @i + 1;
END;

PRINT 'Created 20 core_clazz records.';
GO

-- --------------------------------------------
-- 2.7: core_enrollment (50 enrollments)
-- --------------------------------------------
PRINT 'Creating core_enrollment records...';

DECLARE @i INT = 1;
DECLARE @student_id INT;
DECLARE @clazz_id INT;

DECLARE @min_student_id INT, @min_clazz_id INT;
SELECT @min_student_id = MIN(student_id) FROM core_student;
SELECT @min_clazz_id = MIN(class_id) FROM core_clazz;

WHILE @i <= 50
BEGIN
    SET @student_id = @min_student_id + ((@i - 1) % 35);
    SET @clazz_id = @min_clazz_id + ((@i - 1) % 20);
    
    INSERT INTO core_enrollment (student_id, clazz_id, enrollment_date, status, is_paid, minitest1, minitest2, minitest3, minitest4, midterm, final_test, created_at, updated_at)
    VALUES (
        @student_id,
        @clazz_id,
        DATEADD(DAY, -(@i % 20), GETDATE()),
        CASE WHEN @i % 5 = 0 THEN 'pending' ELSE 'approved' END,
        CASE WHEN @i % 3 = 0 THEN 0 ELSE 1 END,
        CAST(5.0 + (@i % 5) AS DECIMAL(4,2)),
        CAST(6.0 + (@i % 4) AS DECIMAL(4,2)),
        CAST(7.0 + (@i % 3) AS DECIMAL(4,2)),
        CAST(6.5 AS DECIMAL(4,2)),
        CAST(7.5 AS DECIMAL(4,2)),
        CAST(8.0 AS DECIMAL(4,2)),
        GETDATE(), GETDATE()
    );
    SET @i = @i + 1;
END;

PRINT 'Created 50 core_enrollment records.';
GO

-- --------------------------------------------
-- 2.8: core_material (20 materials)
-- --------------------------------------------
PRINT 'Creating core_material records...';

DECLARE @i INT = 1;
DECLARE @clazz_id INT;
DECLARE @min_clazz_id INT;
SELECT @min_clazz_id = MIN(class_id) FROM core_clazz;

WHILE @i <= 20
BEGIN
    SET @clazz_id = @min_clazz_id + ((@i - 1) % 20);
    
    INSERT INTO core_material (title, [file], clazz_id, uploaded_at)
    VALUES ('Lecture Notes Week ' + CAST(@i AS NVARCHAR(10)), 'materials/lecture_' + CAST(@i AS NVARCHAR(10)) + '.pdf', @clazz_id, GETDATE());
    SET @i = @i + 1;
END;

PRINT 'Created 20 core_material records.';
GO

-- --------------------------------------------
-- 2.9: core_announcement (20 announcements)
-- --------------------------------------------
PRINT 'Creating core_announcement records...';

DECLARE @i INT = 1;
DECLARE @clazz_id INT;
DECLARE @min_clazz_id INT;
SELECT @min_clazz_id = MIN(class_id) FROM core_clazz;

WHILE @i <= 20
BEGIN
    SET @clazz_id = @min_clazz_id + ((@i - 1) % 20);
    
    INSERT INTO core_announcement (title, content, clazz_id, posted_at)
    VALUES ('Announcement ' + CAST(@i AS NVARCHAR(10)), 'This is announcement content number ' + CAST(@i AS NVARCHAR(10)), @clazz_id, GETDATE());
    SET @i = @i + 1;
END;

PRINT 'Created 20 core_announcement records.';
GO

-- --------------------------------------------
-- 2.10: core_assignment (20 assignments)
-- --------------------------------------------
PRINT 'Creating core_assignment records...';

DECLARE @i INT = 1;
DECLARE @clazz_id INT;
DECLARE @min_clazz_id INT;
SELECT @min_clazz_id = MIN(class_id) FROM core_clazz;

WHILE @i <= 20
BEGIN
    SET @clazz_id = @min_clazz_id + ((@i - 1) % 20);
    
    INSERT INTO core_assignment (title, description, due_date, clazz_id, created_at)
    VALUES ('Assignment ' + CAST(@i AS NVARCHAR(10)), 'Complete tasks for assignment ' + CAST(@i AS NVARCHAR(10)), DATEADD(DAY, @i, GETDATE()), @clazz_id, GETDATE());
    SET @i = @i + 1;
END;

PRINT 'Created 20 core_assignment records.';
GO

-- --------------------------------------------
-- 2.11: core_assignmentsubmission (30 submissions)
-- --------------------------------------------
PRINT 'Creating core_assignmentsubmission records...';

DECLARE @i INT = 1;
DECLARE @student_id INT;
DECLARE @assignment_id INT;

DECLARE @min_student_id INT, @min_assignment_id INT;
SELECT @min_student_id = MIN(student_id) FROM core_student;
SELECT @min_assignment_id = MIN(id) FROM core_assignment;

WHILE @i <= 30
BEGIN
    SET @student_id = @min_student_id + ((@i - 1) % 35);
    SET @assignment_id = @min_assignment_id + ((@i - 1) % 20);
    
    INSERT INTO core_assignmentsubmission (assignment_id, student_id, submission_file, submitted_at, grade, feedback)
    VALUES (
        @assignment_id,
        @student_id,
        'submissions/sub_' + CAST(@i AS NVARCHAR(10)) + '.pdf',
        GETDATE(),
        CAST(7.0 + (@i % 3) AS DECIMAL(4,2)),
        'Good work on submission ' + CAST(@i AS NVARCHAR(10))
    );
    SET @i = @i + 1;
END;

PRINT 'Created 30 core_assignmentsubmission records.';
GO

-- --------------------------------------------
-- 2.12: core_feedback (20 feedbacks)
-- --------------------------------------------
PRINT 'Creating core_feedback records...';

DECLARE @i INT = 1;
DECLARE @student_id INT;
DECLARE @clazz_id INT;

DECLARE @min_student_id INT, @min_clazz_id INT;
SELECT @min_student_id = MIN(student_id) FROM core_student;
SELECT @min_clazz_id = MIN(class_id) FROM core_clazz;

WHILE @i <= 20
BEGIN
    SET @student_id = @min_student_id + ((@i - 1) % 35);
    SET @clazz_id = @min_clazz_id + ((@i - 1) % 20);
    
    INSERT INTO core_feedback (student_id, clazz_id, teacher_rate, class_rate, comment, created_at, updated_at)
    VALUES (@student_id, @clazz_id, CAST((@i % 4) + 5 AS DECIMAL(3,2)), CAST((@i % 4) + 5 AS DECIMAL(3,2)), 'Great class experience!', GETDATE(), GETDATE());
    SET @i = @i + 1;
END;

PRINT 'Created 20 core_feedback records.';
GO

-- --------------------------------------------
-- 2.13: core_message (20 messages)
-- --------------------------------------------
PRINT 'Creating core_message records...';

DECLARE @i INT = 1;
DECLARE @sender_id INT;
DECLARE @recipient_id INT;

DECLARE @min_user_id INT;
SELECT @min_user_id = MIN(id) FROM auth_user WHERE is_superuser = 0;

WHILE @i <= 20
BEGIN
    SET @sender_id = @min_user_id + ((@i - 1) % 50);
    SET @recipient_id = @min_user_id + (((@i - 1) + 10) % 50);
    
    INSERT INTO core_message (sender_id, recipient_id, subject, body, is_read, created_at)
    VALUES (@sender_id, @recipient_id, 'Message ' + CAST(@i AS NVARCHAR(10)), 'This is message body ' + CAST(@i AS NVARCHAR(10)), 0, GETDATE());
    SET @i = @i + 1;
END;

PRINT 'Created 20 core_message records.';
GO

-- ============================================
-- PART 3: VERIFICATION
-- ============================================

PRINT '';
PRINT '============================================';
PRINT 'DATA SEEDING COMPLETE';
PRINT '============================================';

SELECT 'auth_user' AS [Table], COUNT(*) AS [Count] FROM auth_user WHERE is_superuser = 0
UNION ALL SELECT 'core_admin', COUNT(*) FROM core_admin
UNION ALL SELECT 'core_teacher', COUNT(*) FROM core_teacher
UNION ALL SELECT 'core_student', COUNT(*) FROM core_student
UNION ALL SELECT 'core_classtype', COUNT(*) FROM core_classtype
UNION ALL SELECT 'core_clazz', COUNT(*) FROM core_clazz
UNION ALL SELECT 'core_enrollment', COUNT(*) FROM core_enrollment
UNION ALL SELECT 'core_material', COUNT(*) FROM core_material
UNION ALL SELECT 'core_announcement', COUNT(*) FROM core_announcement
UNION ALL SELECT 'core_assignment', COUNT(*) FROM core_assignment
UNION ALL SELECT 'core_assignmentsubmission', COUNT(*) FROM core_assignmentsubmission
UNION ALL SELECT 'core_feedback', COUNT(*) FROM core_feedback
UNION ALL SELECT 'core_message', COUNT(*) FROM core_message
ORDER BY [Table];

PRINT '';
PRINT 'SEEDING COMPLETED SUCCESSFULLY!';
GO
