// Runs in a logged-in Confluence tab as the body of an async function with `P = { pageId }`:
//   const text = await document.getElementById('__cug').files[0].text();
//   await new Function('P', 'return (async () => {' + text + '})()')({ pageId: '123' })
// Downloads cug-export-<pageId>.json: page metadata, its ADF body, and every image the body shows
// (attachments by fileId, as base64). HTML-macro content stays inside the ADF for unpack_export.py.
const get = async url => { const r = await fetch(url); if (!r.ok) throw new Error(`${url} -> ${r.status}`); return r.json(); };
const page = await get(`/wiki/api/v2/pages/${P.pageId}?body-format=atlas_doc_format&include-properties=true`);
const adf = JSON.parse(page.body.atlas_doc_format.value);

const attachments = [];
let next = `/wiki/api/v2/pages/${P.pageId}/attachments?limit=100`;
while (next) {
  const res = await get(next);
  attachments.push(...res.results);
  next = res._links && res._links.next ? res._links.next.replace(/^\/wiki/, '') : null;
  if (next) next = '/wiki' + next;
}

const used = new Set();
const walk = n => { if (n.type === 'media' && n.attrs && n.attrs.id) used.add(n.attrs.id); (n.content || []).forEach(walk); };
walk(adf);

const toB64 = async blob => {
  const buf = new Uint8Array(await blob.arrayBuffer());
  let s = '';
  for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  return btoa(s);
};
const images = [], missing = [];
for (const fileId of used) {
  const a = attachments.find(x => x.fileId === fileId);
  if (!a) { missing.push(fileId); continue; }
  const r = await fetch('/wiki' + a.downloadLink);
  if (!r.ok) { missing.push(fileId); continue; }
  images.push({ fileId, title: a.title, mediaType: a.mediaType, size: a.fileSize, b64: await toB64(await r.blob()) });
}

const out = { page: { id: page.id, title: page.title, spaceId: page.spaceId, parentId: page.parentId, version: page.version.number,
  properties: (page.properties && page.properties.results || []).map(p => ({ key: p.key, value: p.value })) },
  adf, images, missingImages: missing, attachmentCount: attachments.length };
const blob = new Blob([JSON.stringify(out)], { type: 'application/json' });
const a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = `cug-export-${P.pageId}.json`;
// Confluence's own link handler opens blob: links in the tab instead of saving them; stop it for this one click.
const guard = e => { if (e.target === a) e.stopImmediatePropagation(); };
window.addEventListener('click', guard, true);
document.body.appendChild(a); a.click(); a.remove();
window.removeEventListener('click', guard, true);
let macros = 0;
const count = n => { if (n.type === 'extension' && /html-from-attachment/.test(n.attrs && n.attrs.extensionKey || '')) macros++; (n.content || []).forEach(count); };
count(adf);
return JSON.stringify({ file: a.download, kb: Math.round(blob.size / 1024), images: images.length, missing: missing.length, macros });
