/* ── CONZURA RMS — Dashboard JS ── */
document.addEventListener('DOMContentLoaded', function () {
  fetch('/api/dashboard-stats')
    .then(r => r.json())
    .then(data => {
      const ctx = document.getElementById('revenueChart');
      if (!ctx) return;
      new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
          labels: data.labels.length ? data.labels : ['No data'],
          datasets: [{
            label: 'Revenue (₹)',
            data: data.values.length ? data.values : [0],
            backgroundColor: 'rgba(212,168,83,0.3)',
            borderColor: '#d4a853',
            borderWidth: 2,
            borderRadius: 8,
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#7a7a8c' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#7a7a8c', callback: v => '₹' + v } }
          }
        }
      });
    });
});
