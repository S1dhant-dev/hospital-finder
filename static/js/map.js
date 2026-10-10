(() => {
  const map = document.getElementById("hospital-map");
  const cards = [...document.querySelectorAll(".result-card[data-lat][data-lon]")];
  if (!map || cards.length === 0) return;

  const points = cards.map((card) => ({
    element: card,
    latitude: Number(card.dataset.lat),
    longitude: Number(card.dataset.lon),
  })).filter((point) => Number.isFinite(point.latitude) && Number.isFinite(point.longitude));
  if (points.length === 0) return;

  const showMapError = () => {
    map.textContent = "The interactive map could not be loaded. Use the directions links beside each hospital.";
  };

  const initializeMap = () => {
    if (!window.L) {
      showMapError();
      return;
    }

    const hospitalMap = L.map(map);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
      maxZoom: 19,
    }).addTo(hospitalMap);

    const bounds = [];
    for (const point of points) {
      const location = [point.latitude, point.longitude];
      const marker = L.marker(location, {
        icon: L.divIcon({
          className: "hospital-map-marker",
          html: '<span class="map-marker-symbol">+</span>',
          iconSize: [30, 30],
          iconAnchor: [15, 15],
          popupAnchor: [0, -14],
        }),
      }).addTo(hospitalMap);
      const popup = document.createElement("div");
      const name = document.createElement("strong");
      name.textContent = point.element.dataset.name;
      const address = document.createElement("p");
      address.textContent = point.element.dataset.address;
      const directions = document.createElement("a");
      directions.href = `https://www.openstreetmap.org/directions?to=${point.latitude}%2C${point.longitude}`;
      directions.target = "_blank";
      directions.rel = "noopener noreferrer";
      directions.textContent = "Get directions";
      popup.append(name, address, directions);
      marker.bindPopup(popup);
      bounds.push(location);
    }

    hospitalMap.fitBounds(bounds, { padding: [24, 24], maxZoom: 14 });
  };

  if (window.L) {
    initializeMap();
    return;
  }

  const stylesheet = document.createElement("link");
  stylesheet.rel = "stylesheet";
  stylesheet.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
  document.head.append(stylesheet);

  const library = document.createElement("script");
  library.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
  library.integrity = "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=";
  library.crossOrigin = "anonymous";
  library.onload = initializeMap;
  library.onerror = showMapError;
  document.head.append(library);
})();
