// ─────────────────────────────────────────────────────────────
// Win Marketing — Client Success Form → Google Sheets
//
// HOW TO DEPLOY:
// 1. Go to script.google.com → New project
// 2. Paste this entire file, replacing what's there
// 3. Click Deploy → New deployment → Web app
// 4. Execute as: Me
//    Who has access: Anyone
// 5. Click Deploy → copy the web app URL
// 6. Paste the URL into client-success.html where it says
//    PASTE_YOUR_APPS_SCRIPT_URL_HERE
// ─────────────────────────────────────────────────────────────

const SHEET_ID  = '1yY2jqgokNDe-C0NLurARlxGTA--Hg9lUHLK219-Wywk';
const TAB_NAME  = 'CLIENT FEEDBACK';

const HEADERS = [
  'Timestamp',
  'Client Name',
  '01 — Biggest Win This Month',
  '02 — One Thing They\'d Miss',
  '03 — Happiness Score (1–10)',
  '03 — Reason for Score',
  '04 — What\'s Not Working',
  '05 — Next 30 Days'
];

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    const ss  = SpreadsheetApp.openById(SHEET_ID);
    let   tab = ss.getSheetByName(TAB_NAME);

    // Create tab if it doesn't exist
    if (!tab) {
      tab = ss.insertSheet(TAB_NAME);
    }

    // Add headers if sheet is empty
    if (tab.getLastRow() === 0) {
      tab.appendRow(HEADERS);
      tab.getRange(1, 1, 1, HEADERS.length)
        .setFontWeight('bold')
        .setBackground('#1A1A1A')
        .setFontColor('#FFFFFF');
      tab.setFrozenRows(1);
    }

    // Append the response
    tab.appendRow([
      data.timestamp || new Date().toISOString(),
      data.client_name   || '',
      data.biggest_win   || '',
      data.one_thing     || '',
      data.score         || '',
      data.score_reason  || '',
      data.not_working   || '',
      data.next_30_days  || ''
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Test function — run this manually in the editor to verify it works
function testSubmit() {
  const fake = {
    postData: {
      contents: JSON.stringify({
        timestamp:    new Date().toISOString(),
        client_name:  'Test Client',
        biggest_win:  'Scaled ads to $10k/month',
        one_thing:    'The weekly reporting and communication',
        score:        '9',
        score_reason: 'Results are great, just want faster turnaround',
        not_working:  'Nothing major',
        next_30_days: 'Launch the new VSL'
      })
    }
  };
  doPost(fake);
  Logger.log('Done — check the sheet');
}
