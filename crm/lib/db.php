<?php
/**
 * TKVibes CRM — Database bootstrap
 * PDO connection + schema auto-creation.
 */

function get_db(): PDO
{
    static $pdo = null;
    if ($pdo) return $pdo;

    $cfg = require __DIR__ . '/../config.local.php';
    $db = $cfg['db'];

    // Ensure data directory exists for SQLite
    if (str_starts_with($db['dsn'], 'sqlite:')) {
        $dbPath = substr($db['dsn'], 7); // strip 'sqlite:'
        $dir = dirname($dbPath);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
    }

    $pdo = new PDO($db['dsn'], $db['username'] ?? null, $db['password'] ?? null, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ]);

    // SQLite pragma optimisations
    if (str_starts_with($db['dsn'], 'sqlite:')) {
        $pdo->exec('PRAGMA journal_mode=WAL');
        $pdo->exec('PRAGMA foreign_keys=ON');
    }

    return $pdo;
}

function init_schema(): void
{
    $pdo = get_db();
    $driver = $pdo->getAttribute(PDO::ATTR_DRIVER_NAME);

    if ($driver === 'sqlite') {
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS employees (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                email       TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL,
                role        TEXT    NOT NULL DEFAULT 'employee',  -- admin | employee
                active      INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS employee_regions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
                region      TEXT    NOT NULL,
                country     TEXT    NOT NULL DEFAULT 'India',
                UNIQUE(employee_id, region, country)
            );
            CREATE TABLE IF NOT EXISTS leads (
                lead_key            TEXT    PRIMARY KEY,
                business_name       TEXT    NOT NULL DEFAULT '',
                category            TEXT    NOT NULL DEFAULT '',
                owner_name          TEXT    NOT NULL DEFAULT '',
                phone_primary       TEXT    NOT NULL DEFAULT '',
                phone_secondary     TEXT    NOT NULL DEFAULT '',
                whatsapp            TEXT    NOT NULL DEFAULT '',
                email               TEXT    NOT NULL DEFAULT '',
                address             TEXT    NOT NULL DEFAULT '',
                city                TEXT    NOT NULL DEFAULT '',
                pincode             TEXT    NOT NULL DEFAULT '',
                latitude            REAL,
                longitude           REAL,
                opening_hours       TEXT    NOT NULL DEFAULT '',
                has_website         INTEGER NOT NULL DEFAULT 0,
                website_url         TEXT    NOT NULL DEFAULT '',
                website_quality     TEXT    NOT NULL DEFAULT 'none',
                rating              REAL,
                review_count        INTEGER,
                years_in_business   TEXT    NOT NULL DEFAULT '',
                socials             TEXT    NOT NULL DEFAULT '',
                source              TEXT    NOT NULL DEFAULT '',
                source_url          TEXT    NOT NULL DEFAULT '',
                place_id            TEXT    NOT NULL DEFAULT '',
                lead_score          INTEGER NOT NULL DEFAULT 0,
                lead_tier           TEXT    NOT NULL DEFAULT 'COLD',
                data_fetched_at     TEXT    NOT NULL DEFAULT '',
                stale_after         TEXT    NOT NULL DEFAULT '',
                outreach_status     TEXT    NOT NULL DEFAULT 'new',
                opt_out             INTEGER NOT NULL DEFAULT 0,
                sample_site_url     TEXT    NOT NULL DEFAULT '',
                pitch_deck_url      TEXT    NOT NULL DEFAULT '',
                notes               TEXT    NOT NULL DEFAULT '',
                contact_channel     TEXT    NOT NULL DEFAULT '',
                wa_link             TEXT    NOT NULL DEFAULT '',
                -- CRM columns
                region              TEXT    NOT NULL DEFAULT '',
                country             TEXT    NOT NULL DEFAULT '',
                assigned_employee   TEXT    NOT NULL DEFAULT '',
                pain_points         TEXT    NOT NULL DEFAULT '',
                recommended_pitch   TEXT    NOT NULL DEFAULT '',
                -- CRM state
                crm_status          TEXT    NOT NULL DEFAULT 'new',  -- new | qualified | callback | not_qualified
                crm_notes           TEXT    NOT NULL DEFAULT '',
                last_contacted_at   TEXT,
                next_callback_at    TEXT,
                assigned_employee_id INTEGER,
                removed_at          TEXT,
                created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS lead_activities (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_key    TEXT    NOT NULL REFERENCES leads(lead_key) ON DELETE CASCADE,
                employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
                action      TEXT    NOT NULL,  -- tagged | note | called | contacted
                old_value   TEXT,
                new_value   TEXT,
                description TEXT    NOT NULL DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS proposals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_key    TEXT    NOT NULL REFERENCES leads(lead_key) ON DELETE CASCADE,
                type        TEXT    NOT NULL,  -- sample_site | pitch_deck
                html        TEXT    NOT NULL,
                file_name   TEXT    NOT NULL DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                UNIQUE(lead_key, type)
            );
            CREATE INDEX IF NOT EXISTS idx_leads_region     ON leads(region);
            CREATE INDEX IF NOT EXISTS idx_leads_crm_status ON leads(crm_status);
            CREATE INDEX IF NOT EXISTS idx_leads_employee   ON leads(assigned_employee_id);
            CREATE INDEX IF NOT EXISTS idx_leads_removed    ON leads(removed_at);
            CREATE INDEX IF NOT EXISTS idx_activities_lead  ON lead_activities(lead_key);
        ");
    } else {
        // MySQL schema
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS employees (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                name        VARCHAR(255) NOT NULL,
                email       VARCHAR(255) NOT NULL UNIQUE,
                password    VARCHAR(255) NOT NULL,
                role        ENUM('admin','employee') NOT NULL DEFAULT 'employee',
                active      TINYINT(1) NOT NULL DEFAULT 1,
                created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            CREATE TABLE IF NOT EXISTS employee_regions (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                employee_id INT NOT NULL,
                region      VARCHAR(255) NOT NULL,
                country     VARCHAR(100) NOT NULL DEFAULT 'India',
                UNIQUE KEY uq_emp_region (employee_id, region, country),
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            CREATE TABLE IF NOT EXISTS leads (
                lead_key            VARCHAR(255) PRIMARY KEY,
                business_name       VARCHAR(500) NOT NULL DEFAULT '',
                category            VARCHAR(255) NOT NULL DEFAULT '',
                owner_name          VARCHAR(255) NOT NULL DEFAULT '',
                phone_primary       VARCHAR(50)  NOT NULL DEFAULT '',
                phone_secondary     VARCHAR(50)  NOT NULL DEFAULT '',
                whatsapp            VARCHAR(50)  NOT NULL DEFAULT '',
                email               VARCHAR(255) NOT NULL DEFAULT '',
                address             TEXT         NOT NULL,
                city                VARCHAR(255) NOT NULL DEFAULT '',
                pincode             VARCHAR(20)  NOT NULL DEFAULT '',
                latitude            DECIMAL(10,7),
                longitude           DECIMAL(10,7),
                opening_hours       TEXT         NOT NULL,
                has_website         TINYINT(1)   NOT NULL DEFAULT 0,
                website_url         VARCHAR(500) NOT NULL DEFAULT '',
                website_quality     VARCHAR(50)  NOT NULL DEFAULT 'none',
                rating              DECIMAL(3,1),
                review_count        INT,
                years_in_business   VARCHAR(50)  NOT NULL DEFAULT '',
                socials             TEXT         NOT NULL,
                source              VARCHAR(100) NOT NULL DEFAULT '',
                source_url          VARCHAR(500) NOT NULL DEFAULT '',
                place_id            VARCHAR(255) NOT NULL DEFAULT '',
                lead_score          INT          NOT NULL DEFAULT 0,
                lead_tier           VARCHAR(10)  NOT NULL DEFAULT 'COLD',
                data_fetched_at     DATETIME,
                stale_after         DATETIME,
                outreach_status     VARCHAR(50)  NOT NULL DEFAULT 'new',
                opt_out             TINYINT(1)   NOT NULL DEFAULT 0,
                sample_site_url     VARCHAR(500) NOT NULL DEFAULT '',
                pitch_deck_url      VARCHAR(500) NOT NULL DEFAULT '',
                notes               TEXT         NOT NULL,
                contact_channel     VARCHAR(20)  NOT NULL DEFAULT '',
                wa_link             VARCHAR(500) NOT NULL DEFAULT '',
                -- CRM columns
                region              VARCHAR(100) NOT NULL DEFAULT '',
                country             VARCHAR(100) NOT NULL DEFAULT '',
                assigned_employee   VARCHAR(255) NOT NULL DEFAULT '',
                pain_points         TEXT         NOT NULL,
                recommended_pitch   TEXT         NOT NULL,
                -- CRM state
                crm_status          ENUM('new','qualified','callback','not_qualified') NOT NULL DEFAULT 'new',
                crm_notes           TEXT         NOT NULL,
                last_contacted_at   DATETIME,
                next_callback_at    DATETIME,
                assigned_employee_id INT,
                removed_at          DATETIME,
                created_at          DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at          DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            CREATE TABLE IF NOT EXISTS lead_activities (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                lead_key    VARCHAR(255) NOT NULL,
                employee_id INT,
                action      VARCHAR(50)  NOT NULL,
                old_value   VARCHAR(255),
                new_value   VARCHAR(255),
                description TEXT         NOT NULL,
                created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_key) REFERENCES leads(lead_key) ON DELETE CASCADE,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            CREATE INDEX idx_leads_region     ON leads(region);
            CREATE INDEX idx_leads_crm_status ON leads(crm_status);
            CREATE INDEX idx_leads_employee   ON leads(assigned_employee_id);
            CREATE INDEX idx_leads_removed    ON leads(removed_at);
            CREATE INDEX idx_activities_lead  ON lead_activities(lead_key);
            CREATE TABLE IF NOT EXISTS proposals (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                lead_key    VARCHAR(255) NOT NULL,
                type        VARCHAR(50)  NOT NULL,  -- sample_site | pitch_deck
                html        LONGTEXT     NOT NULL,
                file_name   VARCHAR(255) NOT NULL DEFAULT '',
                created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_proposal (lead_key, type),
                FOREIGN KEY (lead_key) REFERENCES leads(lead_key) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ");
    }
}