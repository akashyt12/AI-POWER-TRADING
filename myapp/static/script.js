let trendChart;

async function fetchData() {
  try {
    const res = await fetch("/fetch");
    const data = await res.json();

    const prediction = data.prediction;
    const numberEl = document.getElementById("predicted-number");
    const colorEl = document.getElementById("predicted-color");
    const confidenceEl = document.getElementById("predicted-confidence");
    const boxEl = document.getElementById("prediction-box");
    const confBar = document.getElementById("confidence-bar");

    const conf = prediction.confidence || 0;
    const predColor = prediction.color || "--";

    // Update prediction box and number
    numberEl.innerText = prediction.next !== null ? prediction.next : "--";
    colorEl.innerText = predColor;
    confidenceEl.innerText = "Confidence: " + (conf*100).toFixed(1) + "%";

    if(conf >= 0.8){
      boxEl.className = "prediction-box high";
      colorEl.className = "green";
      confBar.style.background = "#00ff88";
      numberEl.style.fontSize = "4.5em";
    } else if(conf >= 0.5){
      boxEl.className = "prediction-box medium";
      colorEl.className = "green";
      confBar.style.background = "#ffaa00";
      numberEl.style.fontSize = "4em";
    } else {
      boxEl.className = "prediction-box low";
      colorEl.className = "red";
      confBar.style.background = "#ff4d4d";
      numberEl.style.fontSize = "3.5em";
    }

    confBar.style.width = (conf*100) + "%";

    // Update History Table
    const tbody = document.querySelector("#history-table tbody");
    tbody.innerHTML = "";
    data.history.slice().reverse().forEach((num, idx) => {
      const bigSmall = num >=5 ? 'big' : 'small';
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${idx + 1}</td>
        <td>${num}</td>
        <td class="${num % 2 === 0 ? 'red' : 'green'}">${num %2===0?'RED':'GREEN'}</td>
        <td class="${bigSmall}">${bigSmall.toUpperCase()}</td>
      `;
      tbody.appendChild(row);
    });

    // Update Trend Chart (Big/Small + Red/Green combined)
    const trendLabels = data.history.slice(-10).map((_, i) => i+1);
    const trendData = data.history.slice(-10).map(n => {
      // Combine color + size in numeric
      // RED=0, GREEN=1; SMALL=0, BIG=1 => value 0-3
      const colorVal = n%2===0?0:1;
      const sizeVal = n>=5?1:0;
      return colorVal + sizeVal*2; // 0-3
    });

    if(trendChart){
      trendChart.data.labels = trendLabels;
      trendChart.data.datasets[0].data = trendData;
      trendChart.update();
    } else {
      const ctx = document.getElementById('trend-chart').getContext('2d');
      trendChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: trendLabels,
          datasets: [{
            label: 'Trend (0=R-S,1=G-S,2=R-B,3=G-B)',
            data: trendData,
            backgroundColor: 'rgba(0,255,136,0.2)',
            borderColor: 'rgba(0,255,136,1)',
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: true,
            cubicInterpolationMode: 'monotone'
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: true }},
          scales: {
            y: {
              min: 0,
              max: 3,
              ticks: {
                callback: function(value){
                  switch(value){
                    case 0: return 'RED-S';
                    case 1: return 'GREEN-S';
                    case 2: return 'RED-B';
                    case 3: return 'GREEN-B';
                  }
                }
              }
            }
          }
        }
      });
    }

  } catch (err) {
    console.error("Fetch error:", err);
  }
}

// Auto refresh every 5 sec
setInterval(fetchData, 5000);
fetchData();
