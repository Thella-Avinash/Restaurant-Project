/* ── CONZURA RMS — Menu JS ── */
function openEdit(id, name, category, price, desc, available) {
  document.getElementById('editForm').action = '/menu/edit/' + id;
  document.getElementById('editName').value = name;
  document.getElementById('editCategory').value = category;
  document.getElementById('editPrice').value = price;
  document.getElementById('editDesc').value = desc;
  document.getElementById('editAvailable').value = available;
  document.getElementById('editModal').classList.add('open');
}

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.dataset.cat;
      document.querySelectorAll('.menu-row').forEach(row => {
        row.style.display = (cat === 'all' || row.dataset.cat === cat) ? '' : 'none';
      });
    });
  });
});
