-- ===============================================
-- ADDITIONAL PERMISSIONS FOR POTPLAG USER
-- Run this in MySQL Workbench to fix the REFERENCES error
-- ===============================================

-- Grant the REFERENCES privilege (needed for foreign keys)
GRANT REFERENCES ON potplag.* TO 'potplag'@'localhost';

-- Also grant TRIGGER privilege (sometimes needed)
GRANT TRIGGER ON potplag.* TO 'potplag'@'localhost';

-- Apply the changes
FLUSH PRIVILEGES;

-- Verify the updated grants
SHOW GRANTS FOR 'potplag'@'localhost';

-- ===============================================
-- ALTERNATIVE: Complete privilege set (if needed)
-- ===============================================

-- If you want to grant all common privileges at once:
-- GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES, TRIGGER 
-- ON potplag.* TO 'potplag'@'localhost';

-- FLUSH PRIVILEGES;
