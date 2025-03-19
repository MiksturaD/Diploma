console.log("nps-chart.js loaded");

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM loaded in nps-chart.js");

    console.log("Checking for Chart.js...");
    if (typeof Chart === 'undefined') {
        console.error("Chart.js is not loaded!");
        return;
    }
    console.log("Chart.js is loaded, proceeding...");

    const ctx = document.getElementById('npsGauge');
    if (!ctx) {
        console.error("Canvas element 'npsGauge' not found!");
        return;
    }
    console.log("Canvas element found, initializing chart...");

    console.log("npsValue from window:", window.npsValue);
    const npsValue = window.npsValue || 0;
    console.log("Using npsValue:", npsValue);

    try {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [100, 100, 100],
                    backgroundColor: [
                        'rgba(255, 111, 97, 0.8)', // Красный
                        'rgba(255, 215, 0, 0.8)',  // Жёлтый
                        'rgba(76, 175, 80, 0.8)'   // Зелёный
                    ],
                    borderWidth: 2,
                    borderColor: '#495057',
                    circumference: 180,
                    rotation: 270,
                }]
            },
            options: {
                cutout: '70%',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuad'
                },
                elements: {
                    arc: {
                        borderWidth: 2,
                        borderColor: '#495057',
                        shadowColor: 'rgba(0, 0, 0, 0.3)',
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowOffsetY: 4
                    }
                }
            },
            plugins: [{
                id: 'gaugeNeedle',
                afterDatasetsDraw(chart) {
                    console.log("Drawing gauge needle...");
                    try {
                        const { ctx, chartArea: { width, height } } = chart;
                        ctx.save();
                        console.log("Needle value:", npsValue);
                        const needleValue = npsValue;
                        const angle = (needleValue + 100) * (180 / 200); // Угол для стрелки
                        console.log("Angle:", angle);
                        const centerX = width / 2;
                        const centerY = height;
                        const radius = width / 3; // Уменьшаем радиус для компактности
                        console.log("Center X:", centerX, "Center Y:", centerY, "Radius:", radius);

                        // Рисуем деления и метки
                        for (let i = 0; i <= 10; i++) {
                            const tickAngle = (i * 18) * (Math.PI / 180);
                            const tickLength = i % 5 === 0 ? 12 : 6;
                            const tickStart = radius * 0.75; // Деления ближе к центру
                            const tickEnd = tickStart + tickLength;
                            ctx.beginPath();
                            ctx.strokeStyle = '#fff';
                            ctx.lineWidth = 2;
                            ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
                            ctx.shadowBlur = 5;
                            ctx.moveTo(
                                centerX + tickStart * Math.cos(tickAngle),
                                centerY - tickStart * Math.sin(tickAngle)
                            );
                            ctx.lineTo(
                                centerX + tickEnd * Math.cos(tickAngle),
                                centerY - tickEnd * Math.sin(tickAngle)
                            );
                            ctx.stroke();
                            ctx.closePath();

                            // Метки (-100, -50, 0, 50, 100)
                            if (i % 5 === 0) {
                                const label = (i * 20) - 100;
                                const labelRadius = radius * 0.6; // Метки внутри полукруга
                                ctx.font = 'bold 14px Arial';
                                ctx.fillStyle = '#fff';
                                ctx.textAlign = 'center';
                                ctx.fillText(
                                    label,
                                    centerX + labelRadius * Math.cos(tickAngle),
                                    centerY - labelRadius * Math.sin(tickAngle) + 5
                                );

                                // Смайлы под -100 и +100
                                if (label === -100) {
                                    ctx.font = '20px Arial';
                                    ctx.fillText(
                                        '😡',
                                        centerX + labelRadius * Math.cos(tickAngle),
                                        centerY - labelRadius * Math.sin(tickAngle) + 25
                                    );
                                } else if (label === 100) {
                                    ctx.font = '20px Arial';
                                    ctx.fillText(
                                        '😊',
                                        centerX + labelRadius * Math.cos(tickAngle),
                                        centerY - labelRadius * Math.sin(tickAngle) + 25
                                    );
                                }
                            }
                        }

                        // Рисуем стрелку
                        ctx.translate(centerX, centerY);
                        ctx.rotate((angle * Math.PI) / 180);
                        ctx.beginPath();
                        ctx.moveTo(0, -5);
                        ctx.lineTo(radius * 0.9, 0); // Стрелка чуть короче радиуса
                        ctx.lineTo(0, 5);
                        ctx.fillStyle = '#00b7eb'; // Ярко-голубой цвет
                        ctx.fill();
                        ctx.closePath();

                        // Центральный круг
                        ctx.beginPath();
                        ctx.arc(0, 0, 10, 0, 2 * Math.PI);
                        ctx.fillStyle = '#343a40';
                        ctx.fill();
                        ctx.strokeStyle = '#00b7eb';
                        ctx.stroke();
                        ctx.closePath();

                        // Отображаем значение NPS рядом со стрелкой
                        ctx.rotate(-(angle * Math.PI) / 180);
                        ctx.font = 'bold 14px Arial';
                        ctx.fillStyle = '#fff';
                        ctx.textAlign = 'center';
                        const valueRadius = radius * 1.1; // Чуть дальше стрелки
                        const valueAngle = (angle * Math.PI) / 180;
                        ctx.fillText(
                            npsValue.toFixed(1),
                            valueRadius * Math.cos(valueAngle),
                            -valueRadius * Math.sin(valueAngle) + 5
                        );

                        // Текст "NPS" в центре
                        ctx.font = 'bold 16px Arial';
                        ctx.fillStyle = '#fff';
                        ctx.textAlign = 'center';
                        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
                        ctx.shadowBlur = 5;
                        ctx.fillText('NPS', 0, 5);
                        ctx.restore();
                        console.log("Gauge needle drawn successfully");
                    } catch (e) {
                        console.error("Error in gaugeNeedle:", e);
                    }
                }
            }]
        });
        console.log("Chart initialized successfully");
    } catch (e) {
        console.error("Error initializing chart:", e);
    }
});