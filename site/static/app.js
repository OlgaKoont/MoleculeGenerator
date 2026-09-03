(function () {
  const menuBtn = document.querySelector("[data-menu]");
  const sidebar = document.getElementById("sidebar");
  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }

  const input = document.getElementById("site-search");
  const box = document.getElementById("search-results");
  function rootPrefix() {
    const script = document.querySelector('script[src*="static/app.js"]');
    if (script) {
      const src = script.getAttribute("src") || "";
      const cut = src.indexOf("static/app.js");
      if (cut >= 0) return src.slice(0, cut);
    }
    return "";
  }
  if (input && box && window.SEARCH_INDEX) {
    input.addEventListener("input", function () {
      const q = input.value.trim().toLowerCase();
      if (!q) {
        box.hidden = true;
        box.style.display = "none";
        box.innerHTML = "";
        return;
      }
      const hits = window.SEARCH_INDEX.filter(function (item) {
        return (item.text || "").toLowerCase().indexOf(q) >= 0 || (item.name || "").toLowerCase().indexOf(q) >= 0;
      }).slice(0, 20);
      box.hidden = false;
      box.style.display = "block";
      const prefix = rootPrefix();
      box.innerHTML = hits.length
        ? hits
            .map(function (h) {
              return '<a href="' + prefix + h.href + '"><span class="kind">' + h.kind + "</span>" + h.name + "</a>";
            })
            .join("")
        : '<div style="padding:8px">Ничего не найдено</div>';
    });
    document.addEventListener("click", function (e) {
      if (!box.contains(e.target) && e.target !== input) {
        box.hidden = true;
        box.style.display = "none";
      }
    });
  }

  const table = document.getElementById("tool-table");
  const filters = document.getElementById("tool-filters");
  if (table && filters) {
    filters.addEventListener("change", function () {
      const mods = Array.from(filters.querySelectorAll('[data-f="mod"]:checked')).map(function (x) { return x.value; });
      const ab = filters.querySelector('[data-f="ab"]:checked');
      const ev = filters.querySelector('[data-f="ev"]:checked');
      const open = filters.querySelector('[data-f="open"]:checked');
      const pre = filters.querySelector('[data-f="pre"]:checked');
      Array.from(table.querySelectorAll(".tool-row")).forEach(function (row) {
        let ok = true;
        if (mods.length) {
          ok = mods.some(function (m) { return (row.dataset.mod || "").indexOf(m) >= 0; });
        }
        if (ok && ab) ok = row.dataset.ab === "1";
        if (ok && ev) ok = row.dataset.ev === "1";
        if (ok && open) ok = row.dataset.open === "1";
        if (ok && pre) ok = row.dataset.pre !== "1";
        row.style.display = ok ? "" : "none";
      });
    });
  }

  const cmpBoxes = document.querySelectorAll("input.cmp");
  const cmpTable = document.getElementById("cmp-table");
  const warn = document.getElementById("compat-warn");
  if (cmpBoxes.length && cmpTable && window.COMPARE_DATA) {
    const byId = {};
    window.COMPARE_DATA.forEach(function (row) { byId[row.id] = row; });
    function render() {
      const selected = Array.from(cmpBoxes).filter(function (b) { return b.checked; }).map(function (b) { return b.value; });
      const groups = new Set(selected.map(function (id) { return byId[id] && byId[id].group; }).filter(Boolean));
      if (warn) {
        warn.style.display = groups.size > 1 ? "block" : "none";
        warn.classList.toggle("compat-warn", true);
      }
      if (!selected.length) {
        cmpTable.innerHTML = "";
        return;
      }
      const fields = window.COMPARE_FIELDS;
      let html = "<thead><tr><th>Поле</th>" + selected.map(function (id) {
        return "<th>" + (byId[id] ? byId[id].name : id) + "</th>";
      }).join("") + "</tr></thead><tbody>";
      fields.forEach(function (f) {
        html += "<tr><th>" + f + "</th>";
        selected.forEach(function (id) {
          const val = byId[id] ? byId[id][f] : "";
          html += "<td>" + (val == null || val === "" ? "NR" : String(val)) + "</td>";
        });
        html += "</tr>";
      });
      html += "</tbody>";
      cmpTable.innerHTML = html;
    }
    cmpBoxes.forEach(function (b) { b.addEventListener("change", render); });
  }
})();
