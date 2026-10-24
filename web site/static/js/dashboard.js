/**
 * NutriSmart - Dashboard Chart.js Visualizations
 * Renders:
 * 1. 7-Day Daily Calorie Trend Chart (Line / Area with Goal comparison)
 * 2. Macronutrient Doughnut Chart (Protein, Carbs, Fat)
 * 3. Weekly Multi-Bar Nutrition Breakdown Chart
 */

document.addEventListener('DOMContentLoaded', function() {
    const dataElement = document.getElementById('chart-data');
    if (!dataElement) return;

    let chartData;
    try {
        chartData = JSON.parse(dataElement.textContent);
    } catch (e) {
        console.error("Failed to parse chart data:", e);
        return;
    }

    // Chart.js Default Typography
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = "#64748b";

    // ----------------------------------------------------
    // 1. Daily Calorie Chart (7-Day Trend vs Goal)
    // ----------------------------------------------------
    const calorieCtx = document.getElementById('dailyCalorieChart');
    if (calorieCtx) {
        new Chart(calorieCtx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Calories Consumed (kcal)',
                        data: chartData.calories,
                        backgroundColor: 'rgba(16, 185, 129, 0.12)',
                        borderColor: '#10b981',
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#10b981',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Daily Target Goal (kcal)',
                        data: chartData.calorie_goal,
                        borderColor: '#94a3b8',
                        borderWidth: 1.5,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        titleColor: '#ffffff',
                        bodyColor: '#e2e8f0',
                        padding: 10,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f1f5f9'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + ' kcal';
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // ----------------------------------------------------
    // 2. Macronutrient Doughnut Chart (Protein, Carbs, Fat)
    // ----------------------------------------------------
    const macroCtx = document.getElementById('macroDoughnutChart');
    if (macroCtx) {
        const p = chartData.today_macros.protein || 0;
        const c = chartData.today_macros.carbs || 0;
        const f = chartData.today_macros.fat || 0;

        const hasData = (p + c + f) > 0;
        const dataValues = hasData ? [p, c, f] : [1, 1, 1];
        const colors = hasData 
            ? ['#06b6d4', '#f59e0b', '#ef4444'] 
            : ['#e2e8f0', '#e2e8f0', '#e2e8f0'];

        new Chart(macroCtx, {
            type: 'doughnut',
            data: {
                labels: ['Protein (g)', 'Carbohydrates (g)', 'Healthy Fats (g)'],
                datasets: [{
                    data: dataValues,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (!hasData) return 'No meals logged today yet';
                                return ` ${context.label}: ${context.raw}g`;
                            }
                        }
                    }
                }
            }
        });
    }

    // ----------------------------------------------------
    // 3. Weekly Multi-Bar Nutrition Breakdown Chart
    // ----------------------------------------------------
    const weeklyCtx = document.getElementById('weeklyNutritionChart');
    if (weeklyCtx) {
        new Chart(weeklyCtx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Protein (g)',
                        data: chartData.protein,
                        backgroundColor: '#06b6d4',
                        borderRadius: 4
                    },
                    {
                        label: 'Carbohydrates (g)',
                        data: chartData.carbs,
                        backgroundColor: '#f59e0b',
                        borderRadius: 4
                    },
                    {
                        label: 'Healthy Fats (g)',
                        data: chartData.fat,
                        backgroundColor: '#ef4444',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        padding: 10,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f1f5f9'
                        },
                        ticks: {
                            callback: function(val) {
                                return val + 'g';
                            }
                        }
                    }
                }
            }
        });
    }
});

// ----------------------------------------------------
// 4. Real-Time Hydration Water Tracker Helpers
// ----------------------------------------------------
window.logWater = function(amount) {
    fetch('/api/water/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount_ml: amount })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const bar = document.getElementById('waterProgressBar');
            const txt = document.getElementById('currentWaterText');
            const pct = document.getElementById('waterPercentageText');
            if (bar) bar.style.width = data.percentage + '%';
            if (txt) txt.innerHTML = `<strong>${data.today_water_ml} ml</strong> consumed`;
            if (pct) pct.textContent = `${data.percentage}%`;
        }
    })
    .catch(err => console.error('Error logging water:', err));
};

window.resetWater = function() {
    if (!confirm("Reset today's water intake?")) return;
    fetch('/api/water/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const bar = document.getElementById('waterProgressBar');
            const txt = document.getElementById('currentWaterText');
            const pct = document.getElementById('waterPercentageText');
            if (bar) bar.style.width = '0%';
            if (txt) txt.innerHTML = `<strong>0 ml</strong> consumed`;
            if (pct) pct.textContent = '0%';
        }
    })
    .catch(err => console.error('Error resetting water:', err));
};
