function getFilters() {
    return {
        start_date: document.getElementById("start-date").value,
        end_date: document.getElementById("end-date").value,
        payment_type: document.getElementById("payment-type").value,
        pickup_zone: document.getElementById("pickup-zone").value,
        dropoff_zone: document.getElementById("dropoff-zone").value,
    };
}

async function fetchWithFilters(endpoint) {

    const filters = getFilters();

    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
        if (value) {
            params.append(key, value);
        }
    });

    const url = `${endpoint}?${params.toString()}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
}

async function loadFilterOptions() {

    const response = await fetch("/api/filter-options");

    if (!response.ok) {
        throw new Error(
            `Filter API failed: ${response.status}`
        );
    }

    const data = await response.json();

    // Date filters
    const startDate = document.getElementById("start-date");
    const endDate = document.getElementById("end-date");

    startDate.min = data.min_date;
    startDate.max = data.max_date;
    startDate.value = data.min_date;

    endDate.min = data.min_date;
    endDate.max = data.max_date;
    endDate.value = data.max_date;


    // Payment types
    const paymentSelect =
        document.getElementById("payment-type");

    data.payment_types.forEach(paymentType => {

        const option = document.createElement("option");

        option.value = paymentType;
        option.textContent = paymentType;

        paymentSelect.appendChild(option);
    });


    // Pickup zones
    const pickupSelect =
        document.getElementById("pickup-zone");

    data.pickup_zones.forEach(zone => {

        const option = document.createElement("option");

        option.value = zone;
        option.textContent = `Zone ${zone}`;

        pickupSelect.appendChild(option);
    });


    // Dropoff zones
    const dropoffSelect =
        document.getElementById("dropoff-zone");

    data.dropoff_zones.forEach(zone => {

        const option = document.createElement("option");

        option.value = zone;
        option.textContent = `Zone ${zone}`;

        dropoffSelect.appendChild(option);
    });
}

async function loadKPIs() {

    const data = await fetchWithFilters(`/api/kpis`)

    document.getElementById("total-trips").textContent =
        data.total_trips.toLocaleString();

    document.getElementById("total-revenue").textContent =
        `$${Number(data.total_revenue).toLocaleString(undefined, {
            maximumFractionDigits: 2
        })}`;

    document.getElementById("avg-trip-amount").textContent =
        `$${Number(data.avg_trip_amount).toFixed(2)}`;

    document.getElementById("avg-trip-distance").textContent =
        `${Number(data.avg_trip_distance).toFixed(2)} mi`;
}

async function loadTripsByHour() {

    const data = await fetchWithFilters("/api/trips-by-hour");

    const chart = echarts.init(
        document.getElementById("trips-by-hour")
    );

    const hours = data.map(item => `${item.hour}:00`);
    const tripCounts = data.map(item => item.trip_count);

    const option = {
        grid: {
            left: "5%",
            right: "15%",
            top: "15%",
            bottom: "15%",
            containLabel: true
        },

        tooltip: {
            trigger: "axis"
        },

        xAxis: {
            type: "category",
            data: hours
        },

        yAxis: {
            type: "value",
            name: "Trips"
        },

        series: [
            {
                name: "Trips",
                type: "line",
                data: tripCounts,
                smooth: true
            }
        ]
    };

    chart.setOption(option);
}

async function loadTripsByDay() {

    const data = await fetchWithFilters("/api/trips-by-day");

    const chart = echarts.init(
        document.getElementById("trips-by-day")
    );

    const dates = data.map(item => item.date);
    const tripCounts = data.map(item => item.trip_count);

    const option = {
        grid: {
            left: "5%",
            right: "15%",
            top: "15%",
            bottom: "15%",
            containLabel: true
        },

        tooltip: {
            trigger: "axis"
        },

        xAxis: {
            type: "category",
            data: dates
        },

        yAxis: {
            type: "value",
            name: "Trips"
        },

        series: [
            {
                name: "Trips",
                type: "line",
                data: tripCounts,
                smooth: true
            }
        ]
    };

    chart.setOption(option);
}

async function loadPaymentStatus() {
    const data = await fetchWithFilters("/api/payment-analysis");

    const chart = echarts.init(
        document.getElementById("payment-analysis")
    );

    
    const paymentTypes = data.map(item => item.payment_type);
    const totalRevenues = data.map(item => item.total_revenue);
    const tripCounts = data.map(item => item.trip_count);

    const option = {
        grid: {
            left: "5%",
            right: "15%",
            top: "15%",
            bottom: "15%",
            containLabel: true
        },

        tooltip: {
            trigger: 'axis',
            axisPointer: {
            type: 'cross',
            crossStyle: {
                color: '#999'
            }
            }
        },
        toolbox: {
            feature: {
            dataView: { show: true, readOnly: false },
            magicType: { show: true, type: ['line', 'bar'] },
            restore: { show: true },
            saveAsImage: { show: true }
            }
        },
        legend: {
            data: ['Total Revenue', 'Trip Count']
        },
        xAxis: [
            {
                type: 'category',
                data: paymentTypes,
                axisPointer: {
                    type: 'shadow'
                },
                axisLabel: {
                    interval: 0
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: 'Total Revenue',
                axisLabel: {
                    formatter: function (value) {
                        return '$' + (value / 1000000).toFixed(0) + 'M';
                    }
                }
            },
            {
                type: 'value',
                name: 'Trip Count',
                axisLabel: {
                    formatter: function (value) {
                        return (value / 1000000).toFixed(2) + 'M';
                    }
                }
            },
        ],
        series: [
            {
            name: 'Total Revenue',
            type: 'bar',
            tooltip: {
                valueFormatter: function (value) {
                return '$' + value;
                }
            },
            data: totalRevenues
            },
            {
            name: 'Trip Count',
            type: 'line',
            yAxisIndex: 1,
            tooltip: {
                valueFormatter: function (value) {
                return value;
                }
            },
            data: tripCounts
            }
        ]
        };

    chart.setOption(option)
}

async function loadRevenueByDay() {
    const data = await fetchWithFilters("/api/revenue-by-day");

    const chart = echarts.init(
        document.getElementById("revenue-by-day")
    );

    const dates = data.map(item => item.date);
    const revenues = data.map(item => item.revenue);

    const option = {
        grid: {
            left: "5%",
            right: "15%",
            top: "15%",
            bottom: "15%",
            containLabel: true
        },

        tooltip: {
            trigger: "axis",
            valueFormatter: function (value) {
                return "$" + Number(value).toLocaleString();
            }
        },

        xAxis: {
            type: "category",
            data: dates,
            axisLabel: {
                interval: 0,
                rotate: 90
            }
        },

        yAxis: {
            type: "value",
            name: "Revenue",
            axisLabel: {
                formatter: function (value) {
                    return "$" + (value / 1000000).toFixed(1) + "M";
                }
            }
        },

        series: [
            {
                name: "Revenue",
                type: "line",
                data: revenues,
                smooth: true
            }
        ]
    };

    chart.setOption(option);

    window.addEventListener("resize", () => {
        chart.resize();
    });
}

async function loadRevenueByHour() {
    const data = await fetchWithFilters("/api/revenue-by-hour");

    const chart = echarts.init(
        document.getElementById("revenue-by-hour")
    );

    const hours = data.map(item => `${item.hour}:00`);
    const revenues = data.map(item => item.revenue);

    const option = {
        grid: {
            left: "5%",
            right: "15%",
            top: "15%",
            bottom: "15%",
            containLabel: true
        },

        tooltip: {
            trigger: "axis",
            valueFormatter: function (value) {
                return "$" + Number(value).toLocaleString();
            }
        },

        xAxis: {
            type: "category",
            data: hours,
            axisLabel: {
                interval: 0,
                rotate: 75
            }
        },

        yAxis: {
            type: "value",
            name: "Revenue",
            axisLabel: {
                formatter: function (value) {
                    const millions = value / 1000000;
                    return Number.isInteger(millions)
                        ? "$" + millions + "M"
                        : "$" + millions.toFixed(1) + "M";
                }
            }
        },

        series: [
            {
                name: "Revenue",
                type: "line",
                data: revenues,
                smooth: true
            }
        ]
    };

    chart.setOption(option);

    window.addEventListener("resize", () => {
        chart.resize();
    });
}

async function loadAvgRevenueByHour() {
    const data = await fetchWithFilters("/api/avg-revenue-by-hour");

    const chart = echarts.init(
        document.getElementById("avg-revenue-by-hour")
    );

    const hours = data.map(item => `${item.hour}:00`);
    const avgRevenue = data.map(item => item.avg_revenue);

    const option = {
        grid: {
            left: "5%",
            right: "15%",
            top: "15%",
            bottom: "15%",
            containLabel: true
        },

        tooltip: {
            trigger: "axis",
            valueFormatter: function (value) {
                return "$" + Number(value).toFixed(2);
            }
        },

        xAxis: {
            type: "category",
            data: hours,
            axisLabel: {
                interval: 0,
                rotate: 75
            }
        },

        yAxis: {
            type: "value",
            name: "Avg Revenue",
            axisLabel: {
                formatter: function (value) {
                    return "$" + value.toFixed(0);
                }
            }
        },

        series: [
            {
                name: "Avg Revenue",
                type: "line",
                data: avgRevenue,
                smooth: true
            }
        ]
    };

    chart.setOption(option);

    window.addEventListener("resize", () => {
        chart.resize();
    });
}

async function loadZoneRevenue(type) {

    const endpoint =
        type === "pickup"
            ? "/api/revenue-by-pickup-zone"
            : "/api/revenue-by-dropoff-zone";

    const data = await fetchWithFilters(endpoint);

    const locations = data.map(
        item => `Zone ${item.location_id}`
    );

    const revenues = data.map(
        item => item.revenue
    );

    const chart = echarts.getInstanceByDom(
        document.getElementById("zone-revenue-chart")
    ) || echarts.init(
        document.getElementById("zone-revenue-chart")
    );

    const option = {

        grid: {
            left: "15%",
            right: "15%",
            top: "15%",
            bottom: "15%",
            containLabel: true
        },

        tooltip: {
            trigger: "axis",
            axisPointer: {
                type: "shadow"
            },
            valueFormatter: function (value) {
                return "$" + Number(value).toLocaleString();
            }
        },

        xAxis: {
            type: "value",
            name: "Revenue",
            axisLabel: {
                formatter: function (value) {

                    const millions = value / 1000000;

                    return Number.isInteger(millions)
                        ? "$" + millions + "M"
                        : "$" + millions.toFixed(1) + "M";
                }
            }
        },

        yAxis: {
            type: "category",
            data: locations,
            inverse: true
        },

        series: [
            {
                name: "Revenue",
                type: "bar",
                data: revenues
            }
        ]
    };

    chart.setOption(option);
}

async function loadAIInsights() {
    const container = document.getElementById("ai-insights-content");

    container.innerHTML = `
        <div class="text-sm text-gray-500">
            Generating AI insights...
        </div>
    `;

    try {
        const data = await fetchWithFilters("/api/ai-insights");

        const insights = data.insights
            .split("\n")
            .filter(line => line.trim());

        const categoryStyles = {
            Demand: {
                icon: "📈",
                label: "Demand"
            },
            Revenue: {
                icon: "💰",
                label: "Revenue"
            },
            Payment: {
                icon: "💳",
                label: "Payment"
            },
            Location: {
                icon: "📍",
                label: "Location"
            }
        };

        container.innerHTML = insights.map(insight => {

            const separatorIndex = insight.indexOf(":");

            if (separatorIndex === -1) {
                return `
                    <div class="text-sm text-gray-700">
                        ${insight}
                    </div>
                `;
            }

            const category = insight
                .substring(0, separatorIndex)
                .trim();

            const message = insight
                .substring(separatorIndex + 1)
                .trim();

            const style = categoryStyles[category] || {
                icon: "🤖",
                label: category
            };

            return `
                <div class="border border-gray-100 rounded-lg p-3 bg-gray-50">

                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">
                            ${style.icon}
                        </span>

                        <span class="text-xs font-semibold text-gray-500 uppercase">
                            ${style.label}
                        </span>
                    </div>

                    <p class="text-sm text-gray-800">
                        ${message}
                    </p>

                </div>
            `;
        }).join("");

    } catch (error) {

        console.error("AI Insights Error:", error);

        container.innerHTML = `
            <div class="text-sm text-red-500">
                Unable to generate AI insights.
            </div>
        `;
    }
}

async function loadAIAnomalies() {

    const container = document.getElementById(
        "ai-anomalies-content"
    );

    container.innerHTML = `
        <div class="text-sm text-gray-500">
            Analyzing demand, revenue and distance patterns...
        </div>
    `;

    try {

        const data = await fetchWithFilters(
            "/api/ai-anomalies"
        );

        const categories = [
            {
                key: "demand",
                icon: "📈",
                title: "Demand",
                valueKey: "trip_count",
                unit: "trips"
            },
            {
                key: "revenue",
                icon: "💰",
                title: "Revenue",
                valueKey: "revenue",
                unit: "revenue"
            },
            {
                key: "distance",
                icon: "📏",
                title: "Trip Distance",
                valueKey: "avg_distance",
                unit: "miles"
            }
        ];

        let cards = "";

        categories.forEach(category => {

            const anomalies =
                data.anomalies[category.key] || [];

            anomalies.forEach(anomaly => {

                const isHigh =
                    anomaly.type === "high";

                const direction = isHigh ? "↑" : "↓";

                const label = isHigh
                    ? "Unusually High"
                    : "Unusually Low";

                let period = "";

                if (category.key === "revenue") {
                    period = anomaly.date;
                } else {
                    period =
                        `${String(anomaly.hour).padStart(2, "0")}:00`;
                }

                let value = anomaly[category.valueKey];

                if (category.key === "revenue") {
                    value =
                        "$" + Number(value).toLocaleString(
                            undefined,
                            {
                                maximumFractionDigits: 0
                            }
                        );
                } else if (
                    category.key === "distance"
                ) {
                    value =
                        Number(value).toFixed(2);
                } else {
                    value =
                        Number(value).toLocaleString();
                }

                cards += `
                    <div class="border border-gray-100 rounded-lg p-3 bg-gray-50">

                        <div class="flex items-center justify-between">

                            <div>

                                <div class="flex items-center gap-2">

                                    <span class="text-lg">
                                        ${category.icon}
                                    </span>

                                    <span class="text-xs font-semibold text-gray-500 uppercase">
                                        ${category.title}
                                    </span>

                                </div>

                                <p class="text-sm font-semibold text-gray-800 mt-1">
                                    ${period}
                                </p>

                            </div>

                            <div class="text-right">

                                <span class="text-lg">
                                    ${direction}
                                </span>

                                <p class="text-xs font-medium text-gray-500">
                                    ${label}
                                </p>

                                <p class="text-sm font-semibold text-gray-800">
                                    ${value}
                                    ${category.unit !== "revenue"
                                        ? " " + category.unit
                                        : ""}
                                </p>

                            </div>

                        </div>

                    </div>
                `;
            });
        });

        if (!cards) {

            container.innerHTML = `
                <div class="border border-gray-100 rounded-lg p-4 bg-gray-50">
                    <div class="flex items-center gap-2">
                        <span>✓</span>
                        <span class="text-sm font-medium text-gray-700">
                            No significant anomalies detected
                        </span>
                    </div>

                    <p class="text-xs text-gray-500 mt-1">
                        Demand, revenue and trip distance are
                        within their expected statistical ranges.
                    </p>
                </div>
            `;

            return;
        }

        container.innerHTML = `

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                ${cards}
            </div>

            <div class="mt-3 border border-gray-100 rounded-lg p-3 bg-gray-50">

                <p class="text-xs font-semibold text-gray-500 uppercase mb-1">
                    AI Analysis
                </p>

                <div class="text-sm text-gray-700 leading-relaxed">
                    ${data.explanation}
                </div>

            </div>
        `;
        
    } catch (error) {

        console.error(
            "AI Anomaly Detection Error:",
            error
        );

        container.innerHTML = `
            <div class="text-sm text-red-500">
                Unable to detect anomalies.
            </div>
        `;
    }
}

async function refreshDashboard() {

    await Promise.all([
        loadKPIs(),
        loadTripsByHour(),
        loadTripsByDay(),
        loadPaymentStatus(),
        loadRevenueByDay(),
        loadRevenueByHour(),
        loadAvgRevenueByHour(),
        loadZoneRevenue("pickup"),
        loadAIInsights(),
        loadAIAnomalies()
    ]);
}

async function initializeDashboard() {
    await loadFilterOptions();
    await refreshDashboard();
}

document
    .getElementById("pickup-zone-btn")
    .addEventListener("click", function () {

        document.getElementById("zone-chart-title").textContent =
            "Top 10 Pickup Zones by Revenue";

        loadZoneRevenue("pickup");

        this.classList.add("bg-gray-900", "text-white");
        this.classList.remove("bg-gray-200", "text-gray-700");

        document
            .getElementById("dropoff-zone-btn")
            .classList.remove("bg-gray-900", "text-white");

        document
            .getElementById("dropoff-zone-btn")
            .classList.add("bg-gray-200", "text-gray-700");
    });


document
    .getElementById("dropoff-zone-btn")
    .addEventListener("click", function () {

        document.getElementById("zone-chart-title").textContent =
            "Top 10 Dropoff Zones by Revenue";

        loadZoneRevenue("dropoff");

        this.classList.add("bg-gray-900", "text-white");
        this.classList.remove("bg-gray-200", "text-gray-700");

        document
            .getElementById("pickup-zone-btn")
            .classList.remove("bg-gray-900", "text-white");

        document
            .getElementById("pickup-zone-btn")
            .classList.add("bg-gray-200", "text-gray-700");
    });


document.querySelectorAll(".filters").forEach(filter=>{
    filter.addEventListener("change", refreshDashboard);
})

document
    .getElementById("reset-filters")
    .addEventListener("click", function () {

        document.getElementById("start-date").value = "2026-05-01";
        document.getElementById("end-date").value = "2026-05-31";

        refreshDashboard();
    });

document
    .getElementById("refresh-ai-insights")
    .addEventListener(
        "click",
        loadAIAnomalies
    );

document
    .getElementById("refresh-ai-anomalies")
    .addEventListener(
        "click",
        loadAIAnomalies
    );


initializeDashboard();
loadKPIs();
loadTripsByHour();
loadTripsByDay();
loadPaymentStatus();
loadRevenueByDay();
loadRevenueByHour();
loadAvgRevenueByHour();
loadZoneRevenue("pickup");
loadAIInsights();
loadAIAnomalies();