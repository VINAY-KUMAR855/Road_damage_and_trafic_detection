/*
====================================================
URBAN INTELLIGENCE — BUS-01 ROUTE MONITORING

1. Left Panel shows Current Location Vehicle Count (not total).
   Clicking any red, yellow, or green dot on the map updates
   the current location count and vehicle type breakdown.
2. Road Damage Intelligence panel shows:
   - Total Road Damage from entire route.
   - 4 sub-categories (Longitudinal Crack, Alligator Crack, Pothole, White Line / Paint Blur).
3. Map features small, crisp, visible Red, Yellow, and Green traffic location dots.
====================================================
*/

/* ================================================
   TRAFFIC CLUSTERING & THRESHOLDS
================================================ */

const CLUSTER_RADIUS_METERS = 100;
const TRAFFIC_HIGH = 8;    // Red
const TRAFFIC_MEDIUM = 5;  // Yellow, else Green

function getTrafficColor(count) {
    if (count >= TRAFFIC_HIGH) return "#ff263d";   // Red
    if (count >= TRAFFIC_MEDIUM) return "#ffd21c";  // Yellow
    return "#35d49a";                               // Green
}

function getTrafficLevelLabel(count) {
    if (count >= TRAFFIC_HIGH) return "High Traffic";
    if (count >= TRAFFIC_MEDIUM) return "Medium Traffic";
    return "Low Traffic";
}

function bucketVehicleType(type) {
    const t = (type || "").toLowerCase();
    if (t === "car") return "CARS";
    if (t === "motorcycle" || t === "bicycle" || t === "bike") return "BIKES";
    if (t === "autorickshaw" || t === "auto") return "AUTOS";
    return "OTHER"; // bus, truck
}

/* ================================================
   BUILD TRAFFIC LOCATIONS (ZONES)
================================================ */

function buildTrafficZones(vehicleDetections, map) {
    const zones = [];

    vehicleDetections.forEach((vehicle) => {
        let zone = zones.find(
            (z) => map.distance(z.position, vehicle.position) <= CLUSTER_RADIUS_METERS
        );

        if (!zone) {
            zone = {
                id: `LOC-${zones.length + 1}`,
                position: vehicle.position,
                count: 0,
                buckets: { CARS: 0, BIKES: 0, AUTOS: 0, OTHER: 0 },
                vehicles: []
            };
            zones.push(zone);
        }

        zone.count++;
        const bucket = bucketVehicleType(vehicle.type);
        zone.buckets[bucket]++;
        zone.vehicles.push(vehicle);
    });

    return zones;
}

/* ================================================
   CREATE MAP
================================================ */

