<?php
/**
 * TKVibes CRM — Admin Dashboard
 * Manages leads, employees, regions, and settings.
 */
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/auth.php';
require __DIR__ . '/lib/functions.php';

$emp = require_admin();
$pdo = get_db();

$tab = $_GET['tab'] ?? 'overview';

// Handle POST actions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action === 'add_employee') {
        $name     = trim($_POST['name'] ?? '');
        $email    = trim($_POST['email'] ?? '');
        $password = $_POST['password'] ?? '';
        $role     = $_POST['role'] ?? 'employee';

        if ($name && $email && $password) {
            $hash = password_hash($password, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("INSERT INTO employees (name, email, password, role) VALUES (?, ?, ?, ?)");
            $stmt->execute([$name, $email, $hash, $role]);
            $emp_id = $pdo->lastInsertId();

            // Save regions
            $regions = $_POST['regions'] ?? [];
            foreach ($regions as $r) {
                if (trim($r)) {
                    $parts = explode('|', $r);
                    $region = trim($parts[0]);
                    $country = trim($parts[1] ?? 'India');
                    $stmt = $pdo->prepare("INSERT INTO employee_regions (employee_id, region, country) VALUES (?, ?, ?)");
                    $stmt->execute([$emp_id, $region, $country]);
                }
            }
            flash_set('success', "Employee '$name' added.");
        }
        header('Location: admin.php?tab=employees');
        exit;
    }

    if ($action === 'edit_employee') {
        $id      = (int)($_POST['id'] ?? 0);
        $name    = trim($_POST['name'] ?? '');
        $email   = trim($_POST['email'] ?? '');
        $role    = $_POST['role'] ?? 'employee';
        $active  = isset($_POST['active']) ? 1 : 0;
        $new_pw  = trim($_POST['password'] ?? '');

        if ($id && $name && $email) {
            if ($new_pw) {
                $hash = password_hash($new_pw, PASSWORD_BCRYPT);
                $stmt = $pdo->prepare("UPDATE employees SET name=?, email=?, role=?, active=?, password=?, updated_at=datetime('now') WHERE id=?");
                $stmt->execute([$name, $email, $role, $active, $hash, $id]);
            } else {
                $stmt = $pdo->prepare("UPDATE employees SET name=?, email=?, role=?, active=?, updated_at=datetime('now') WHERE id=?");
                $stmt->execute([$name, $email, $role, $active, $id]);
            }

            // Update regions
            $pdo->prepare("DELETE FROM employee_regions WHERE employee_id = ?")->execute([$id]);
            $regions = $_POST['regions'] ?? [];
            foreach ($regions as $r) {
                if (trim($r)) {
                    $parts = explode('|', $r);
                    $region = trim($parts[0]);
                    $country = trim($parts[1] ?? 'India');
                    $stmt = $pdo->prepare("INSERT INTO employee_regions (employee_id, region, country) VALUES (?, ?, ?)");
                    $stmt->execute([$id, $region, $country]);
                }
            }
            flash_set('success', "Employee updated.");
        }
        header('Location: admin.php?tab=employees');
        exit;
    }

    if ($action === 'delete_employee') {
        $id = (int)($_POST['id'] ?? 0);
        if ($id && $id !== $emp['id']) {
            $pdo->prepare("DELETE FROM employee_regions WHERE employee_id = ?")->execute([$id]);
            $pdo->prepare("DELETE FROM employees WHERE id = ?")->execute([$id]);
            flash_set('success', "Employee deleted.");
        }
        header('Location: admin.php?tab=employees');
        exit;
    }

    if ($action === 'update_lead') {
        $lead_key = $_POST['lead_key'] ?? '';
        if ($lead_key) {
            $fields = ['region', 'country', 'assigned_employee', 'crm_status', 'crm_notes', 'lead_tier', 'outreach_status'];
            $updates = [];
            $params = [];
            foreach ($fields as $f) {
                if (isset($_POST[$f])) {
                    $updates[] = "$f = ?";
                    $params[] = $_POST[$f];
                }
            }
            if ($updates) {
                $updates[] = "updated_at = datetime('now')";
                $params[] = $lead_key;
                $pdo->prepare("UPDATE leads SET " . implode(', ', $updates) . " WHERE lead_key = ?")->execute($params);
                flash_set('success', "Lead updated.");
            }
        }
        header('Location: admin.php?tab=leads' . (isset($_POST['page']) ? '&page=' . (int)$_POST['page'] : ''));
        exit;
    }

    if ($action === 'delete_lead') {
        $lead_key = $_POST['lead_key'] ?? '';
        if ($lead_key) {
            $pdo->prepare("DELETE FROM lead_activities WHERE lead_key = ?")->execute([$lead_key]);
            $pdo->prepare("DELETE FROM leads WHERE lead_key = ?")->execute([$lead_key]);
            flash_set('success', "Lead deleted.");
        }
        header('Location: admin.php?tab=leads');
        exit;
    }

    if ($action === 'sync_from_sheet') {
        // Trigger sync from Google Sheets (if configured)
        $cfg = require __DIR__ . '/config.local.php';
        if ($cfg['google_service_account'] && $cfg['google_sheet_id']) {
            try {
                require __DIR__ . '/lib/GoogleSheetsClient.php';
                $client = new GoogleSheetsClient($cfg['google_service_account'], $cfg['google_sheet_id']);
                [$header, $rows] = $client->read_sheet();
                // Import rows into leads table
                $imported = 0;
                foreach ($rows as $row) {
                    if (empty($row)) continue;
                    $data = array_combine($header, array_pad($row, count($header), ''));
                    $lk = $data['lead_key'] ?? '';
                    if (!$lk) continue;

                    $stmt = $pdo->prepare("SELECT lead_key FROM leads WHERE lead_key = ?");
                    $stmt->execute([$lk]);
                    if (!$stmt->fetch()) {
                        $ins = $pdo->prepare("INSERT INTO leads (lead_key, business_name, category, city, phone_primary, email, region, country, assigned_employee, pain_points, recommended_pitch, crm_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', datetime('now'), datetime('now'))");
                        $ins->execute([
                            $lk, $data['business_name'] ?? '', $data['category'] ?? '',
                            $data['city'] ?? '', $data['phone_primary'] ?? '', $data['email'] ?? '',
                            $data['region'] ?? '', $data['country'] ?? '',
                            $data['assigned_employee'] ?? '', $data['pain_points'] ?? '',
                            $data['recommended_pitch'] ?? '',
                        ]);
                        $imported++;
                    }
                }
                flash_set('success', "Synced $imported new leads from Google Sheet.");
            } catch (Exception $e) {
                flash_set('error', "Sync failed: " . $e->getMessage());
            }
        } else {
            flash_set('error', "Google Sheets sync not configured. Set google_service_account and google_sheet_id in config.local.php");
        }
        header('Location: admin.php?tab=leads');
        exit;
    }

    if ($action === 'export_csv') {
        $filters = [
            'status'  => $_GET['status'] ?? '',
            'tier'    => $_GET['tier'] ?? '',
            'region'  => $_GET['region'] ?? '',
            'country' => $_GET['country'] ?? '',
            'q'       => $_GET['q'] ?? '',
        ];
        $leads = leads_query($emp, $filters);

        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="tkvibes-leads-export.csv"');
        $out = fopen('php://output', 'w');
        // Header
        fputcsv($out, ['Business Name', 'Category', 'City', 'Country', 'Region', 'Phone', 'Email', 'Rating', 'Reviews', 'Score', 'Tier', 'Status', 'Pain Points', 'Pitch', 'Assigned To', 'Notes']);
        foreach ($leads as $l) {
            fputcsv($out, [
                $l['business_name'], $l['category'], $l['city'], $l['country'], $l['region'],
                $l['phone_primary'], $l['email'], $l['rating'], $l['review_count'],
                $l['lead_score'], $l['lead_tier'], $l['crm_status'] ?? 'new',
                $l['pain_points'], $l['recommended_pitch'], $l['assigned_employee'],
                $l['crm_notes'],
            ]);
        }
        fclose($out);
        exit;
    }
}

