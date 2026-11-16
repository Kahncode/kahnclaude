// Run with the Chrome javascript_tool in a logged-in tab on the project's Confluence site, after
// file_upload has put one or more bundle.json files (from md_to_confluence.py) into the input labelled
// "cc-bundle-upload". Per bundle: uploads the diagram PNGs as attachments (same name = new attachment
// version), PUTs the storage body, then re-reads the page and reports anything that would not render.
await (async () => {
  const input = document.querySelector('input[aria-label="cc-bundle-upload"]');
  if (!input || !input.files.length) return 'No bundle in the cc-bundle-upload input';
  const xsrf = { 'X-Atlassian-Token': 'no-check' };

  const publish = async (p) => {
    for (const a of p.attachments) {
      const bytes = Uint8Array.from(atob(a.b64), c => c.charCodeAt(0));
      const form = new FormData();
      form.append('file', new Blob([bytes], { type: 'image/png' }), a.name);
      form.append('minorEdit', 'true');
      const r = await fetch(`/wiki/rest/api/content/${p.id}/child/attachment`, { method: 'PUT', headers: xsrf, body: form });
      if (!r.ok) return { title: p.title, step: 'attachment', name: a.name, status: r.status, err: (await r.text()).slice(0, 400) };
    }
    const cur = await (await fetch(`/wiki/api/v2/pages/${p.id}`)).json();
    const put = await fetch(`/wiki/api/v2/pages/${p.id}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ id: p.id, status: 'current', title: p.title,
        body: { representation: 'storage', value: p.body },
        version: { number: cur.version.number + 1, message: `Sync from ${p.source}` } }) });
    if (!put.ok) return { title: p.title, step: 'page', status: put.status, err: (await put.text()).slice(0, 600) };

    const after = await (await fetch(`/wiki/api/v2/pages/${p.id}?body-format=storage`)).json();
    const s = after.body.storage.value.replace(/<!\[CDATA\[[\s\S]*?\]\]>/g, '');
    const atts = await (await fetch(`/wiki/api/v2/pages/${p.id}/attachments?limit=250`)).json();
    const names = new Set((atts.results || []).map(x => x.title));
    const images = [...s.matchAll(/ri:filename="([^"]+)"/g)].map(m => m[1]);
    return {
      id: p.id, title: p.title, version: `${cur.version.number} -> ${after.version.number}`,
      uploaded: p.attachments.length,
      imagesMissingAttachment: images.filter(n => !names.has(n)),
      mdNamesLeft: (s.match(/<a [^>]*>[^<]*\.md\b/g) || []).length,
      localHrefs: (s.match(/href="(?!https?:\/\/|#|mailto:)[^"]*"/g) || []),
      mermaidCodeBlocks: (s.match(/ac:name="language">mermaid</g) || []).length,
    };
  };

  const reports = [];
  for (const f of input.files) reports.push(await publish(JSON.parse(await f.text())));
  return reports;
})()
