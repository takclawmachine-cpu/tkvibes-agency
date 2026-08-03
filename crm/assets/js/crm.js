/**
 * TKVibes CRM — JavaScript
 */
(function() {
    'use strict';

    var leadKey = null;
    var editMode = false;
    var changedFields = {};

    // ── Detect lead_key from page ──────────────────────────────────────
    (function() {
        var h = document.querySelector('input[name="lead_key"]');
        if (h) leadKey = h.value;
    })();

    // ── Flash messages auto-dismiss ─────────────────────────────────────
    document.querySelectorAll('.alert').forEach(function(el) {
        setTimeout(function() { el.style.opacity = '0'; el.style.transition = 'opacity 0.5s'; }, 5000);
        setTimeout(function() { el.remove(); }, 5500);
    });

    // ── Submit note via AJAX ────────────────────────────────────────────
    window.submitNote = function(e) {
        e.preventDefault();
        var form = e.target;
        var data = new FormData(form);
        var btn = form.querySelector('button');
        btn.disabled = true;
        btn.textContent = 'Saving...';

        fetch('api/leads.php', {
            method: 'POST',
            body: data
        })
        .then(function(r) { return r.json(); })
        .then(function(result) {
            if (result.status === 'ok') {
                form.querySelector('textarea').value = '';
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
                btn.disabled = false;
                btn.textContent = 'Save Note';
            }
        })
        .catch(function(err) {
            alert('Network error: ' + err.message);
            btn.disabled = false;
            btn.textContent = 'Save Note';
        });
    };

    // ── Tag action via AJAX ────────────────────────────────────────────
    document.querySelectorAll('.actions-bar form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var data = new FormData(form);
            var btn = form.querySelector('button');
            var original = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Processing...';

            fetch('api/leads.php', {
                method: 'POST',
                body: data
            })
            .then(function(r) { return r.json(); })
            .then(function(result) {
                if (result.status === 'ok') {
                    location.reload();
                } else {
                    alert('Error: ' + (result.error || 'Unknown'));
                    btn.disabled = false;
                    btn.textContent = original;
                }
            })
            .catch(function(err) {
                alert('Network error: ' + err.message);
                btn.disabled = false;
                btn.textContent = original;
            });
        });
    });

    // ── Inline Edit Mode ──────────────────────────────────────────────

    /**
     * Toggle edit mode on/off
     */
    window.toggleEditMode = function() {
        editMode = !editMode;
        changedFields = {};

        var btn = document.getElementById('editToggleBtn');
        var bar = document.getElementById('editActionsBar');

        if (editMode) {
            btn.textContent = '✏️ Editing...';
            btn.classList.add('btn-active');
            bar.style.display = 'flex';
            document.querySelectorAll('.edit-cell').forEach(function(cell) { makeEditable(cell); });
        } else {
            btn.textContent = '✏ Edit';
            btn.classList.remove('btn-active');
            bar.style.display = 'none';
            document.getElementById('editStatus').textContent = '';
            document.querySelectorAll('.edit-cell').forEach(function(cell) { makeReadonly(cell); });
        }
    };

    /**
     * Convert a display cell into an editable input/textarea
     */
    function makeEditable(cell) {
        var field = cell.getAttribute('data-field');
        if (!field) return;

        var currentText = cell.textContent.trim();
        if (currentText === '—' || currentText === 'none') currentText = '';

        var input;
        var isLongText = currentText.length > 60 || cell.classList.contains('pain-points-box') || cell.classList.contains('pitch-box') || cell.classList.contains('notes-box');

        if (isLongText) {
            input = document.createElement('textarea');
            input.className = 'form-control edit-input';
            input.rows = 3;
            // Unformat pain points / pitch (join with | )
            input.value = currentText;
            // For pain points display, they show as warnings separated by newlines
            // but the DB stores them as pipe-separated
            if (cell.classList.contains('pain-points-box')) {
                input.value = currentText;
            }
            if (cell.classList.contains('pitch-box')) {
                input.value = currentText;
            }
        } else {
            input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control edit-input';

            if (field === 'rating' || field === 'review_count') {
                input.type = 'number';
                input.step = field === 'rating' ? '0.1' : '1';
            }
            if (field === 'has_website') {
                input.type = 'number';
                input.min = 0;
                input.max = 1;
                input.step = 1;
            }
        }

        input.dataset.field = field;
        input.dataset.original = currentText;
        input.value = currentText;
        input.style.width = '100%';
        input.style.boxSizing = 'border-box';

        input.addEventListener('input', function() {
            var orig = this.dataset.original;
            var val = this.value;
            if (val !== orig) {
                changedFields[field] = val;
            } else {
                delete changedFields[field];
            }
            updateSaveStatus();
        });

        cell.innerHTML = '';
        cell.appendChild(input);
        input.focus();
    }

    /**
     * Restore a cell to readonly display
     */
    function makeReadonly(cell) {
        var field = cell.getAttribute('data-field');
        if (!field) return;

        var input = cell.querySelector('.edit-input');
        if (!input) return;

        // Restore the original value display
        var val = input.dataset.original || input.value;
        cell.innerHTML = escapeHtml(val || '—');
    }

    /**
     * Save all changed fields via AJAX
     */
    window.saveAllEdits = function() {
        // Collect latest values from DOM inputs
        document.querySelectorAll('.edit-input').forEach(function(inp) {
            var field = inp.dataset.field;
            var orig = inp.dataset.original;
            var val = inp.value;
            if (val !== orig) {
                changedFields[field] = val;
            } else {
                delete changedFields[field];
            }
        });

        var fields = Object.keys(changedFields);
        if (fields.length === 0) {
            document.getElementById('editStatus').textContent = 'No changes to save.';
            return;
        }

        var statusEl = document.getElementById('editStatus');
        statusEl.textContent = 'Saving ' + fields.length + ' field(s)...';

        // Save fields sequentially
        var saveNext = function(index) {
            if (index >= fields.length) {
                statusEl.textContent = 'All saved! Reloading...';
                setTimeout(function() { location.reload(); }, 600);
                return;
            }

            var field = fields[index];
            var value = changedFields[field];

            fetch('api/leads.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
                body: 'action=update&lead_key=' + encodeURIComponent(leadKey) +
                      '&field=' + encodeURIComponent(field) +
                      '&value=' + encodeURIComponent(value)
            })
            .then(function(r) { return r.json(); })
            .then(function(result) {
                if (result.status === 'ok') {
                    statusEl.textContent = '✓ ' + field + ' saved (' + (index + 1) + '/' + fields.length + ')';
                    saveNext(index + 1);
                } else {
                    statusEl.textContent = '✗ Error on ' + field + ': ' + (result.error || 'Unknown');
                }
            })
            .catch(function(err) {
                statusEl.textContent = '✗ Network error on ' + field + ': ' + err.message;
            });
        };

        saveNext(0);
    };

    function updateSaveStatus() {
        var count = Object.keys(changedFields).length;
        var el = document.getElementById('editStatus');
        if (count > 0) {
            el.textContent = count + ' field(s) changed';
        } else {
            el.textContent = '';
        }
    }

    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // ── Keyboard shortcuts ─────────────────────────────────────────────
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (editMode) {
                toggleEditMode();
                return;
            }
            var modals = document.querySelectorAll('.modal');
            modals.forEach(function(m) { m.style.display = 'none'; });
        }
        if (e.ctrlKey && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            var trainingBtn = document.querySelector('.btn-training');
            if (trainingBtn) trainingBtn.click();
        }
        // Ctrl+Enter while editing → save
        if (e.ctrlKey && e.key === 'Enter' && editMode) {
            e.preventDefault();
            saveAllEdits();
        }
    });

    // ── Lead card click → open detail (on dashboard, already links) ────
    // Handled by <a> tags

    // ── Modal close on backdrop click ──────────────────────────────────
    document.querySelectorAll('.modal').forEach(function(m) {
        m.addEventListener('click', function(e) {
            if (e.target === m) m.style.display = 'none';
        });
    });

    // ── Proposal Generation ─────────────────────────────────
    window.generateProposal = function(lk) {
        var btn = document.querySelector('.btn-generate-proposal');
        if (!btn) return;
        btn.disabled = true;
        btn.textContent = '⏳ Starting...';
        
        fetch('api/proposals.php?action=generate&lead_key=' + encodeURIComponent(lk))
        .then(function(r) { return r.json(); })
        .then(function(result) {
            if (result.status === 'ok') {
                btn.textContent = '✅ Queued!';
                // Poll for status after delay
                setTimeout(function() { pollProposalStatus(lk); }, 2000);
            } else {
                alert('Error: ' + (result.error || 'Unknown'));
                btn.disabled = false;
                btn.textContent = '⚡ Generate Proposal';
            }
        })
        .catch(function(err) {
            alert('Network error: ' + err.message);
            btn.disabled = false;
            btn.textContent = '⚡ Generate Proposal';
        });
    };

    window.pollProposalStatus = function(lk) {
        fetch('api/proposals.php?action=status&lead_key=' + encodeURIComponent(lk))
        .then(function(r) { return r.json(); })
        .then(function(result) {
            if (result.status !== 'ok') return;
            var latest = result.jobs && result.jobs[0];
            if (!latest) return;
            
            var statusEl = document.getElementById('proposal-status-' + lk);
            if (!statusEl) return;
            
            if (latest.status === 'pending') {
                statusEl.innerHTML = '<span class="badge badge-callback">⏳ Queued</span>';
                setTimeout(function() { pollProposalStatus(lk); }, 5000);
            } else if (latest.status === 'running') {
                statusEl.innerHTML = '<span class="badge badge-callback">🔄 Generating...</span>';
                setTimeout(function() { pollProposalStatus(lk); }, 5000);
            } else if (latest.status === 'completed') {
                statusEl.innerHTML = '<span class="badge badge-qualified">✅ Done</span>';
                setTimeout(function() { location.reload(); }, 1000);
            } else if (latest.status === 'failed') {
                statusEl.innerHTML = '<span class="badge badge-notqualified">❌ Failed</span>';
            }
        })
        .catch(function() {
            // Retry on error
            setTimeout(function() { pollProposalStatus(lk); }, 10000);
        });
    };

    window.openFeedbackModal = function(lk) {
        document.getElementById('feedbackLeadKey').value = lk;
        document.getElementById('feedbackText').value = '';
        document.getElementById('feedbackModal').style.display = 'flex';
    };

    window.closeFeedbackModal = function() {
        document.getElementById('feedbackModal').style.display = 'none';
    };

    window.submitRegenerate = function() {
        var lk = document.getElementById('feedbackLeadKey').value;
        var fb = document.getElementById('feedbackText').value.trim();
        if (!fb) {
            alert('Please describe what needs improvement.');
            return;
        }
        
        var btn = document.querySelector('.btn-regenerate-proposal');
        if (btn) { btn.disabled = true; btn.textContent = '⏳ Submitting...'; }
        closeFeedbackModal();
        
        fetch('api/proposals.php?action=generate&lead_key=' + encodeURIComponent(lk) + '&feedback=' + encodeURIComponent(fb))
        .then(function(r) { return r.json(); })
        .then(function(result) {
            if (result.status === 'ok') {
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Unknown'));
                if (btn) { btn.disabled = false; btn.textContent = '🔄 Re-generate'; }
            }
        })
        .catch(function(err) {
            alert('Network error: ' + err.message);
            if (btn) { btn.disabled = false; btn.textContent = '🔄 Re-generate'; }
        });
    };

})();