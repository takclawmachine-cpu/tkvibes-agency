<?php
header('X-Robots-Tag: noindex, nofollow');
/**
 * TKVibes CRM — Helper functions
 */

function e(?string $s): string
{
    return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8');
}

function json_response($data, int $code = 200): void
{
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function body_json(): array
{
    $raw = file_get_contents('php://input');
    $data = json_decode($raw ?: '', true);
    return is_array($data) ? $data : [];
}

function now_iso(): string
{
    return date('c');
}

function status_label(string $status): string
{
    return match ($status) {
        'new'           => 'New',
        'qualified'     => 'Qualified',
        'callback'      => 'Callback',
        'not_qualified' => 'Not Qualified',
        default         => ucfirst($status),
    };
}

function status_badge(string $status): string
{
    $map = [
        'new'           => 'badge-new',
        'qualified'     => 'badge-qualified',
        'callback'      => 'badge-callback',
        'not_qualified' => 'badge-notqualified',
    ];
    $cls = $map[$status] ?? 'badge-new';
    return '<span class="badge ' . $cls . '">' . e(status_label($status)) . '</span>';
}

function tier_badge(string $tier): string
{
    $cls = match (strtoupper($tier)) {
        'HOT'  => 'tier-hot',
        'WARM' => 'tier-warm',
        default => 'tier-cold',
    };
    return '<span class="badge ' . $cls . '">' . e(strtoupper($tier)) . '</span>';
}

function log_activity(int $employee_id, string $lead_key, string $action,
                      ?string $old_value, ?string $new_value, string $description = ''): void
{
    $pdo = get_db();
    $stmt = $pdo->prepare(
        "INSERT INTO lead_activities (lead_key, employee_id, action, old_value, new_value, description)
         VALUES (?, ?, ?, ?, ?, ?)"
    );
    $stmt->execute([$lead_key, $employee_id, $action, $old_value, $new_value, $description]);
}

function get_employee_regions(int $employee_id): array
{
    $pdo = get_db();
    $stmt = $pdo->prepare("SELECT region, country FROM employee_regions WHERE employee_id = ?");
    $stmt->execute([$employee_id]);
    return $stmt->fetchAll();
}

function get_all_regions(): array
{
    $pdo = get_db();
    return $pdo->query("SELECT DISTINCT region, country FROM employee_regions ORDER BY country, region")->fetchAll();
}

function is_valid_phone(?string $phone): bool
{
    if (!$phone) return false;
    $digits = preg_replace('/\D/', '', $phone);
    return strlen($digits) >= 7;
}

function mask_phone(string $phone): string
{
    if (strlen($phone) < 7) return $phone;
    return substr($phone, 0, 3) . '****' . substr($phone, -4);
}

/**
 * Get the list of leads visible to an employee.
 * - Admin: all leads
 * - Employee: leads assigned to them, or leads in their regions (fallback),
 *   excluding not_qualified leads that were removed more than 24h ago.
 */
function leads_query(array $emp, array $filters = []): array
{
    $pdo = get_db();
    $where = [];
    $params = [];

    // 24h removal rule: not_qualified leads disappear from dashboards after 24h
    $where[] = "(leads.crm_status != 'not_qualified'
                 OR leads.updated_at >= datetime('now', '-1 day'))";

    if ($emp['role'] !== 'admin') {
        // Assigned to this employee by name or by employee_id
        $regions = get_employee_regions($emp['id']);
        $region_conds = ["leads.assigned_employee = ?"];
        $params[] = $emp['name'];
        foreach ($regions as $r) {
            $region_conds[] = "(leads.region = ? AND leads.country = ?)";
            $params[] = $r['region'];
            $params[] = $r['country'];
        }
        $where[] = "(" . implode(" OR ", $region_conds) . ")";
    }

    if (!empty($filters['status'])) {
        $where[] = "leads.crm_status = ?";
        $params[] = $filters['status'];
    }
    if (!empty($filters['tier'])) {
        $where[] = "leads.lead_tier = ?";
        $params[] = strtoupper($filters['tier']);
    }
    if (!empty($filters['region'])) {
        $where[] = "leads.region = ?";
        $params[] = $filters['region'];
    }
    if (!empty($filters['country'])) {
        $where[] = "leads.country = ?";
        $params[] = $filters['country'];
    }
    if (!empty($filters['q'])) {
        $q = '%' . $filters['q'] . '%';
        $where[] = "(leads.business_name LIKE ? OR leads.city LIKE ? OR leads.category LIKE ? OR leads.phone_primary LIKE ?)";
        array_push($params, $q, $q, $q, $q);
    }
    if (isset($filters['assigned_employee_id'])) {
        if ($filters['assigned_employee_id'] === 'unassigned') {
            $where[] = "(leads.assigned_employee_id IS NULL OR leads.assigned_employee_id = 0)";
        } else {
            $where[] = "leads.assigned_employee_id = ?";
            $params[] = (int)$filters['assigned_employee_id'];
        }
    }

    $sql = "SELECT leads.*, 
                   (SELECT COUNT(*) FROM lead_activities a WHERE a.lead_key = leads.lead_key) AS activity_count,
                   (SELECT MAX(created_at) FROM lead_activities a WHERE a.lead_key = leads.lead_key) AS last_activity
            FROM leads";
    if ($where) {
        $sql .= " WHERE " . implode(" AND ", $where);
    }
    $sql .= " ORDER BY 
              CASE leads.crm_status WHEN 'qualified' THEN 0 WHEN 'callback' THEN 1 WHEN 'new' THEN 2 ELSE 3 END,
              leads.lead_score DESC, leads.created_at DESC";

    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    return $stmt->fetchAll();
}

