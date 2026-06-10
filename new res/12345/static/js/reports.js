/* ── CONZURA RMS — Reports JS ── */
let lineChart, pieChart;

function loadChart(days) {
  fetch('/reports/api/chart-data?days=' + days)
    .then(r => r.json())
    .then(data => {
      if (lineChart) lineChart.destroy();
      lineChart = new Chart(document.getElementById('lineChart').getContext('2d'), {
        type: 'line',
        data: {
          labels: data.daily.labels.length ? data.daily.labels : ['No data'],
          datasets: [{
            label: 'Revenue (₹)', data: data.daily.values.length ? data.daily.values : [0],
            borderColor: '#d4a853', backgroundColor: 'rgba(212,168,83,0.1)',
            borderWidth: 2.5, fill: true, tension: 0.4,
            pointBackgroundColor: '#d4a853', pointRadius: 4,
          }]
        },
        options: {
          responsive: true, plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#7a7a8c', font: { size: 11 } } },
            y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#7a7a8c', callback: v => '₹' + v } }
          }
        }
      });

      if (pieChart) pieChart.destroy();
      pieChart = new Chart(document.getElementById('pieChart').getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: data.categories.labels.length ? data.categories.labels : ['No data'],
          datasets: [{
            data: data.categories.values.length ? data.categories.values : [1],
            backgroundColor: ['#d4a853','#4eca8b','#5b9ef7','#e85d5d','#a855f7','#f97316','#ec4899'],
            borderWidth: 0,
          }]
        },
        options: {
          responsive: true, cutout: '65%',
          plugins: { legend: { position: 'bottom', labels: { color: '#7a7a8c', padding: 14, font: { size: 12 } } } }
        }
      });
    });
}

document.addEventListener('DOMContentLoaded', () => loadChart(30));