const map = L.map("map", { zoomControl: true });
map.setView([15.5057, 80.0499], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

let routeLine = null;
let routeBounds = null;
let trafficZoneMarkers = [];
let activeZoneMarker = null;

function fitBusRoute() {
    if (!routeBounds) return;
    map.fitBounds(routeBounds, { padding: [50, 50], maxZoom: 15, animate: true, duration: 0.8 });
}
document.getElementById("fitRouteButton").addEventListener("click", fitBusRoute);

/* ================================================
   RENDER ROUTE & BUS MARKER
================================================ */

function renderRoute(routePoints) {
    if (routePoints.length === 0) return;

    routeLine = L.polyline(routePoints, {
        color: "#38bdf8",
        weight: 3,
        opacity: 0.5,
        lineCap: "round",
        lineJoin: "round",
    }).addTo(map);

    const startPoint = routePoints[0];
    L.circleMarker(startPoint, {
        radius: 6, color: "#ffffff", fillColor: "#101820", fillOpacity: 1, weight: 2,
    }).addTo(map).bindTooltip("ROUTE START");

    const endPoint = routePoints[routePoints.length - 1];
    const busIcon = L.divIcon({
        className: "",
        html: `<div class="bus-map-marker">🚌</div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
    });

    L.marker(endPoint, { icon: busIcon, zIndexOffset: 1000 })
        .addTo(map)
        .bindPopup(`
            <div class="popup-title">BUS-01 (Current Position)</div>
            <div class="popup-row"><span>Status</span><strong>ACTIVE</strong></div>
            <div class="popup-row"><span>GPS</span><strong>${endPoint[0].toFixed(4)}° N, ${endPoint[1].toFixed(4)}° E</strong></div>
        `);

    routeBounds = L.latLngBounds(routePoints);
    fitBusRoute();
}

/* ================================================
   CURRENT LOCATION SELECTION
================================================ */

function updateCurrentLocationUI(zone) {
    if (!zone) return;

    // 1. Current Location Vehicle Count (Left panel main number)
    document.getElementById("vehicleCount").textContent = zone.count;

    // 2. Selected Location label and details
    const label = document.getElementById("selectedZoneCount");
    const level = getTrafficLevelLabel(zone.count);
    label.innerHTML = `<strong>${zone.id}</strong> — ${zone.position[0].toFixed(4)}° N, ${zone.position[1].toFixed(4)}° E (${level}: ${zone.count} vehicles)`;

    // 3. Breakdown for current location
    document.getElementById("carCount").textContent = zone.buckets.CARS;
    document.getElementById("bikeCount").textContent = zone.buckets.BIKES;
    document.getElementById("autoCount").textContent = zone.buckets.AUTOS;
    document.getElementById("otherCount").textContent = zone.buckets.OTHER;
}

/* ================================================
   RENDER SMALL & VISIBLE RED, YELLOW, GREEN DOTS
================================================ */

function renderTrafficZones(zones) {
    // Clear old markers
    trafficZoneMarkers.forEach(m => map.removeLayer(m));
    trafficZoneMarkers = [];

    document.getElementById("trafficLocationCount").textContent = String(zones.length).padStart(2, "0");

    if (zones.length === 0) return;

    zones.forEach((zone) => {
        const color = getTrafficColor(zone.count);

        // Small, sharp, visible circle dot
        const marker = L.circleMarker(zone.position, {
            radius: 6,
            color: "#ffffff",
            weight: 1.5,
            fillColor: color,
            fillOpacity: 0.95,
            zIndexOffset: 600
        }).addTo(map);

        const popupContent = `
            <div class="popup-title">Traffic Location: ${zone.id}</div>
            <div class="popup-row"><span>Location Vehicles</span><strong style="color:${color}">${zone.count} vehicles</strong></div>
            <div class="popup-row"><span>Cars</span><strong>${zone.buckets.CARS}</strong></div>
            <div class="popup-row"><span>Bikes</span><strong>${zone.buckets.BIKES}</strong></div>
            <div class="popup-row"><span>Autos</span><strong>${zone.buckets.AUTOS}</strong></div>
            <div class="popup-row"><span>Other</span><strong>${zone.buckets.OTHER}</strong></div>
            <div class="popup-row"><span>GPS</span><strong>${zone.position[0].toFixed(4)}, ${zone.position[1].toFixed(4)}</strong></div>
        `;

        marker.bindPopup(popupContent);

        marker.on("click", () => {
            updateCurrentLocationUI(zone);
        });

        trafficZoneMarkers.push(marker);
    });

    // Default current location to the first location or active position
    if (zones.length > 0) {
        updateCurrentLocationUI(zones[0]);
    }
}

/* ================================================
   ROAD DAMAGE — TOTAL & 4 SUB-THINGS
================================================ */

let damageListItems = [];

function selectDamageItem(index) {
    damageListItems.forEach((el, i) => el.classList.toggle("selected", i === index));
    if (damageListItems[index]) {
        damageListItems[index].scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
}

function renderDamage(damageData) {
    const listContainer = document.getElementById("damageList");
    listContainer.innerHTML = "";
    damageListItems = [];

    // Total Road Damage from entire path
    document.getElementById("damageCount").textContent = String(damageData.length).padStart(2, "0");

    // Count the 4 sub-things matching model DAMAGE_LABELS
    let d00Count = 0; // Longitudinal Crack
    let d20Count = 0; // Alligator Crack
    let d40Count = 0; // Pothole
    let d44Count = 0; // White Line / Paint Blur

    damageData.forEach((item, index) => {
        const type = (item.type || "").toLowerCase();

        if (type.includes("longitudinal")) d00Count++;
        else if (type.includes("alligator")) d20Count++;
        else if (type.includes("pothole")) d40Count++;
        else if (type.includes("white") || type.includes("paint") || type.includes("blur")) d44Count++;
        else {
            // fallback matching raw codes
            if (type === "d00") d00Count++;
            else if (type === "d20") d20Count++;
            else if (type === "d40") d40Count++;
            else if (type === "d44") d44Count++;
            else d00Count++; // general damage
        }

        // Map marker for road damage
        const damageIcon = L.divIcon({
            className: "",
            html: `<div class="damage-map-marker">⚠</div>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12],
        });

        const marker = L.marker(item.position, { icon: damageIcon, zIndexOffset: 800 })
            .addTo(map)
            .bindPopup(`
                <div class="popup-title">⚠ ${item.type}</div>
                <div class="popup-row"><span>Confidence</span><strong>${item.confidence}%</strong></div>
                <div class="popup-row"><span>GPS</span><strong>${item.gps}</strong></div>
                <div class="popup-row"><span>Frame</span><strong>${item.frame}</strong></div>
            `);

        marker.on("click", () => selectDamageItem(index));

        // Sidebar list entry
        const el = document.createElement("div");
        el.className = "damage-item";
        el.innerHTML = `
            <div class="damage-symbol">⚠</div>
            <div class="damage-info">
                <strong>${item.type}</strong>
                <span>Confidence ${item.confidence}%</span>
            </div>
            <span class="zone">FRAME ${item.frame}</span>
        `;
        el.addEventListener("click", () => {
            map.setView(item.position, 17, { animate: true });
            marker.openPopup();
            selectDamageItem(index);
        });

        listContainer.appendChild(el);
        damageListItems.push(el);
    });

    // Update 4 sub-things in Road Damage panel
    document.getElementById("d00Count").textContent = d00Count;
    document.getElementById("d20Count").textContent = d20Count;
    document.getElementById("d40Count").textContent = d40Count;
    document.getElementById("d44Count").textContent = d44Count;
}

