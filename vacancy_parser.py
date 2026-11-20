SCRAPE_JS = """() => {
  const nodes = document.querySelectorAll('a[data-qa="serp-item__title"]');
  const data = [];
  nodes.forEach(node => {
    if (!node.href.includes('/vacancy/')) return;
    const titleSpan = node.querySelector('span[data-qa="serp-item__title-text"]');
    data.push({
      title: titleSpan ? titleSpan.textContent.trim() : "Unknown",
      link: node.href
    });
  });
  return data;
}
"""


async def scrape_vacancies(page):
    return await page.evaluate(SCRAPE_JS)
