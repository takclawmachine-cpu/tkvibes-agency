<?php
/**
 * Lead Detail Template
 * Included by dashboard.php. Variables: $selected_lead, $activities, $emp
 */
$l = $selected_lead;
?>
<div class="lead-detail">
    <div class="lead-detail-header">
        <a href="dashboard.php<?= isset($status_filter) ? '?status=' . urlencode($status_filter) : '' ?>" class="btn btn-sm btn-outline">← Back</a>
        <div class="lead-detail-title">
            <h2><?= e($l['business_name']) ?></h2>
            <?= tier_badge($l['lead_tier']) ?>
            <?= status_badge($l['crm_status'] ?? 'new') ?>
        </div>
        <div class="lead-detail-actions">
            <!-- Instant call buttons -->
            <?php if (is_valid_phone($l['phone_primary'])): ?>
                <a href="tel:<?= e($l['phone_primary']) ?>" class="btn btn-sm btn-call" title="Call">📞 Call</a>
            <?php endif; ?>
            <?php if ($l['whatsapp']): ?>
                <a href="https://wa.me/<?= e(preg_replace('/\D/', '', $l['whatsapp'])) ?>" target="_blank" class="btn btn-sm btn-wa" title="WhatsApp">💬 WhatsApp</a>
            <?php endif; ?>
            <?php if ($l['wa_link']): ?>
                <a href="<?= e($l['wa_link']) ?>" target="_blank" class="btn btn-sm btn-wa" title="Pre-written Message">📨 WA Message</a>
            <?php endif; ?>
            <!-- Training shortcut -->
            <a href="../cold-call-training.html" target="_blank" class="btn btn-sm btn-training">🎯 Training</a>
        </div>
    </div>

    <div class="lead-detail-grid">
        <!-- Left column: lead info -->
        <div class="detail-section">
            <h3>Business Information</h3>
            <table class="detail-table">
                <tr><td>Category</td><td><?= e($l['category']) ?></td></tr>
                <tr><td>Owner</td><td><?= e($l['owner_name'] ?: '—') ?></td></tr>
                <tr><td>Phone</td><td><?= e($l['phone_primary'] ?: '—') ?></td></tr>
                <tr><td>Secondary</td><td><?= e($l['phone_secondary'] ?: '—') ?></td></tr>
                <tr><td>WhatsApp</td><td><?= e($l['whatsapp'] ?: '—') ?></td></tr>
                <tr><td>Email</td><td><?= $l['email'] ? '<a href="mailto:' . e($l['email']) . '">' . e($l['email']) . '</a>' : '—' ?></td></tr>
                <tr><td>Address</td><td><?= e($l['address'] ?: '—') ?></td></tr>
                <tr><td>City</td><td><?= e($l['city'] ?: '—') ?></td></tr>
                <tr><td>Pincode</td><td><?= e($l['pincode'] ?: '—') ?></td></tr>
                <tr><td>Region</td><td><?= e($l['region'] ?: '—') ?> / <?= e($l['country'] ?: '—') ?></td></tr>
            </table>
        </div>

        <div class="detail-section">
            <h3>Online Presence</h3>
            <table class="detail-table">
                <tr><td>Website</td><td>
                    <?php if ($l['website_url']): ?>
                        <a href="<?= e($l['website_url']) ?>" target="_blank"><?= e(truncate($l['website_url'], 50)) ?></a>
                    <?php else: ?>
                        <span class="text-danger">No website</span>
                    <?php endif; ?>
                </td></tr>
                <tr><td>Website Quality</td><td><?= e(ucfirst(str_replace('_', ' ', $l['website_quality'] ?? 'none'))) ?></td></tr>
                <tr><td>Rating</td><td>⭐ <?= e($l['rating'] ?? '—') ?> / 5 (<?= e($l['review_count'] ?? 0) ?> reviews)</td></tr>
                <tr><td>Years in Business</td><td><?= e($l['years_in_business'] ?: '—') ?></td></tr>
                <tr><td>Socials</td><td><?= e($l['socials'] ?: '—') ?></td></tr>
                <tr><td>Contact Channel</td><td><?= e(ucfirst($l['contact_channel'] ?: '—')) ?></td></tr>
                <tr><td>Source</td><td><?= e($l['source'] ?: '—') ?></td></tr>
            </table>
        </div>

        <!-- Right column: CRM info -->
        <div class="detail-section">
            <h3>Pain Points</h3>
            <div class="pain-points-box">
                <?php if ($l['pain_points']): ?>
                    <?php foreach (explode(' | ', $l['pain_points']) as $pp): ?>
                        <div class="pain-point">⚠️ <?= e($pp) ?></div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <p class="text-muted">No pain points identified.</p>
                <?php endif; ?>
            </div>
        </div>

        <div class="detail-section">
            <h3>Recommended Pitch</h3>
            <div class="pitch-box">
                <?php if ($l['recommended_pitch']): ?>
                    <?php foreach (explode(' | ', $l['recommended_pitch']) as $i => $part): ?>
                        <p class="pitch-line"><?= $i === 0 ? '🎯' : '📌' ?> <?= e($part) ?></p>
                    <?php endforeach; ?>
                <?php else: ?>
                    <p class="text-muted">No pitch recommendation available.</p>
                <?php endif; ?>
            </div>
        </div>

        <div class="detail-section">
            <h3>Lead Score</h3>
            <div class="score-bar">
                <div class="score-fill" style="width: <?= min(100, (int)$l['lead_score']) ?>%">
                    <?= (int)$l['lead_score'] ?>/100
                </div>
            </div>
            <div class="score-meta">
                <span>Tier: <?= e($l['lead_tier']) ?></span>
                <span>Assigned: <?= e($l['assigned_employee'] ?: 'Unassigned') ?></span>
                <span>Fetched: <?= fmt_datetime($l['data_fetched_at']) ?></span>
            </div>
        </div>

        <div class="detail-section">
            <h3>Proposals</h3>
            <table class="detail-table">
                <?php if ($l['sample_site_url']): ?>
                <tr><td>Sample Site</td><td><a href="<?= e($l['sample_site_url']) ?>" target="_blank">View →</a></td></tr>
                <?php endif; ?>
                <?php if ($l['pitch_deck_url']): ?>
                <tr><td>Pitch Deck</td><td><a href="<?= e($l['pitch_deck_url']) ?>" target="_blank">View →</a></td></tr>
                <?php endif; ?>
            </table>
        </div>

        <div class="detail-section">
            <h3>Notes</h3>
            <div class="notes-box">
                <?php if ($l['notes']): ?>
                    <p><?= e($l['notes']) ?></p>
                <?php endif; ?>
                <?php if ($l['crm_notes']): ?>
                    <hr class="notes-divider">
                    <p class="text-muted">CRM Notes:</p>
                    <p><?= nl2br(e($l['crm_notes'])) ?></p>
                <?php endif; ?>
                <?php if (!$l['notes'] && !$l['crm_notes']): ?>
                    <p class="text-muted">No notes yet.</p>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- Actions bar -->
    <div class="actions-bar">
        <form method="post" action="api/leads.php" class="inline-form">
            <input type="hidden" name="action" value="tag">
            <input type="hidden" name="lead_key" value="<?= e($l['lead_key']) ?>">
            <input type="hidden" name="status" value="qualified">
            <button type="submit" class="btn btn-qualified" onclick="return confirm('Mark as Qualified?')">✅ Qualified</button>
        </form>
        <form method="post" action="api/leads.php" class="inline-form">
            <input type="hidden" name="action" value="tag">
            <input type="hidden" name="lead_key" value="<?= e($l['lead_key']) ?>">
            <input type="hidden" name="status" value="callback">
            <button type="submit" class="btn btn-callback">📅 Callback Pending</button>
        </form>
        <form method="post" action="api/leads.php" class="inline-form">
            <input type="hidden" name="action" value="tag">
            <input type="hidden" name="lead_key" value="<?= e($l['lead_key']) ?>">
            <input type="hidden" name="status" value="not_qualified">
            <button type="submit" class="btn btn-notqualified" onclick="return confirm('Mark as Not Qualified? This will archive the lead in 24h.')">❌ Not Qualified</button>
        </form>
    </div>

    <!-- Add note form -->
    <div class="add-note-section">
        <h3>Add Note</h3>
        <form method="post" action="api/leads.php" class="note-form" onsubmit="submitNote(event)">
            <input type="hidden" name="action" value="note">
            <input type="hidden" name="lead_key" value="<?= e($l['lead_key']) ?>">
            <textarea name="note" class="form-control" rows="3" placeholder="Enter call notes, conversation summary, next steps..." required></textarea>
            <button type="submit" class="btn btn-primary">Save Note</button>
        </form>
    </div>

    <!-- Activity log -->
    <div class="activity-section">
        <h3>Activity Log</h3>
        <?php if (empty($activities)): ?>
            <p class="text-muted">No activity yet.</p>
        <?php else: ?>
            <div class="activity-timeline">
                <?php foreach ($activities as $a): ?>
                    <div class="activity-item">
                        <div class="activity-icon">
                            <?= match ($a['action']) {
                                'tagged' => '🏷️',
                                'note'   => '📝',
                                'called' => '📞',
                                default  => '📌',
                            } ?>
                        </div>
                        <div class="activity-body">
                            <div class="activity-header">
                                <strong><?= e($a['employee_name'] ?? 'System') ?></strong>
                                <span class="text-muted"><?= time_ago($a['created_at']) ?></span>
                            </div>
                            <div class="activity-text">
                                <?php if ($a['action'] === 'tagged'): ?>
                                    Changed status from <strong><?= e($a['old_value'] ?? 'new') ?></strong>
                                    to <strong><?= e($a['new_value']) ?></strong>
                                <?php elseif ($a['action'] === 'note'): ?>
                                    Added note: <?= e(truncate($a['description'], 200)) ?>
                                <?php elseif ($a['action'] === 'called'): ?>
                                    Marked as contacted
                                <?php else: ?>
                                    <?= e($a['description']) ?>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
</div>