/* ================================================
   LOAD DATA FROM FASTAPI ENDPOINTS
================================================ */

async function loadData() {
    try {
        const [routeRaw, vehiclesRaw, damageRaw] = await Promise.all([
            fetch("/api/route").then((r) => r.json()),
            fetch("/api/vehicles").then((r) => r.json()),
            fetch("/api/damage").then((r) => r.json()),
        ]);

        const vehicleDetections = vehiclesRaw
            .filter((v) => v.lat !== null && v.lon !== null)
            .map((v) => ({
                id: `V${String(v.id).padStart(3, "0")}`,
                type: v.class_name,
                position: [v.lat, v.lon],
            }));

        const damageData = damageRaw
            .filter((d) => d.lat !== null && d.lon !== null)
            .map((d) => ({
                type: d.class_name, // relabeled by API (e.g. "Longitudinal Crack", "Pothole", etc.)
                confidence: Math.round(d.confidence * 100),
                position: [d.lat, d.lon],
                gps: `${d.lat.toFixed(4)}° N, ${d.lon.toFixed(4)}° E`,
                frame: d.frame_number,
            }));

        renderRoute(routeRaw);
        const trafficZones = buildTrafficZones(vehicleDetections, map);
        renderTrafficZones(trafficZones);
        renderDamage(damageData);
    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

loadData();
