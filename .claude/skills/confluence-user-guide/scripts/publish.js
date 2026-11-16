// Runs in a logged-in Confluence tab as the body of an async function with the bundle as `B`:
//   const B = JSON.parse(await document.getElementById('__cug').files[0].text());
//   await new Function('B', 'return (async () => {' + B.publisher + '})()')(B)
// Creates or updates the page, uploads images, fills media placeholders, sets full width, adds labels.
const api = async (method, url, body, headers = {}) => {
  const r = await fetch(url, { method, headers: body instanceof FormData ? { 'X-Atlassian-Token': 'no-check', ...headers }
    : { 'Content-Type': 'application/json', ...headers }, body: body instanceof FormData ? body : body && JSON.stringify(body) });
  const text = await r.text();
  if (!r.ok) throw new Error(`${method} ${url} -> ${r.status}: ${text.slice(0, 600)}`);
  return text ? JSON.parse(text) : {};
};
const t = B.target, log = [];
let id = t.pageId, page;

if (!id) {
  const exists = await api('GET', `/wiki/api/v2/spaces/${t.spaceId}/pages?title=${encodeURIComponent(t.title)}`);
  if (exists.results.length) throw new Error(`a page titled "${t.title}" already exists: ${exists.results[0].id}`);
  page = await api('POST', '/wiki/api/v2/pages', { spaceId: t.spaceId, parentId: t.parentId, status: 'current', title: t.title,
    body: { representation: 'atlas_doc_format', value: JSON.stringify({ type: 'doc', version: 1,
      content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Publishing…' }] }] }) } });
  id = page.id; log.push(`created ${id}`);
}
page = await api('GET', `/wiki/api/v2/pages/${id}`);

const files = {};
for (const img of B.images) {
  const bin = Uint8Array.from(atob(img.b64), c => c.charCodeAt(0));
  const fd = new FormData();
  fd.append('file', new Blob([bin], { type: img.mediaType }), img.name);
  fd.append('minorEdit', 'true');
  const res = await api('PUT', `/wiki/rest/api/content/${id}/child/attachment`, fd);
  const fileId = res.results?.[0]?.extensions?.fileId;
  if (!fileId) throw new Error(`no fileId for ${img.name}`);
  files[img.placeholder] = fileId;
}
log.push(`uploaded ${Object.keys(files).length} images`);

const unfilled = [];
const fill = n => {
  if (n.type === 'media' && /^@@IMG:/.test(n.attrs.id)) {
    const key = n.attrs.id.slice(6, -2);
    if (files[key]) { n.attrs.id = files[key]; n.attrs.collection = `contentId-${id}`; } else unfilled.push(key);
  }
  (n.content || []).forEach(fill);
};
fill(B.adf);
if (unfilled.length) throw new Error(`placeholders without an upload: ${unfilled.join(', ')}`);

await api('PUT', `/wiki/api/v2/pages/${id}`, { id, status: 'current', title: page.title,
  body: { representation: 'atlas_doc_format', value: JSON.stringify(B.adf) },
  version: { number: page.version.number + 1, message: 'confluence-user-guide: illustrated, native content + interactive widgets' } });
log.push(`page version ${page.version.number + 1}`);

const props = (await api('GET', `/wiki/api/v2/pages/${id}/properties?limit=100`)).results;
for (const key of ['content-appearance-published', 'content-appearance-draft']) {
  const p = props.find(x => x.key === key);
  if (!p) await api('POST', `/wiki/api/v2/pages/${id}/properties`, { key, value: 'max' });
  else if (p.value !== 'max') await api('PUT', `/wiki/api/v2/pages/${id}/properties/${p.id}`, { key, value: 'max', version: { number: p.version.number + 1 } });
}
log.push('full width');

// Title emoji: set the one the page chose, but never replace an emoji someone already gave the page.
if (t.emoji) {
  const current = props.find(x => x.key === 'emoji-title-published');
  if (current && current.value) log.push(`kept existing emoji ${current.value}`);
  else {
    for (const key of ['emoji-title-published', 'emoji-title-draft']) {
      const p = props.find(x => x.key === key);
      if (!p) await api('POST', `/wiki/api/v2/pages/${id}/properties`, { key, value: t.emoji });
      else await api('PUT', `/wiki/api/v2/pages/${id}/properties/${p.id}`, { key, value: t.emoji, version: { number: p.version.number + 1 } });
    }
    log.push(`emoji ${t.emoji}`);
  }
}

if (t.labels && t.labels.length) {
  await api('POST', `/wiki/rest/api/content/${id}/label`, t.labels.map(name => ({ prefix: 'global', name })), { 'X-Atlassian-Token': 'no-check' });
  log.push(`labels ${t.labels.join(', ')}`);
}
return JSON.stringify({ id, url: `${location.origin}/wiki/pages/viewpage.action?pageId=${id}`, title: page.title, widgets: B.widgets.length, images: Object.keys(files).length, log });
