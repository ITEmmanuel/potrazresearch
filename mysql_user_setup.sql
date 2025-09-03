-- ===============================================
-- POTPLAG MySQL User Setup Commands
-- Run these commands in MySQL Workbench as root user
-- ===============================================

-- 1. Create the potplag application user
-- You can change the password to something more secure if needed
CREATE USER 'potplag'@'localhost' IDENTIFIED BY 'potplag_secure_password_123';

-- Optional: If you need to connect from other hosts, also create:
-- CREATE USER 'potplag'@'%' IDENTIFIED BY 'potplag_secure_password_123';

-- 2. Grant all necessary permissions on the potplag database
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX 
ON potplag.* TO 'potplag'@'localhost';

-- If you created the user for all hosts, also grant permissions:
-- GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX 
-- ON potplag.* TO 'potplag'@'%';

-- 3. Apply the permission changes
FLUSH PRIVILEGES;

-- 4. Verify the user was created successfully
SELECT User, Host FROM mysql.user WHERE User = 'potplag';

-- 5. Show the grants for the potplag user
SHOW GRANTS FOR 'potplag'@'localhost';

-- ===============================================
-- VERIFICATION COMMANDS
-- ===============================================

-- Test the database exists
SHOW DATABASES LIKE 'potplag';

-- Test connection (you can run this to verify everything works)
-- SELECT 'User potplag can connect successfully!' AS status;
