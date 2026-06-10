/* ── CONZURA RMS — Inventory JS ── */
function openEdit(id, name, cat, qty, unit, min, cost, supplier) {
  document.getElementById('editForm').action = '/inventory/update/' + id;
  document.getElementById('eName').value     = name;
  document.getElementById('eCat').value      = cat;
  document.getElementById('eQty').value      = qty;
  document.getElementById('eUnit').value     = unit;
  document.getElementById('eMin').value      = min;
  document.getElementById('eCost').value     = cost;
  document.getElementById('eSupplier').value = supplier;
  document.getElementById('editModal').classList.add('open');
}