// ── Data for tabs ───────────────────────────────────────────────────────────

$employees = $pdo->query("SELECT * FROM employees ORDER BY name")->fetchAll();
foreach ($employees as &$e) {
    $stmt = $pdo->prepare("SELECT region, country FROM employee_regions WHERE employee_id = ?");
    $stmt->execute([$e['id']]);
    $e['regions'] = $stmt->fetchAll();
}
unset($e);

// Overview stats
$stats = [];
$stats['total_leads'] = $pdo->query("SELECT COUNT(*) FROM leads")->fetchColumn();
$stats['new_leads'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE crm_status = 'new'")->fetchColumn();
$stats['qualified'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE crm_status = 'qualified'")->fetchColumn();
$stats['callback'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE crm_status = 'callback'")->fetchColumn();
$stats['not_qualified'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE crm_status = 'not_qualified'")->fetchColumn();
$stats['hot'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE lead_tier = 'HOT'")->fetchColumn();
$stats['warm'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE lead_tier = 'WARM'")->fetchColumn();
$stats['cold'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE lead_tier = 'COLD'")->fetchColumn();
$stats['canada'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE country = 'Canada'")->fetchColumn();
$stats['india'] = $pdo->query("SELECT COUNT(*) FROM leads WHERE country = 'India'")->fetchColumn();
$stats['employees'] = count($employees);
$stats['active_employees'] = $pdo->query("SELECT COUNT(*) FROM employees WHERE active = 1")->fetchColumn();

// Leads list (paginated)
$page = max(1, (int)($_GET['page'] ?? 1));
$per_page = 50;
$admin_filters = [
    'status'  => $_GET['status'] ?? '',
    'tier'    => $_GET['tier'] ?? '',
    'region'  => $_GET['region'] ?? '',
    'country' => $_GET['country'] ?? '',
    'q'       => $_GET['q'] ?? '',
    'assigned_employee_id' => $_GET['assigned'] ?? '',
];
$all_leads = leads_query($emp, $admin_filters);
$total_leads = count($all_leads);
$leads_page = array_slice($all_leads, ($page - 1) * $per_page, $per_page);
$total_pages = max(1, ceil($total_leads / $per_page));

// All regions
$all_regions = [];
$regions_data = $pdo->query("SELECT DISTINCT region, country FROM leads WHERE region != '' ORDER BY country, region")->fetchAll();
foreach ($regions_data as $r) {
    $all_regions[] = $r['region'] . '|' . $r['country'];
}
?>
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TKVibes CRM — Admin</title>
<link rel="stylesheet" href="assets/css/crm.css?v=1">
</head>
<body class="admin-page">
<nav class="navbar">
    <div class="nav-left">
        <img src="../tk-vibes-mark.svg" alt="TKVibes" height="32">
        <span class="nav-title">CRM Admin</span>
        <span class="nav-role"><?= e($emp['name']) ?></span>
    </div>
    <div class="nav-right">
        <a href="dashboard.php" class="btn btn-sm btn-outline">← Employee Dashboard</a>
        <a href="logout.php" class="btn btn-sm btn-outline">Logout</a>
    </div>
</nav>

<div class="admin-tabs">
    <a href="?tab=overview" class="tab <?= $tab === 'overview' ? 'active' : '' ?>">📊 Overview</a>
    <a href="?tab=employees" class="tab <?= $tab === 'employees' ? 'active' : '' ?>">👥 Employees</a>
    <a href="?tab=leads" class="tab <?= $tab === 'leads' ? 'active' : '' ?>">📋 All Leads</a>
</div>

<div class="admin-content">
    <?php $flashes = flash_get(); foreach ($flashes as $f): ?>
        <div class="alert alert-<?= e($f['type']) ?>"><?= e($f['msg']) ?></div>
    <?php endforeach; ?>

    <?php if ($tab === 'overview'): ?>
        <div class="admin-overview">
            <h2>📊 Overview</h2>
            <div class="stats-grid">
                <div class="stat-card stat-all"><div class="stat-num"><?= $stats['total_leads'] ?></div><div class="stat-label">Total Leads</div></div>
                <div class="stat-card stat-new"><div class="stat-num"><?= $stats['new_leads'] ?></div><div class="stat-label">New</div></div>
                <div class="stat-card stat-qualified"><div class="stat-num"><?= $stats['qualified'] ?></div><div class="stat-label">Qualified</div></div>
                <div class="stat-card stat-callback"><div class="stat-num"><?= $stats['callback'] ?></div><div class="stat-label">Callback</div></div>
                <div class="stat-card stat-notqualified"><div class="stat-num"><?= $stats['not_qualified'] ?></div><div class="stat-label">Not Qualified</div></div>
                <div class="stat-card"><div class="stat-num"><?= $stats['hot'] ?></div><div class="stat-label">🔥 HOT</div></div>
                <div class="stat-card"><div class="stat-num"><?= $stats['warm'] ?></div><div class="stat-label">🔥 WARM</div></div>
                <div class="stat-card"><div class="stat-num"><?= $stats['cold'] ?></div><div class="stat-label">❄️ COLD</div></div>
                <div class="stat-card"><div class="stat-num"><?= $stats['india'] ?></div><div class="stat-label">🇮🇳 India</div></div>
                <div class="stat-card"><div class="stat-num"><?= $stats['canada'] ?></div><div class="stat-label">🇨🇦 Canada</div></div>
                <div class="stat-card"><div class="stat-num"><?= $stats['active_employees'] ?>/<?= $stats['employees'] ?></div><div class="stat-label">Active Employees</div></div>
            </div>

            <h3>Quick Links</h3>
            <div class="quick-links">
                <a href="admin.php?tab=employees" class="btn btn-outline">✚ Add Employee</a>
                <a href="admin.php?tab=leads&status=new" class="btn btn-outline">📋 New Leads</a>
                <a href="admin.php?tab=leads&status=qualified" class="btn btn-outline">✅ Qualified Leads</a>
                <a href="admin.php?tab=leads" class="btn btn-outline">📥 Export CSV</a>
                <form method="post" style="display:inline" action="admin.php?tab=leads">
                    <input type="hidden" name="action" value="sync_from_sheet">
                    <button type="submit" class="btn btn-outline" onclick="return confirm('Sync leads from Google Sheet?')">🔄 Sync from Sheet</button>
                </form>
            </div>
        </div>

    <?php elseif ($tab === 'employees'): ?>
        <div class="admin-employees">
            <h2>👥 Manage Employees</h2>

            <h3>Add New Employee</h3>
            <form method="post" class="employee-form">
                <input type="hidden" name="action" value="add_employee">
                <div class="form-row">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" name="name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" class="form-control" required minlength="6">
                    </div>
                    <div class="form-group">
                        <label>Role</label>
                        <select name="role" class="form-control">
                            <option value="employee">Employee</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label>Assigned Regions</label>
                    <select name="regions[]" class="form-control region-select" multiple>
                        <?php foreach ($all_regions as $r): ?>
                            <?php $parts = explode('|', $r); ?>
                            <option value="<?= e($r) ?>"><?= e($parts[0]) ?> (<?= e($parts[1] ?? 'India') ?>)</option>
                        <?php endforeach; ?>
                    </select>
                    <small class="text-muted">Hold Ctrl/Cmd to select multiple. Regions auto-populate from lead data.</small>
                </div>
                <button type="submit" class="btn btn-primary">Add Employee</button>
            </form>

            <h3>Existing Employees</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Active</th>
                        <th>Regions</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($employees as $e): ?>
                        <tr>
                            <td><?= e($e['name']) ?></td>
                            <td><?= e($e['email']) ?></td>
                            <td><?= e(ucfirst($e['role'])) ?></td>
                            <td><?= $e['active'] ? '✅' : '❌' ?></td>
                            <td>
                                <?php foreach ($e['regions'] as $r): ?>
                                    <span class="region-tag"><?= e($r['region']) ?> (<?= e($r['country']) ?>)</span>
                                <?php endforeach; ?>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-outline" onclick="editEmployee(<?= $e['id'] ?>, '<?= e(addslashes($e['name'])) ?>', '<?= e($e['email']) ?>', '<?= e($e['role']) ?>', <?= $e['active'] ? 'true' : 'false' ?>, <?= e(json_encode(array_map(fn($r) => $r['region'] . '|' . $r['country'], $e['regions']))) ?>)">Edit</button>
                                <?php if ((int)$e['id'] !== $emp['id']): ?>
                                    <form method="post" style="display:inline" onsubmit="return confirm('Delete this employee?')">
                                        <input type="hidden" name="action" value="delete_employee">
                                        <input type="hidden" name="id" value="<?= $e['id'] ?>">
                                        <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                                    </form>
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <!-- Edit Employee Modal -->
        <div id="editEmployeeModal" class="modal" style="display:none">
            <div class="modal-content">
                <span class="modal-close" onclick="closeModal()">&times;</span>
                <h3>Edit Employee</h3>
                <form method="post" class="employee-form">
                    <input type="hidden" name="action" value="edit_employee">
                    <input type="hidden" name="id" id="edit_id">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Name</label>
                            <input type="text" name="name" id="edit_name" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" name="email" id="edit_email" class="form-control" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>New Password (leave blank to keep current)</label>
                        <input type="password" name="password" class="form-control" minlength="6" placeholder="Leave blank to keep existing">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Role</label>
                            <select name="role" id="edit_role" class="form-control">
                                <option value="employee">Employee</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Active</label>
                            <input type="checkbox" name="active" id="edit_active" value="1" checked>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Regions</label>
                        <select name="regions[]" class="form-control region-select" multiple id="edit_regions">
                            <?php foreach ($all_regions as $r): ?>
                                <?php $parts = explode('|', $r); ?>
                                <option value="<?= e($r) ?>"><?= e($parts[0]) ?> (<?= e($parts[1] ?? 'India') ?>)</option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </form>
            </div>
        </div>

    <?php elseif ($tab === 'leads'): ?>
        <div class="admin-leads">
            <h2>📋 All Leads</h2>

            <div class="admin-filters">
                <form method="get" class="filter-form">
                    <input type="hidden" name="tab" value="leads">
                    <input type="text" name="q" class="form-control" placeholder="Search..." value="<?= e($_GET['q'] ?? '') ?>">
                    <select name="status" class="form-control" onchange="this.form.submit()">
                        <option value="">All Status</option>
                        <option value="new" <?= ($_GET['status'] ?? '') === 'new' ? 'selected' : '' ?>>New</option>
                        <option value="qualified" <?= ($_GET['status'] ?? '') === 'qualified' ? 'selected' : '' ?>>Qualified</option>
                        <option value="callback" <?= ($_GET['status'] ?? '') === 'callback' ? 'selected' : '' ?>>Callback</option>
                        <option value="not_qualified" <?= ($_GET['status'] ?? '') === 'not_qualified' ? 'selected' : '' ?>>Not Qualified</option>
                    </select>
                    <select name="tier" class="form-control" onchange="this.form.submit()">
                        <option value="">All Tiers</option>
                        <option value="HOT" <?= ($_GET['tier'] ?? '') === 'HOT' ? 'selected' : '' ?>>HOT</option>
                        <option value="WARM" <?= ($_GET['tier'] ?? '') === 'WARM' ? 'selected' : '' ?>>WARM</option>
                        <option value="COLD" <?= ($_GET['tier'] ?? '') === 'COLD' ? 'selected' : '' ?>>COLD</option>
                    </select>
                    <select name="assigned" class="form-control" onchange="this.form.submit()">
                        <option value="">All Assignments</option>
                        <option value="unassigned" <?= ($_GET['assigned'] ?? '') === 'unassigned' ? 'selected' : '' ?>>Unassigned</option>
                        <?php foreach ($employees as $e): ?>
                            <?php if ($e['active']): ?>
                                <option value="<?= $e['id'] ?>" <?= ($_GET['assigned'] ?? '') == $e['id'] ? 'selected' : '' ?>><?= e($e['name']) ?></option>
                            <?php endif; ?>
                        <?php endforeach; ?>
                    </select>
                    <button type="submit" class="btn btn-sm btn-primary">Filter</button>
                    <a href="admin.php?tab=leads" class="btn btn-sm btn-outline">Clear</a>
                    <a href="admin.php?tab=leads&action=export_csv<?= isset($_SERVER['QUERY_STRING']) ? '&' . $_SERVER['QUERY_STRING'] : '' ?>" class="btn btn-sm btn-outline">📥 Export CSV</a>
                </form>
            </div>

            <div class="admin-actions">
                <form method="post" style="display:inline">
                    <input type="hidden" name="action" value="sync_from_sheet">
                    <button type="submit" class="btn btn-sm btn-outline" onclick="return confirm('Sync leads from Google Sheet?')">🔄 Sync from Sheet</button>
                </form>
                <span class="text-muted"><?= $total_leads ?> leads total</span>
            </div>

            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Business</th>
                            <th>Category</th>
                            <th>City</th>
                            <th>Country</th>
                            <th>Region</th>
                            <th>Phone</th>
                            <th>Score</th>
                            <th>Tier</th>
                            <th>Status</th>
                            <th>Assigned</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($leads_page as $l): ?>
                            <tr>
                                <td><?= e(truncate($l['business_name'], 40)) ?></td>
                                <td><?= e(truncate($l['category'], 25)) ?></td>
                                <td><?= e($l['city']) ?></td>
                                <td><?= e($l['country']) ?></td>
                                <td><?= e($l['region']) ?></td>
                                <td><?= e($l['phone_primary'] ?: '—') ?></td>
                                <td><?= (int)$l['lead_score'] ?></td>
                                <td><?= tier_badge($l['lead_tier']) ?></td>
                                <td><?= status_badge($l['crm_status'] ?? 'new') ?></td>
                                <td><?= e($l['assigned_employee'] ?: '—') ?></td>
                                <td>
                                    <a href="dashboard.php?lead=<?= urlencode($l['lead_key']) ?>" class="btn btn-sm btn-outline" target="_blank">View</a>
                                    <form method="post" style="display:inline" onsubmit="return confirm('Delete this lead?')">
                                        <input type="hidden" name="action" value="delete_lead">
                                        <input type="hidden" name="lead_key" value="<?= e($l['lead_key']) ?>">
                                        <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                        <?php if (empty($leads_page)): ?>
                            <tr><td colspan="11" class="text-muted">No leads found.</td></tr>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>

            <?php if ($total_pages > 1): ?>
                <div class="pagination">
                    <?php for ($i = 1; $i <= $total_pages; $i++): ?>
                        <a href="?tab=leads&page=<?= $i ?><?= isset($_SERVER['QUERY_STRING']) ? '&' . preg_replace('/&?page=\d+/', '', $_SERVER['QUERY_STRING']) : '' ?>" class="page-link <?= $i === $page ? 'active' : '' ?>"><?= $i ?></a>
                    <?php endfor; ?>
                </div>
            <?php endif; ?>
        </div>
    <?php endif; ?>
</div>

<script src="assets/js/crm.js?v=1"></script>
<script>
function editEmployee(id, name, email, role, active, regions) {
    document.getElementById('edit_id').value = id;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_email').value = email;
    document.getElementById('edit_role').value = role;
    document.getElementById('edit_active').checked = active;
    const sel = document.getElementById('edit_regions');
    for (let opt of sel.options) opt.selected = regions.includes(opt.value);
    document.getElementById('editEmployeeModal').style.display = 'flex';
}
function closeModal() {
    document.getElementById('editEmployeeModal').style.display = 'none';
}
</script>
</body>
</html>