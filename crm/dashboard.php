<?php
/**
 * TKVibes CRM — Employee Dashboard
 */
require __DIR__ . '/lib/db.php';
require __DIR__ . '/lib/auth.php';
require __DIR__ . '/lib/functions.php';

$emp = require_auth();

$status_filter = $_GET['status'] ?? '';
$tier_filter   = $_GET['tier'] ?? '';
$q_filter      = $_GET['q'] ?? '';
$region_filter = $_GET['region'] ?? '';
$lead_key      = $_GET['lead'] ?? '';

$filters = array_filter([
    'status' => $status_filter,
    'tier'   => $tier_filter,
    'q'      => $q_filter,
    'region' => $region_filter,
]);

$leads = leads_query($emp, $filters);
$selected_lead = $lead_key ? get_lead($lead_key) : null;
$activities = $selected_lead ? get_lead_activities($selected_lead['lead_key']) : [];

// Stats
$stats = ['new' => 0, 'qualified' => 0, 'callback' => 0, 'not_qualified' => 0, 'total' => count($leads)];
foreach ($leads as $l) {
    $s = $l['crm_status'] ?? 'new';
    $stats[$s] = ($stats[$s] ?? 0) + 1;
}
?>
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TKVibes CRM — Dashboard</title>
<link rel="stylesheet" href="assets/css/crm.css?v=1">
</head>
<body class="dashboard-page">
<nav class="navbar">
    <div class="nav-left">
        <img src="../tk-vibes-mark.svg" alt="TKVibes" height="32">
        <span class="nav-title">CRM</span>
        <span class="nav-role"><?= e($emp['name']) ?> (<?= ucfirst($emp['role']) ?>)</span>
    </div>
    <div class="nav-right">
        <a href="?lead=<?= urlencode('_training') ?>" class="btn btn-sm btn-training" onclick="event.preventDefault(); window.open('../cold-call-training.html', '_blank', 'width=1200,height=800')">
            🎯 Cold Call Training
        </a>
        <a href="logout.php" class="btn btn-sm btn-outline">Logout</a>
    </div>
</nav>

<div class="dashboard-layout">
    <!-- Sidebar: filters + stats -->
    <aside class="sidebar">
        <div class="stats-cards">
            <div class="stat-card stat-all" onclick="window.location='dashboard.php'">
                <div class="stat-num"><?= $stats['total'] ?></div>
                <div class="stat-label">All Leads</div>
            </div>
            <div class="stat-card stat-new" onclick="window.location='dashboard.php?status=new'">
                <div class="stat-num"><?= $stats['new'] ?></div>
                <div class="stat-label">New</div>
            </div>
            <div class="stat-card stat-qualified" onclick="window.location='dashboard.php?status=qualified'">
                <div class="stat-num"><?= $stats['qualified'] ?></div>
                <div class="stat-label">Qualified</div>
            </div>
            <div class="stat-card stat-callback" onclick="window.location='dashboard.php?status=callback'">
                <div class="stat-num"><?= $stats['callback'] ?></div>
                <div class="stat-label">Callback</div>
            </div>
            <div class="stat-card stat-notqualified" onclick="window.location='dashboard.php?status=not_qualified'">
                <div class="stat-num"><?= $stats['not_qualified'] ?></div>
                <div class="stat-label">Not Qualified</div>
            </div>
        </div>

        <form method="get" class="filter-form">
            <input type="text" name="q" class="form-control" placeholder="Search business, city, phone..." value="<?= e($q_filter) ?>">
            <select name="tier" class="form-control" onchange="this.form.submit()">
                <option value="">All Tiers</option>
                <option value="HOT" <?= $tier_filter === 'HOT' ? 'selected' : '' ?>>HOT</option>
                <option value="WARM" <?= $tier_filter === 'WARM' ? 'selected' : '' ?>>WARM</option>
                <option value="COLD" <?= $tier_filter === 'COLD' ? 'selected' : '' ?>>COLD</option>
            </select>
            <button type="submit" class="btn btn-sm btn-primary">Filter</button>
        </form>

        <?php if ($emp['role'] === 'admin'): ?>
            <div class="admin-shortcuts">
                <a href="admin.php" class="btn btn-sm btn-outline">⚙ Admin Dashboard</a>
            </div>
        <?php endif; ?>
    </aside>

    <!-- Main content -->
    <main class="main-content">
        <?php if ($selected_lead && $selected_lead['lead_key'] === '_training'): ?>
            <!-- Cold Call Training iframe -->
            <div class="training-view">
                <div class="training-header">
                    <h2>🎯 Cold Call Training</h2>
                    <a href="dashboard.php" class="btn btn-sm btn-outline">← Back</a>
                </div>
                <iframe src="../cold-call-training.html" class="training-iframe" frameborder="0"></iframe>
            </div>

        <?php elseif ($selected_lead && lead_accessible_to($emp, $selected_lead)): ?>
            <!-- Lead Detail View -->
            <?php include __DIR__ . '/templates/lead_detail.php'; ?>

        <?php else: ?>
            <!-- Lead List -->
            <?php if (empty($leads)): ?>
                <div class="empty-state">
                    <h3>No leads found</h3>
                    <p>Adjust your filters or wait for the next lead discovery run.</p>
                </div>
            <?php else: ?>
                <div class="lead-list-header">
                    <h2>My Leads <span class="text-muted">(<?= count($leads) ?>)</span></h2>
                </div>
                <div class="lead-grid">
                    <?php foreach ($leads as $l): ?>
                        <a href="dashboard.php?lead=<?= urlencode($l['lead_key']) ?>&status=<?= urlencode($status_filter) ?>&tier=<?= urlencode($tier_filter) ?>&q=<?= urlencode($q_filter) ?>" class="lead-card">
                            <div class="lead-card-header">
                                <h3><?= e(truncate($l['business_name'], 60)) ?></h3>
                                <?= tier_badge($l['lead_tier']) ?>
                                <?= status_badge($l['crm_status'] ?? 'new') ?>
                            </div>
                            <div class="lead-card-body">
                                <span class="lead-meta">📍 <?= e($l['city']) ?>, <?= e($l['country']) ?></span>
                                <span class="lead-meta">📂 <?= e($l['category']) ?></span>
                                <?php if ($l['phone_primary']): ?>
                                    <span class="lead-meta">📞 <?= e(mask_phone($l['phone_primary'])) ?></span>
                                <?php endif; ?>
                                <span class="lead-meta">⭐ <?= e($l['rating'] ?? '—') ?> (<?= e($l['review_count'] ?? 0) ?>)</span>
                            </div>
                            <div class="lead-card-footer">
                                <span class="lead-score">Score: <?= (int)$l['lead_score'] ?></span>
                                <?php if ($l['last_activity']): ?>
                                    <span class="text-muted"><?= time_ago($l['last_activity']) ?></span>
                                <?php endif; ?>
                            </div>
                        </a>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        <?php endif; ?>
    </main>
</div>

<script src="assets/js/crm.js?v=1"></script>
</body>
</html>