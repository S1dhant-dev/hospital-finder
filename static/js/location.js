(() => {
  const button = document.getElementById("use-location");
  const latitude = document.getElementById("user-lat");
  const longitude = document.getElementById("user-lon");
  const status = document.getElementById("location-status");

  if (!button || !latitude || !longitude || !status) return;

  button.addEventListener("click", () => {
    if (!navigator.geolocation) {
      status.textContent = "Location isn't available in this browser.";
      return;
    }

    button.disabled = true;
    status.textContent = "Finding your location…";
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        latitude.value = coords.latitude;
        longitude.value = coords.longitude;
        status.textContent = "Location added. Select “Find hospitals” to see nearby care.";
        button.disabled = false;
      },
      () => {
        status.textContent = "Couldn't access your location. Check browser permissions or search by city.";
        button.disabled = false;
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
    );
  });
})();
