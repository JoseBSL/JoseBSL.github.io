
document.addEventListener("DOMContentLoaded", () => {
  const refs = document.querySelector("#refs");
  if (!refs) return;

  const entries = Array.from(
    refs.querySelectorAll(".csl-entry")
  );

  function normalizeName(html) {
    return html
      .replace(
        /\bB\.\s*Lanuza,\s*Jose\b/gi,
        "Lanuza, J. B."
      )
      .replace(
        /\bLanuza,\s*Jose\s*B\.?\b/gi,
        "Lanuza, J. B."
      )
      .replace(
        /\bJose\s*B\.?\s*Lanuza\b/gi,
        "Lanuza, J. B."
      )
      .replace(
        /\bLanuza,\s*J\.?\s*B\.?\b/gi,
        "Lanuza, J. B."
      )
      .replace(
        /\bLanuza\s+JB\b/gi,
        "Lanuza, J. B."
      );
  }

  function highlightName(html) {
    return html.replace(
      /\bLanuza,\s*J\.\s*B\./gi,
      '<strong class="my-name">Lanuza, J. B.</strong>'
    );
  }

  function highlightTitle(html) {
    // Matches article titles enclosed in curly or straight quotes.
    return html.replace(
      /[“"]([^”"]+)[”"]/g,
      '<strong class="publication-title">$1</strong>'
    );
  }

  function getYear(entry) {
    const text = entry.textContent;
    const years = [...text.matchAll(/\b(?:19|20)\d{2}\b/g)]
      .map(match => Number(match[0]));

    return years.length ? years[0] : 0;
  }

  entries.forEach(entry => {
    let html = entry.innerHTML;

    html = normalizeName(html);
    html = highlightName(html);
    html = highlightTitle(html);

    entry.innerHTML = html;
  });

  // Newest publications first
  entries.sort((a, b) => getYear(b) - getYear(a));

  entries.forEach(entry => refs.appendChild(entry));
});
