/**
 * TKVibes CRM — JavaScript
 */
(function() {
    'use strict';

    // ── Flash messages auto-dismiss ──────────────────────────────────────
    document.querySelectorAll('.alert').forEach(function(el) {
        setTimeout(function() { el.style.opacity = '0'; el.style.transition = 'opacity 0.5s'; }, 5000);
        setTimeout(function() { el.remove(); }, 5500);
    });

    // ── Submit note via AJAX ─────────────────────────────────────────────
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
                // Reload to show the new note
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

    // ── Tag action via AJAX ─────────────────────────────────────────────
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

    // ── Keyboard shortcuts ──────────────────────────────────────────────
    document.addEventListener('keydown', function(e) {
        // Escape → close modals
        if (e.key === 'Escape') {
            var modals = document.querySelectorAll('.modal');
            modals.forEach(function(m) { m.style.display = 'none'; });
        }
        // Ctrl+Shift+T → open training (on dashboard)
        if (e.ctrlKey && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            var trainingBtn = document.querySelector('.btn-training');
            if (trainingBtn) trainingBtn.click();
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

})();