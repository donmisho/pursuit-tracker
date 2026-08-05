/*
 * Dump the schema of every `pursuit-tracker*` list on the PursuitTracking site.
 *
 * HOW TO RUN
 *   1. Sign in to https://westmonroepartners1.sharepoint.com/sites/PursuitTracking
 *      in your browser, as you normally would.
 *   2. Open DevTools (F12) -> Console.
 *   3. Paste this whole file, press Enter.
 *   4. Copy the printed output.
 *
 * It uses your existing browser session against SharePoint's own REST API. No app
 * registration, no admin consent, no new permissions -- it can only see what you can
 * already see. Every call is a GET; nothing is written or changed.
 */
(async () => {
  const site = location.origin + location.pathname.split('/_layouts')[0].replace(/\/(SitePages|Lists)\/.*$/i, '');
  const web = site.match(/\/sites\/[^/]+/i) ? site.match(/^https?:\/\/[^/]+\/sites\/[^/]+/i)[0] : location.origin;

  const get = async (url) => {
    const res = await fetch(url, { headers: { Accept: 'application/json;odata=nometadata' }, credentials: 'include' });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${url}`);
    return res.json();
  };

  // Columns SharePoint adds to every list. Hidden here so the real schema stands out.
  const NOISE = new Set([
    'ContentType', 'Attachments', 'Edit', 'LinkTitleNoMenu', 'LinkTitle', 'DocIcon',
    'ItemChildCount', 'FolderChildCount', '_ComplianceFlags', '_ComplianceTag',
    '_ComplianceTagWrittenTime', '_ComplianceTagUserId', '_IsRecord', 'AppAuthor',
    'AppEditor', '_UIVersionString', 'ID', 'Created', 'Modified', 'Author', 'Editor',
  ]);

  const TYPES = {
    1: 'Integer', 2: 'Single line of text', 3: 'Multiple lines of text', 4: 'Date and Time',
    5: 'Counter', 6: 'Choice', 7: 'Lookup', 8: 'Yes/No', 9: 'Currency', 10: 'URL',
    11: 'URL', 12: 'Computed', 15: 'Multi-choice', 17: 'Calculated', 20: 'Person or Group',
    30: 'Multi-lookup',
  };

  let lists;
  try {
    lists = (await get(`${web}/_api/web/lists?$select=Title,Id,ItemCount,BaseTemplate&$filter=startswith(Title,'pursuit-tracker')`)).value;
  } catch (e) {
    console.error('Could not read lists. Are you signed in, and on the PursuitTracking site?', e);
    return;
  }

  if (!lists.length) {
    console.warn(`No lists starting with "pursuit-tracker" found under ${web}. Check the site URL.`);
    return;
  }

  const summary = [];
  for (const list of lists.sort((a, b) => a.Title.localeCompare(b.Title))) {
    const fields = (await get(
      `${web}/_api/web/lists/getbytitle('${encodeURIComponent(list.Title)}')/fields` +
      `?$select=Title,InternalName,TypeAsString,FieldTypeKind,Required,Hidden,ReadOnlyField,Choices,LookupList,AllowMultipleValues`
    )).value.filter((f) => !f.Hidden && !f.ReadOnlyField && !NOISE.has(f.InternalName));

    console.group(`%c${list.Title}%c  (${list.ItemCount} items, ${fields.length} columns)`,
      'font-weight:bold;font-size:13px', 'color:#888');
    console.table(fields.map((f) => ({
      'Display name': f.Title,
      'Internal name': f.InternalName,
      Type: f.TypeAsString || TYPES[f.FieldTypeKind] || f.FieldTypeKind,
      Multi: f.AllowMultipleValues ? 'yes' : '',
      Required: f.Required ? 'yes' : '',
      Choices: (f.Choices || []).join(' | '),
    })));
    console.groupEnd();

    summary.push(
      `## ${list.Title}  (${list.ItemCount} items)\n` +
      fields.map((f) =>
        `- ${f.Title} [${f.InternalName}] : ${f.TypeAsString || TYPES[f.FieldTypeKind]}` +
        (f.AllowMultipleValues ? ' (multi)' : '') +
        (f.Required ? ' (required)' : '') +
        ((f.Choices || []).length ? `\n    choices: ${f.Choices.join(', ')}` : '')
      ).join('\n')
    );
  }

  const text = summary.join('\n\n');
  console.log('%c\n--- copy everything below this line ---\n', 'color:#6B7DF2;font-weight:bold');
  console.log(text);
  try {
    await navigator.clipboard.writeText(text);
    console.log('%c(also copied to your clipboard)', 'color:#888');
  } catch {
    console.log('%c(clipboard blocked -- select and copy the block above)', 'color:#888');
  }
})();
