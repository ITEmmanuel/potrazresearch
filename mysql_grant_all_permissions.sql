-- ===============================================
-- GRANT ALL PRIVILEGES TO POTPLAG USER
-- Run this in MySQL Workbench as root user
-- ===============================================

-- Grant ALL privileges on the potplag database to potplag user
GRANT ALL PRIVILEGES ON potplag.* TO 'potplag'@'localhost';

-- Apply the changes immediately
FLUSH PRIVILEGES;

-- Verify the grants (should show ALL PRIVILEGES)
SHOW GRANTS FOR 'potplag'@'localhost';

-- Expected output should be something like:
-- GRANT ALL PRIVILEGES ON `potplag`.* TO `potplag`@`localhost`
