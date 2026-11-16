# Brief for the export agent

Fill the `{…}` fields and pass everything below the line as the Agent prompt (subagent_type `general-purpose`).

---

Export the Confluence page **{PAGE_ID}** ("{TITLE}") and its images to `{WS}\existing\`, so a later step can rebuild the page without losing anything. The user has already approved downloading `cug-export-{PAGE_ID}.json` from {{CONFLUENCE_URL}} to their Downloads folder (`{{DOWNLOADS}}`). Don't change anything on Confluence.

1. Load the Chrome tools in one ToolSearch call: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__find,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__tabs_close_mcp`. Call `tabs_context_mcp` with createIfEmpty set to true, create a new tab, and navigate to `{{CONFLUENCE_URL}}/spaces/{{CONFLUENCE_SPACE_KEY}}/pages/{PAGE_ID}`.
2. Inject a loader input with `javascript_tool`:
   `document.getElementById('__cug')?.remove(); const i=document.createElement('input'); i.type='file'; i.id='__cug'; i.setAttribute('aria-label','ZZ cug loader'); i.style.cssText='position:fixed;top:0;left:0;z-index:99999'; document.body.appendChild(i); 'ok'`
   Find it with `find` ("file input labelled ZZ cug loader"). Make sure the ref is that input, not one of Confluence's own upload inputs: a file put into one of those would be attached to the page. Then `file_upload` `{SKILL_DIR}\scripts\export.js` into it.
3. Run it with `javascript_tool`:
   `const text = await document.getElementById('__cug').files[0].text(); await new Function('P', 'return (async () => {' + text + '})()')({ pageId: '{PAGE_ID}' })`
   It returns `{file, kb, images, missing, macros}` and saves the file to the Downloads folder.
4. Move `cug-export-{PAGE_ID}.json` from the Downloads folder (`{{DOWNLOADS}}`) to `{WS}\`. If there are several copies, take the newest, such as `… (1).json`.
5. Run `python "{SKILL_DIR}\scripts\unpack_export.py" "{WS}\cug-export-{PAGE_ID}.json" "{WS}\existing"`.
6. Close your tab.

If an image is reported as `missing` (for example it lives on another page), list its fileId; don't try to fix it.

**Reply** in at most 6 lines: the page title and version, the number of images kept (attachments and from HTML macros), the number of HTML macros, any missing images, and the `existing` path.
