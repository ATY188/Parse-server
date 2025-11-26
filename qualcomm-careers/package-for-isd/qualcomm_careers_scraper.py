#!/usr/bin/env python3
"""
Qualcomm Careers Scraper
========================
A web scraper for Qualcomm Careers website using Eightfold AI API.

This scraper extracts job listings with detailed information including:
- Basic info: Job ID, Title, URL, Department, Location
- Detail info: Company, Job Area, General Summary, Responsibilities, Qualifications

Author: ISD Team
Version: 1.0
Last Updated: 2024-11-26
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import time
import json
import re
from html import unescape
import argparse


class QualcommCareersScraper:
    """
    Qualcomm Careers Scraper
    
    This class scrapes job listings from Qualcomm Careers website.
    It uses the Eightfold AI API which powers the careers page.
    
    API Endpoints:
    - List API: GET /api/apply/v2/jobs?domain=qualcomm.com
    - Detail API: GET /api/apply/v2/jobs/{position_id}?domain=qualcomm.com
    
    No authentication required - public API.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the scraper.
        
        Args:
            verbose: Whether to print progress messages
        """
        self.base_url = "https://careers.qualcomm.com/api/apply/v2/jobs"
        self.domain = "qualcomm.com"
        self.session = requests.Session()
        self.verbose = verbose
        
        # Standard browser headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Referer': 'https://careers.qualcomm.com/careers',
        }
        self.session.headers.update(self.headers)
        
        # Data storage
        self.all_positions = []
        self.all_departments = set()
        self.failed_requests = 0
    
    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def fetch_jobs(self, start: int = 0, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch job listings from the list API.
        
        Args:
            start: Starting position (offset)
            limit: Number of jobs to fetch per request
        
        Returns:
            JSON response containing job listings
        """
        url = f"{self.base_url}?domain={self.domain}&start={start}&num={limit}&sort_by=relevance"
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"   [ERROR] HTTP {response.status_code}")
                self.failed_requests += 1
                return {}
        except requests.exceptions.RequestException as e:
            self.log(f"   [ERROR] Request failed: {str(e)}")
            self.failed_requests += 1
            return {}
    
    def fetch_job_detail(self, position_id: int) -> Dict[str, Any]:
        """
        Fetch detailed information for a single job.
        
        Args:
            position_id: The position ID from the list API
        
        Returns:
            JSON response containing job details
        """
        url = f"{self.base_url}/{position_id}?domain={self.domain}"
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                self.failed_requests += 1
                return {}
        except requests.exceptions.RequestException as e:
            self.failed_requests += 1
            return {}
    
    def clean_html(self, html: str) -> str:
        """
        Remove HTML tags and clean up text.
        
        Args:
            html: HTML string to clean
        
        Returns:
            Plain text without HTML tags
        """
        if not html:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Decode HTML entities
        text = unescape(text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_section(self, html: str, start_pattern: str, end_patterns: List[str]) -> str:
        """
        Extract a specific section from HTML content.
        
        Args:
            html: Full HTML content
            start_pattern: Regex pattern for section start
            end_patterns: List of regex patterns that mark section end
        
        Returns:
            Extracted text content
        """
        if not html:
            return ""
        
        # Find start position
        start_match = re.search(start_pattern, html, re.IGNORECASE | re.DOTALL)
        if not start_match:
            return ""
        
        start_pos = start_match.end()
        
        # Find end position (next section)
        end_pos = len(html)
        for end_pattern in end_patterns:
            end_match = re.search(end_pattern, html[start_pos:], re.IGNORECASE | re.DOTALL)
            if end_match:
                end_pos = min(end_pos, start_pos + end_match.start())
        
        section_html = html[start_pos:end_pos]
        return self.clean_html(section_html)
    
    def parse_job_description(self, html: str) -> Dict[str, str]:
        """
        Parse job_description HTML and extract structured sections.
        
        The HTML typically contains these sections:
        - Company
        - Job Area
        - General Summary
        - Job Responsibilities
        - Minimum Qualifications
        - Preferred Qualifications
        - Educational Requirements
        
        Args:
            html: The job_description HTML from the API
        
        Returns:
            Dictionary with extracted sections
        """
        result = {
            'company': '',
            'job_area': '',
            'general_summary': '',
            'responsibilities': '',
            'minimum_qualifications': '',
            'preferred_qualifications': '',
            'educational_requirements': '',
        }
        
        if not html:
            return result
        
        # Section markers used to detect end of each section
        section_markers = [
            r'<h2[^>]*>.*?Company',
            r'<h2[^>]*>.*?Job Area',
            r'<[ub]><b>General Summary',
            r'<b[^>]*>.*?Job responsibilities',
            r'<b[^>]*>.*?Minimum Qualifications',
            r'<b[^>]*>.*?Preferred Qualifications',
            r'<b[^>]*>.*?Educational Requirements',
            r'<b[^>]*>.*?To all Staffing',
            r'Qualcomm is an equal opportunity',
        ]
        
        # Extract each section
        result['company'] = self.extract_section(
            html,
            r'<h2[^>]*>.*?<b>Company:?</b>.*?</h2>',
            section_markers
        )
        
        result['job_area'] = self.extract_section(
            html,
            r'<h2[^>]*>.*?<b>Job Area:?</b>.*?</h2>',
            section_markers
        )
        
        result['general_summary'] = self.extract_section(
            html,
            r'<[ub]><b>General Summary:?</b></[ub]>',
            section_markers
        )
        
        result['responsibilities'] = self.extract_section(
            html,
            r'<b[^>]*>.*?Job responsibilities.*?:?</b>',
            section_markers
        )
        
        result['minimum_qualifications'] = self.extract_section(
            html,
            r'<[ub]><b>Minimum Qualifications:?</b></[ub]>',
            section_markers
        )
        
        result['preferred_qualifications'] = self.extract_section(
            html,
            r'<b[^>]*>Preferred Qualifications:?</b>',
            section_markers
        )
        
        result['educational_requirements'] = self.extract_section(
            html,
            r'<b[^>]*>Educational Requirements:?</b>',
            section_markers
        )
        
        return result
    
    def get_total_count(self) -> int:
        """
        Get total number of job listings.
        
        Returns:
            Total count of available jobs
        """
        self.log("\n[Step 1] Getting total job count...")
        data = self.fetch_jobs(start=0, limit=1)
        if not data:
            self.log("   [ERROR] Failed to get data")
            return 0
        total = data.get('count', 0)
        self.log(f"   [OK] Total jobs: {total}")
        return total
    
    def scrape_job_list(self) -> List[Dict]:
        """
        Scrape all job listings (basic info only).
        
        Returns:
            List of job positions
        """
        total_count = self.get_total_count()
        if total_count == 0:
            return []
        
        self.log(f"\n[Step 2] Scraping {total_count} job listings...")
        
        batch_size = 50
        start = 0
        seen_ids = set()
        batch_num = 1
        
        while start < total_count:
            remaining = total_count - start
            current_batch = min(batch_size, remaining)
            
            self.log(f"   Batch {batch_num} (jobs {start+1}-{start+current_batch})...", )
            
            data = self.fetch_jobs(start=start, limit=batch_size)
            
            if not data:
                self.log("   Retrying...")
                time.sleep(2)
                continue
            
            positions = data.get('positions', [])
            
            if not positions:
                self.log("   No more data")
                break
            
            new_count = 0
            for pos in positions:
                pos_id = pos.get('id')
                if pos_id and pos_id not in seen_ids:
                    seen_ids.add(pos_id)
                    self.all_positions.append(pos)
                    new_count += 1
                    
                    dept = pos.get('department')
                    if dept:
                        self.all_departments.add(dept)
            
            self.log(f"   [OK] Added {new_count}, Total: {len(self.all_positions)}")
            
            start += len(positions)
            batch_num += 1
            time.sleep(0.3)  # Rate limiting
        
        self.log(f"\n   [DONE] List scraping complete: {len(self.all_positions)} jobs")
        return self.all_positions
    
    def scrape_job_details(self, limit: Optional[int] = None) -> None:
        """
        Scrape detailed information for each job.
        
        This calls the detail API for each job to get full description,
        then parses the HTML to extract structured sections.
        
        Args:
            limit: Maximum number of details to fetch (for testing)
        """
        total = len(self.all_positions)
        if limit:
            total = min(total, limit)
        
        self.log(f"\n[Step 3] Scraping details for {total} jobs...")
        self.log("   (This may take several minutes)")
        
        for i, pos in enumerate(self.all_positions[:total]):
            pos_id = pos.get('id')
            if not pos_id:
                continue
            
            # Progress update every 50 jobs
            if (i + 1) % 50 == 0 or i == 0:
                self.log(f"   Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
            
            detail = self.fetch_job_detail(pos_id)
            
            if detail:
                job_desc = detail.get('job_description', '')
                parsed = self.parse_job_description(job_desc)
                
                # Add parsed fields to position data
                pos['detail_company'] = parsed['company']
                pos['detail_job_area'] = parsed['job_area']
                pos['general_summary'] = parsed['general_summary']
                pos['responsibilities'] = parsed['responsibilities']
                pos['minimum_qualifications'] = parsed['minimum_qualifications']
                pos['preferred_qualifications'] = parsed['preferred_qualifications']
                pos['educational_requirements'] = parsed['educational_requirements']
            
            time.sleep(0.2)  # Rate limiting
        
        self.log(f"   [DONE] Detail scraping complete")
    
    def build_dataframe(self) -> pd.DataFrame:
        """
        Convert job data to pandas DataFrame.
        
        Returns:
            DataFrame with all job information
        """
        self.log("\n[Step 4] Building output data...")
        
        jobs = []
        
        for pos in self.all_positions:
            # Parse location
            location = pos.get('location', '')
            location_parts = [p.strip() for p in location.split(',')] if location else []
            
            city = location_parts[0] if len(location_parts) >= 1 else None
            region = location_parts[1] if len(location_parts) >= 2 else None
            country = location_parts[2] if len(location_parts) >= 3 else None
            
            # Parse timestamp
            t_create = pos.get('t_create')
            created_date = None
            if t_create:
                try:
                    created_date = datetime.fromtimestamp(t_create).strftime('%Y-%m-%d')
                except:
                    pass
            
            job = {
                # Basic fields from list API
                'job_id': pos.get('ats_job_id') or pos.get('display_job_id'),
                'position_id': pos.get('id'),
                'title': pos.get('name'),
                'url': pos.get('canonicalPositionUrl'),
                'department': pos.get('department'),
                'business_unit': pos.get('business_unit'),
                'location': location,
                'city': city,
                'region': region,
                'country': country,
                'work_type': pos.get('work_location_option'),
                'created_date': created_date,
                # Detail fields from detail API
                'company': pos.get('detail_company', ''),
                'job_area': pos.get('detail_job_area', ''),
                'general_summary': pos.get('general_summary', ''),
                'responsibilities': pos.get('responsibilities', ''),
                'minimum_qualifications': pos.get('minimum_qualifications', ''),
                'preferred_qualifications': pos.get('preferred_qualifications', ''),
                'educational_requirements': pos.get('educational_requirements', ''),
            }
            jobs.append(job)
        
        df = pd.DataFrame(jobs)
        
        # Sort by department and title
        if 'department' in df.columns:
            df = df.sort_values(['department', 'title'])
        
        self.log(f"   [DONE] {len(df)} jobs processed")
        
        return df
    
    def save_to_excel(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Save data to Excel file.
        
        Args:
            df: DataFrame to save
            filename: Output filename (auto-generated if not provided)
        
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qualcomm_careers_{timestamp}.xlsx"
        
        df.to_excel(filename, index=False)
        self.log(f"\n[OUTPUT] Excel saved: {filename}")
        
        return filename
    
    def save_to_json(self, filename: Optional[str] = None) -> str:
        """
        Save raw data to JSON file.
        
        Args:
            filename: Output filename (auto-generated if not provided)
        
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qualcomm_careers_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'positions': self.all_positions,
                'departments': list(self.all_departments),
                'count': len(self.all_positions),
                'scraped_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        self.log(f"[OUTPUT] JSON saved: {filename}")
        
        return filename
    
    def print_summary(self, df: pd.DataFrame):
        """Print summary statistics."""
        self.log("\n" + "="*60)
        self.log("SCRAPING SUMMARY")
        self.log("="*60)
        
        self.log(f"\nTotal Jobs: {len(df)}")
        self.log(f"Departments: {len(self.all_departments)}")
        self.log(f"Failed Requests: {self.failed_requests}")
        
        # Detail field fill rates
        detail_fields = ['company', 'job_area', 'general_summary', 'responsibilities', 
                         'minimum_qualifications', 'preferred_qualifications']
        self.log(f"\nDetail Field Fill Rates:")
        for field in detail_fields:
            if field in df.columns:
                filled = df[field].notna() & (df[field] != '')
                rate = filled.sum() / len(df) * 100
                self.log(f"   {field}: {rate:.1f}%")
    
    def run(self, fetch_details: bool = True, detail_limit: Optional[int] = None, 
            output_excel: Optional[str] = None, output_json: Optional[str] = None) -> pd.DataFrame:
        """
        Run the complete scraping process.
        
        Args:
            fetch_details: Whether to fetch detail pages (slower but more data)
            detail_limit: Limit number of details to fetch (for testing)
            output_excel: Custom Excel filename
            output_json: Custom JSON filename
        
        Returns:
            DataFrame with all scraped data
        """
        self.log("="*60)
        self.log("QUALCOMM CAREERS SCRAPER")
        self.log("="*60)
        self.log(f"Platform: Eightfold AI")
        self.log(f"Website: https://careers.qualcomm.com")
        self.log(f"Fetch Details: {'Yes' if fetch_details else 'No'}")
        if detail_limit:
            self.log(f"Detail Limit: {detail_limit}")
        
        # Step 1-2: Scrape job list
        self.scrape_job_list()
        
        # Step 3: Scrape details (optional)
        if fetch_details:
            self.scrape_job_details(limit=detail_limit)
        
        # Step 4: Build DataFrame
        df = self.build_dataframe()
        
        # Save outputs
        self.save_to_excel(df, output_excel)
        self.save_to_json(output_json)
        
        # Print summary
        self.print_summary(df)
        
        self.log("\n" + "="*60)
        self.log("SCRAPING COMPLETE!")
        self.log("="*60)
        
        return df


def main():
    """
    Main entry point with command line argument support.
    
    Usage:
        # Full scrape with details
        python qualcomm_careers_scraper.py
        
        # Quick scrape (list only, no details)
        python qualcomm_careers_scraper.py --no-details
        
        # Test mode (only 10 job details)
        python qualcomm_careers_scraper.py --test
        
        # Custom output filename
        python qualcomm_careers_scraper.py --output my_output.xlsx
    """
    parser = argparse.ArgumentParser(
        description='Qualcomm Careers Scraper - Extract job listings from Qualcomm Careers website'
    )
    parser.add_argument(
        '--no-details', 
        action='store_true',
        help='Skip fetching job details (faster, but less data)'
    )
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Test mode - only fetch details for first 10 jobs'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output Excel filename (default: auto-generated with timestamp)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - suppress progress messages'
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = QualcommCareersScraper(verbose=not args.quiet)
    
    # Determine settings
    fetch_details = not args.no_details
    detail_limit = 10 if args.test else None
    
    # Run scraper
    df = scraper.run(
        fetch_details=fetch_details,
        detail_limit=detail_limit,
        output_excel=args.output
    )
    
    return df


if __name__ == "__main__":
    main()

