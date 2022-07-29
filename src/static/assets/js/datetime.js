const el = document.getElementById("daySelect");
el.min = new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, -8);