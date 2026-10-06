# Trh práce SK: live platform

This repository contains the data analysis. The live web app is built in Lovable on Lovable Cloud (Postgres, edge functions, cron, realtime).

- Preview: https://id-preview--59e32487-582b-4add-bf45-fa8cd61eaa44.lovable.app
- Editor: https://lovable.dev/projects/59e32487-582b-4add-bf45-fa8cd61eaa44

Status as of 6 October 2026. The app is not published yet.

## Features

| Area | What it does |
|---|---|
| Overview | Vacancies, unemployment, wages and work from home, with a "What changed" feed and a release calendar. Updates live. |
| Graduates | Graduates by ISCED level and field, recent-graduate employment rate, and graduates compared with openings. |
| Regions | NUTS3 map of the 8 kraje (Eurostat GISCO boundaries), a side panel per region, and okres rankings. |
| Industries | Per NACE section: vacancy rate, wages, wage growth, and links to employers. |
| Find jobs | About 1,440 real jobs (Jooble API and public ATS feeds) with filters. Apply opens the original ad. Search links for 105 employers. |
| Employers | Approved employers post jobs. Every post goes to an admin moderation queue. |
| CV builder | FlowCV-style flow: My CVs, Content, Customize, AI Tools, PDF export, 6 original templates, Apply with my CV. |
| Accounts | Google or email login with seeker, employer and admin roles. GDPR data export and account deletion. |

## Data sources

| Source | Data | How it arrives |
|---|---|---|
| Eurostat | Unemployment (total, under 25, NUTS3), HICP, job vacancy rate by NACE, graduates, work from home | API, every 6 hours |
| ŠÚ SR DATAcube | Average wage by kraj and NACE, real wage growth | API, weekly |
| ÚPSVaR | PDU, jobseekers, vacancies by kraj and okres | Monthly file, parsed daily |
| Jooble | Job listings for Slovakia | REST API (key stored as a backend secret) |
| Greenhouse, SmartRecruiters and other ATS | Company job feeds | Official public job-board endpoints, daily |
| Profesia | Quarterly report figures | Entered by hand. The live connector is off by default because their terms forbid scraping. |
| CVTI SR, Trexima | Graduates, salaries | CSV import in Admin |
| Snowflake (optional) | Full history warehouse | Sync built. Blocked until the database and grants exist. |

## Rules

- Real data only. A metric with no data shows "Awaiting data". No invented numbers, ratings or listings.
- No scraping of LinkedIn or Profesia.
- Company search links never claim that a role exists.
- CVs are private. An employer only sees the CV snapshot sent to their own job.

## Next

1. The language choice must persist across all pages.
2. Company Directory page using the RPO API (Statistical Office, CC BY 4.0).
3. Final review, then publish.

The full roadmap and bug list are kept in Notion.
