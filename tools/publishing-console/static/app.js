let registry;
const level = document.querySelector('#level');
const book = document.querySelector('#book');
const pageType = document.querySelector('#page_type');
const activityFields = document.querySelector('#activity-fields');
const physicalPage = document.querySelector('#physical_page');
const pageId = document.querySelector('#page_id');
const activityType = document.querySelector('#activity_type');
const output = document.querySelector('#output');

function populateBooks() {
  const books = registry.levels[level.value].books;
  book.innerHTML = Object.entries(books)
    .map(([slug, value]) => `<option value="${slug}">${value.title}</option>`)
    .join('');
  updatePageId();
}

function updatePageId() {
  if (!registry || !book.value) return;
  const meta = registry.levels[level.value];
  const selected = meta.books[book.value];
  const number = String(Number(physicalPage.value || 1)).padStart(3, '0');
  pageId.value = `${selected.prefix}-${meta.id_level}-V4-P${number}`;
}

function updatePageType() {
  const isCover = pageType.value === 'cover';
  activityFields.classList.toggle('hidden', isCover);
  activityType.value = isCover ? '' : pageType.value;
  updatePageId();
}

async function init() {
  const response = await fetch('/api/registry');
  registry = await response.json();
  level.innerHTML = Object.entries(registry.levels)
    .map(([slug, value]) => `<option value="${slug}">${value.display_level} (${value.age})</option>`)
    .join('');
  populateBooks();
  updatePageType();
}

level.addEventListener('change', populateBooks);
book.addEventListener('change', updatePageId);
physicalPage.addEventListener('input', updatePageId);
pageType.addEventListener('change', updatePageType);

document.querySelector('#publish-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  output.textContent = 'Publishing…';
  const formData = new FormData(event.currentTarget);
  formData.set('approve', document.querySelector('#approve').checked ? 'true' : 'false');
  try {
    const response = await fetch('/api/publish', {method: 'POST', body: formData});
    const result = await response.json();
    output.textContent = result.ok
      ? `${result.stdout || 'Page generated successfully.'}\n${result.stderr || ''}`
      : `${result.error || result.stderr || 'Publishing failed.'}`;
  } catch (error) {
    output.textContent = `Request failed: ${error.message}`;
  }
});

init().catch(error => { output.textContent = `Startup failed: ${error.message}`; });
