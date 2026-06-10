/* ── CONZURA RMS — Orders JS ── */
document.addEventListener('DOMContentLoaded', function () {
  // ── Order Search ──
  const searchInput = document.getElementById('orderSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const q = this.value.toLowerCase().trim();
      document.querySelectorAll('.order-row').forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = (!q || text.includes(q)) ? '' : 'none';
      });
    });
  }

  // Status filter
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const s = btn.dataset.status;
      document.querySelectorAll('.order-row').forEach(r => {
        r.style.display = (s === 'all' || r.dataset.status === s) ? '' : 'none';
      });
    });
  });

  // Live status update
  document.querySelectorAll('.status-select').forEach(sel => {
    sel.addEventListener('change', function () {
      fetch('/orders/update-status/' + this.dataset.id, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'status=' + this.value
      }).then(r => r.json()).then(d => {
        if (d.success) this.closest('tr').dataset.status = this.value;
      });
    });
  });

  // Estimated total
  document.getElementById('orderItems').addEventListener('change', updateTotal);
  document.getElementById('orderItems').addEventListener('input', updateTotal);
});

function addItemRow() {
  const container = document.getElementById('orderItems');
  const clone = container.querySelector('.order-item-row').cloneNode(true);
  clone.querySelectorAll('input').forEach(i => { if (i.type === 'number') i.value = '1'; else i.value = ''; });
  clone.querySelector('select').value = '';
  container.appendChild(clone);
  updateTotal();
}

function updateTotal() {
  let total = 0;
  document.querySelectorAll('.order-item-row').forEach(row => {
    const sel = row.querySelector('.item-select');
    const qty = parseInt(row.querySelector('.qty-input').value) || 0;
    if (sel.value) total += (parseFloat(sel.options[sel.selectedIndex].dataset.price) || 0) * qty;
  });
  document.getElementById('estTotal').textContent = '₹' + total.toFixed(0);
}

function generateBill(orderId) {
  document.getElementById('billOrderId').value = orderId;
  document.getElementById('billModal').classList.add('open');
}

document.addEventListener('DOMContentLoaded', function () {
  const confirmBtn = document.getElementById('confirmBillBtn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', function () {
      const orderId  = document.getElementById('billOrderId').value;
      const discount = document.getElementById('billDiscount').value || 0;
      const payment  = document.getElementById('billPayment').value;
      const form = document.getElementById('bill-form-' + orderId);
      form.querySelector('[name="discount"]').value = discount;
      form.querySelector('[name="payment_method"]').value = payment;
      form.submit();
    });
  }
});

function viewOrder(id) {
  document.getElementById('viewOrderModal').classList.add('open');
  document.getElementById('viewOrderBody').innerHTML =
    '<div style="text-align:center;padding:20px;color:var(--muted);"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
  fetch('/orders/view/' + id).then(r => r.json()).then(data => {
    const o = data.order;
    let html = `<div style="margin-bottom:16px;"><strong style="color:var(--gold);">Order #${o.id}</strong> — Table ${o.table_number}</div>`;
    html += `<table style="width:100%;margin-bottom:16px;"><thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead><tbody>`;
    let sub = 0;
    data.items.forEach(item => {
      const t = item.quantity * item.unit_price; sub += t;
      html += `<tr><td>${item.name}</td><td>${item.quantity}</td><td>₹${item.unit_price}</td><td style="color:var(--gold);">₹${t.toFixed(0)}</td></tr>`;
    });
    html += `</tbody></table>`;
    if (data.bill) {
      html += `<div style="background:var(--surface2);border-radius:10px;padding:16px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;"><span>Subtotal</span><span>₹${data.bill.subtotal.toFixed(2)}</span></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;"><span>Tax (5%)</span><span>₹${data.bill.tax_amount.toFixed(2)}</span></div>
        <div style="display:flex;justify-content:space-between;font-size:16px;font-weight:700;color:var(--gold);border-top:1px solid var(--border);padding-top:10px;"><span>Total</span><span>₹${data.bill.total_amount.toFixed(2)}</span></div>
      </div>`;
    } else {
      html += `<div style="color:var(--muted);font-size:13px;text-align:center;margin-top:10px;">Subtotal: ₹${sub.toFixed(2)} | Bill not generated</div>`;
    }
    document.getElementById('viewOrderTitle').textContent = 'Order #' + id;
    document.getElementById('viewOrderBody').innerHTML = html;
  });
}