function get_lead(string $lead_key): ?array
{
    $pdo = get_db();
    $stmt = $pdo->prepare("SELECT * FROM leads WHERE lead_key = ?");
    $stmt->execute([$lead_key]);
    $lead = $stmt->fetch();
    return $lead ?: null;
}

function get_lead_activities(string $lead_key): array
{
    $pdo = get_db();
    $stmt = $pdo->prepare(
        "SELECT a.*, e.name AS employee_name
         FROM lead_activities a
         LEFT JOIN employees e ON e.id = a.employee_id
         WHERE a.lead_key = ?
         ORDER BY a.created_at DESC
         LIMIT 50"
    );
    $stmt->execute([$lead_key]);
    return $stmt->fetchAll();
}

function lead_has_proposal(string $lead_key, string $type): bool
{
    $pdo = get_db();
    $stmt = $pdo->prepare("SELECT 1 FROM proposals WHERE lead_key = ? AND type = ?");
    $stmt->execute([$lead_key, $type]);
    return (bool)$stmt->fetch();
}

function get_proposal(string $lead_key, string $type): ?array
{
    $pdo = get_db();
    $stmt = $pdo->prepare("SELECT * FROM proposals WHERE lead_key = ? AND type = ?");
    $stmt->execute([$lead_key, $type]);
    $r = $stmt->fetch();
    return $r ?: null;
}

function lead_accessible_to(array $emp, array $lead): bool
{
    if ($emp['role'] === 'admin') return true;
    $regions = get_employee_regions($emp['id']);
    foreach ($regions as $r) {
        if ($r['region'] === $lead['region'] && $r['country'] === $lead['country']) {
            return true;
        }
    }
    if ($lead['assigned_employee'] === $emp['name']) return true;
    if ((int)($lead['assigned_employee_id'] ?? 0) === $emp['id']) return true;
    return false;
}

/**
 * Log a system-level event (workflow error, cron result, API failure).
 * Writes to system_logs table.
 */
function log_system(string $level, string $source, string $message, array $context = []): void
{
    try {
        $pdo = get_db();
        $ctx = json_encode($context, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $stmt = $pdo->prepare(
            "INSERT INTO system_logs (level, source, message, context, created_at)
             VALUES (?, ?, ?, ?, " . (
                $pdo->getAttribute(PDO::ATTR_DRIVER_NAME) === 'sqlite'
                ? "datetime('now')" : "NOW()"
             ) . ")"
        );
        $stmt->execute([$level, $source, $message, $ctx]);
    } catch (Throwable $e) {
        error_log("log_system failed: " . $e->getMessage());
    }
}

function csv_escape($v): string
{
    $v = (string)$v;
    if (strpbrk($v, ",\"\n\r") !== false) {
        return '"' . str_replace('"', '""', $v) . '"';
    }
    return $v;
}

function flash_set(string $type, string $msg): void
{
    start_session();
    $_SESSION['flash'][] = ['type' => $type, 'msg' => $msg];
}

function flash_get(): array
{
    start_session();
    $f = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $f;
}

/**
 * Render a hidden CSRF token input field.
 * Call this inside any <form> that needs CSRF protection.
 */
function csrf_field(): void
{
    echo '<input type="hidden" name="_csrf_token" value="' . csrf_token() . '">';
}

function fmt_datetime(?string $dt): string
{
    if (!$dt) return '—';
    $ts = strtotime($dt);
    if (!$ts) return '—';
    return date('M j, Y g:i A', $ts);
}

function time_ago(?string $dt): string
{
    if (!$dt) return '—';
    $ts = strtotime($dt);
    if (!$ts) return '—';
    $diff = time() - $ts;
    if ($diff < 60) return 'just now';
    if ($diff < 3600) return floor($diff / 60) . 'm ago';
    if ($diff < 86400) return floor($diff / 3600) . 'h ago';
    if ($diff < 604800) return floor($diff / 86400) . 'd ago';
    return date('M j', $ts);
}

function truncate(string $s, int $len): string
{
    if (mb_strlen($s) <= $len) return $s;
    return mb_substr($s, 0, $len) . '…';
}