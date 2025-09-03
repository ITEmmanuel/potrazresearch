-- POTPLAG MySQL Database Setup Script
-- Run this script as MySQL root user

-- ===============================================
-- 1. CREATE DATABASE
-- ===============================================

-- Create the main database with proper character set for international support
CREATE DATABASE potplag 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Optional: Create separate database for testing
CREATE DATABASE potplag_test 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- ===============================================
-- 2. CREATE APPLICATION USER
-- ===============================================

-- Create user that can connect from localhost only (more secure)
CREATE USER 'potplag'@'localhost' IDENTIFIED BY 'your_secure_password_here';

-- If you need to connect from remote hosts, create additional user:
-- CREATE USER 'potplag'@'%' IDENTIFIED BY 'your_secure_password_here';

-- For Docker or containerized deployments, you might need:
-- CREATE USER 'potplag'@'172.%' IDENTIFIED BY 'your_secure_password_here';

-- ===============================================
-- 3. GRANT PERMISSIONS
-- ===============================================

-- Grant all necessary permissions on the main database
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX 
ON potplag.* TO 'potplag'@'localhost';

-- Grant permissions on test database (if created)
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX 
ON potplag_test.* TO 'potplag'@'localhost';

-- If using remote connection, grant permissions for remote user too:
-- GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX 
-- ON potplag.* TO 'potplag'@'%';

-- ===============================================
-- 4. APPLY CHANGES
-- ===============================================

-- Reload the grant tables to apply changes
FLUSH PRIVILEGES;

-- ===============================================
-- 5. VERIFY SETUP
-- ===============================================

-- Show created databases
SHOW DATABASES LIKE 'potplag%';

-- Show created users
SELECT User, Host FROM mysql.user WHERE User = 'potplag';

-- Show grants for the user
SHOW GRANTS FOR 'potplag'@'localhost';
