# Brief for the publish agent

Fill the `{…}` fields and pass everything below the line as the Agent prompt (subagent_type `general-purpose`).
`{TARGET_ARGS}` is `--page-id {PAGE_ID}` for an update, or `--parent-id {PARENT_ID} --space-id {{CONFLUENCE_SPACE_ID}} --label user-guide` for a new page.

---

Convert `{WS}\page.html` to Confluence and publish it to {TARGET_TEXT}. The user approved this overwrite; Confluence keeps the previous version in its page history. Static content becomes native Confluence content, interactive figures become HTML macros, and the page is set to full width.

1. **Convert:**
   `python "{SKILL_DIR}\scripts\to_adf.py" "{WS}\page.html" --out "{WS}\bundle.json" {TARGET_ARGS} {EXISTING_ARG}`
   Read the printed summary. Stop and report instead of publishing if:
   - `warnings` lists a widget script error, or
   - `kept_images_not_placed` is not empty (an image from the old page would disappear), or
   - `bundle_kb` is over 9500 (too big for the browser upload).
   Other warnings: note them, then go on.
2. **Open Confluence:** load the Chrome tools in one ToolSearch call: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__find,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__tabs_close_mcp`. Call `tabs_context_mcp` with createIfEmpty set to true, create a new tab, and open `{{CONFLUENCE_URL}}/spaces/{{CONFLUENCE_SPACE_KEY}}/pages/{PAGE_OR_PARENT_ID}`.
3. **Load the bundle:** inject the loader input with `javascript_tool`:
   `document.getElementById('__cug')?.remove(); const i=document.createElement('input'); i.type='file'; i.id='__cug'; i.setAttribute('aria-label','ZZ cug loader'); i.style.cssText='position:fixed;top:0;left:0;z-index:99999'; document.body.appendChild(i); 'ok'`
   Find it with `find` ("file input labelled ZZ cug loader"). It must be that input, not one of Confluence's upload inputs. Then `file_upload` `{WS}\bundle.json` into it.
4. **Publish:** run with `javascript_tool`:
   `const B = JSON.parse(await document.getElementById('__cug').files[0].text()); const r = await new Function('B', 'return (async () => {' + B.publisher + '})()')(B); (typeof r === 'string' ? r : JSON.stringify(r)).replace(/[?&=]/g, ' ')`
   It returns `{id, url, title, widgets, images, log}` as text. `?`, `&` and `=` are replaced with spaces because the browser tool hides any return value that looks like it holds a query string. If it throws, report the error text. Don't retry by hand-editing the page.
5. **Verify on the live page:** navigate to the page, wait about 5 s, then check with `javascript_tool`:
   `[document.querySelectorAll('iframe').length, [...document.querySelectorAll('img')].filter(i => i.naturalWidth > 200).length]`
   The iframe count should be at least the number of widgets, and the image count at least the number of images. Take one screenshot of the first screen and look at it: the title, the table of contents at the top, coloured headings, full width. Click one control in the first widget and check that something changes.
6. Close your tab.

**Reply** in at most 8 lines: the page URL, the version published, counts (widgets, images uploaded, images reused, code blocks, tables), the verification result, and any warning the user should know about.
