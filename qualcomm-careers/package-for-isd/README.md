# Qualcomm Careers Scraper

A Python web scraper for extracting job listings from [Qualcomm Careers](https://careers.qualcomm.com) website.

---

## Overview

This scraper uses the **Eightfold AI API** that powers the Qualcomm Careers website. It extracts comprehensive job information including:

- Basic job information (title, location, department)
- Detailed job descriptions (responsibilities, qualifications)

### Key Features

- ✅ **No authentication required** - Uses public API
- ✅ **Structured data extraction** - Parses HTML to extract specific sections
- ✅ **Rate limiting** - Built-in delays to avoid server overload
- ✅ **Multiple output formats** - Excel (.xlsx) and JSON
- ✅ **Command line interface** - Easy to use with various options

---

## Requirements

- Python 3.8 or higher
- Required packages (see `requirements.txt`)

### Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Verify installation
python qualcomm_careers_scraper.py --help
```

---

## Usage

### Basic Usage

```bash
# Full scrape with all job details (recommended)
python qualcomm_careers_scraper.py

# Quick scrape - job list only, no details (faster)
python qualcomm_careers_scraper.py --no-details

# Test mode - only fetch 10 job details
python qualcomm_careers_scraper.py --test

# Custom output filename
python qualcomm_careers_scraper.py --output qualcomm_jobs.xlsx

# Quiet mode (no progress messages)
python qualcomm_careers_scraper.py --quiet
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--no-details` | Skip fetching job details (faster, ~2 min) |
| `--test` | Test mode - only fetch 10 job details |
| `--output FILE` | Custom output Excel filename |
| `--quiet` | Suppress progress messages |
| `--help` | Show help message |

### Expected Runtime

| Mode | Jobs | Time |
|------|------|------|
| List only (`--no-details`) | ~1,300 | ~2 minutes |
| Full scrape | ~1,300 | ~10-15 minutes |
| Test mode (`--test`) | ~1,300 list + 10 details | ~3 minutes |

---

## Output

### Excel File Columns

| Column | Source | Description |
|--------|--------|-------------|
| `job_id` | List API | Unique job identifier |
| `position_id` | List API | Internal position ID |
| `title` | List API | Job title |
| `url` | List API | Direct link to job posting |
| `department` | List API | Department/category (e.g., "Software Engineering") |
| `business_unit` | List API | Business unit code |
| `location` | List API | Full location string |
| `city` | List API | City name (parsed from location) |
| `region` | List API | State/Province (parsed from location) |
| `country` | List API | Country name (parsed from location) |
| `work_type` | List API | Work arrangement: "onsite", "remote", "hybrid" |
| `created_date` | List API | Job posting date |
| `company` | Detail API | Company entity (e.g., "Qualcomm China") |
| `job_area` | Detail API | Job area/function |
| `general_summary` | Detail API | Job overview/summary |
| `responsibilities` | Detail API | Job responsibilities |
| `minimum_qualifications` | Detail API | Required qualifications |
| `preferred_qualifications` | Detail API | Preferred/nice-to-have qualifications |
| `educational_requirements` | Detail API | Education requirements |

### JSON File Structure

```json
{
  "positions": [...],
  "departments": ["Software Engineering", "Hardware Engineering", ...],
  "count": 1300,
  "scraped_at": "2024-11-26T12:00:00"
}
```

---

## Technical Details

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/apply/v2/jobs?domain=qualcomm.com` | GET | Job listings |
| `/api/apply/v2/jobs/{id}?domain=qualcomm.com` | GET | Job details |

### Scraping Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    SCRAPING WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Get Total Count                                    │
│     GET /api/apply/v2/jobs?domain=qualcomm.com&num=1       │
│     → Returns: { "count": 1300, ... }                       │
│                                                             │
│  Step 2: Fetch Job List (paginated)                         │
│     GET /api/apply/v2/jobs?domain=qualcomm.com&start=0&num=50│
│     GET /api/apply/v2/jobs?domain=qualcomm.com&start=50&num=50│
│     ...                                                     │
│     → Returns: Basic job info (title, location, department) │
│                                                             │
│  Step 3: Fetch Job Details (for each job)                   │
│     GET /api/apply/v2/jobs/{position_id}?domain=qualcomm.com│
│     → Returns: { "job_description": "<html>...</html>" }    │
│                                                             │
│  Step 4: Parse HTML                                         │
│     Extract sections: Company, Job Area, Summary,           │
│                       Responsibilities, Qualifications      │
│                                                             │
│  Step 5: Output                                             │
│     → Excel file (.xlsx)                                    │
│     → JSON file (.json)                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Rate Limiting

The scraper includes built-in delays:
- **0.3 seconds** between list API calls
- **0.2 seconds** between detail API calls

This prevents server overload and ensures reliable scraping.

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Connection timeout | Check internet connection, retry |
| Empty detail fields | Some jobs may not have all sections filled |
| SSL errors | Update Python/certificates, or use VPN |

### Logging

To see detailed progress, run without `--quiet` flag:

```bash
python qualcomm_careers_scraper.py
```

---

## Notes

1. **No API key required** - This uses public APIs
2. **Data freshness** - Job listings update frequently; re-run to get latest data
3. **Field variations** - Not all jobs have all detail fields (depends on how recruiter filled the posting)
4. **Legal** - Use responsibly and in accordance with Qualcomm's terms of service

---

## Support

For questions or issues, contact your IT team lead.

---

*Last Updated: November 2024*

