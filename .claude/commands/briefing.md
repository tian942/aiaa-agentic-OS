# /briefing — Daily Kairo Business Briefing

Run the daily finance and business briefing. Reads every tab from the master Google Sheet, generates a full Hormozi-framework analysis with Claude, and sends it to tian@kairoscales.com.

**Execute immediately — no questions, no confirmation:**

```bash
cd /Users/marsi/Desktop/BusinessOS && python3 railway_apps/finance_report/briefing_local.py
```

**What happens:**
1. Authenticates with Google (browser opens automatically first time or if token expired — just log in with tmarsel26@gmail.com and allow permissions)
2. Reads ALL tabs from the master sheet — auto-detects any new tabs
3. Reads DAILY NOTES tab if it exists (your previous responses feed into today's report)
4. Generates the full briefing via Claude: financial snapshot, client health, unit economics, expenses, D100, cold email campaigns, cold calls, leads pipeline, business health diagnosis, top 3 actions
5. Sends the email to tian@kairoscales.com

**If the browser opens for Google login:**
- Log in as tmarsel26@gmail.com
- Click Allow on all permission requests
- It saves the token — won't ask again for months

**After it runs:**
Report the result to the user: confirm email was sent, or show any error with a clear explanation of what to do.
