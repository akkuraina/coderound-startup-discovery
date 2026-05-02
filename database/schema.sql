CREATE DATABASE IF NOT EXISTS coderound_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE coderound_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP NULL,
  INDEX idx_email (email),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  website VARCHAR(500),
  linkedin_url VARCHAR(500),
  funding_amount FLOAT,
  funding_date TIMESTAMP NULL,
  funding_round VARCHAR(50),
  investors LONGTEXT,
  sector VARCHAR(100),
  country VARCHAR(100),
  description LONGTEXT,
  hiring_status INT DEFAULT 0,
  hiring_positions LONGTEXT,
  enriched_data JSON,
  decision_makers JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_enriched TIMESTAMP NULL,
  discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_name (name),
  INDEX idx_funding_date (funding_date),
  INDEX idx_hiring_status (hiring_status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Outreach table
CREATE TABLE IF NOT EXISTS outreach (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  company_id INT NOT NULL,
  email_sent_to VARCHAR(255) NOT NULL,
  email_subject VARCHAR(255) NOT NULL,
  email_content LONGTEXT NOT NULL,
  response_status INT DEFAULT 0,
  response_received_at TIMESTAMP NULL,
  response_notes LONGTEXT,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_company_id (company_id),
  INDEX idx_response_status (response_status),
  INDEX idx_sent_at (sent_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_funding_date ON companies(funding_date);
CREATE INDEX idx_outreach_user_company ON outreach(user_id, company_id);

