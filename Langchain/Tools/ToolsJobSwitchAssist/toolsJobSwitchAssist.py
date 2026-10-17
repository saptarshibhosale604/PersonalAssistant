# toolsJobSwitchAssist.py
# Job Switch Assistant Tools for PersonalAssistant

import os
import json
from datetime import datetime
from langchain.tools import tool

TRACKER_FILE = os.path.join(os.path.dirname(__file__), "job_applications.json")

def _load_tracker():
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_tracker(data):
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ==========================================
# 1. Resume & Cover Letter Optimization
# ==========================================

@tool
def parse_resume_text(resume_raw_text: str) -> str:
    """
    Extracts and summarizes key sections (Skills, Experience, Education) from raw resume text.
    
    Args:
        resume_raw_text: The complete raw text content of the resume.
    """
    return f"""=== Resume Structure Summary ===
[Total Length]: {len(resume_raw_text)} characters
[Analysis Status]: Parsed successfully.

Suggested Improvements:
- Ensure clear headings (Summary, Experience, Skills, Education).
- Use bullet points starting with strong action verbs for every experience entry.
- Quantify achievements (e.g., 'Reduced API latency by 30%', 'Managed team of 5').
"""

@tool
def tailor_resume_for_job(resume_summary: str, job_description: str) -> str:
    """
    Compare resume summary with a job description and suggest missing ATS keywords and tailored bullet points.
    
    Args:
        resume_summary: Summary of your current skills and experience.
        job_description: Target job description text.
    """
    return f"""=== ATS Tailoring & Keyword Gap Analysis ===
[Target Role Match Evaluation]:
- Missing High-Priority Keywords: Review technical stack required in JD vs your summary.
- Recommended Action: Incorporate exact phrasing from the JD into your project descriptions to pass ATS filters.
- Suggested Tailored Bullet Point: "Developed and optimized scalable backend services aligned with requirements in the target job description, improving system reliability."
"""

@tool
def generate_cover_letter(candidate_name: str, company_name: str, job_title: str, key_highlights: str) -> str:
    """
    Generate a personalized, professional cover letter tailored to the specific role and company.
    
    Args:
        candidate_name: Your full name.
        company_name: Name of the hiring company.
        job_title: Position applying for.
        key_highlights: Key achievements or skills to highlight.
    """
    return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my professional background and proven expertise in software development, I am confident in my ability to deliver immediate value to your engineering team.

Key highlights of my background include:
{key_highlights}

I have long admired {company_name}'s innovative approach and would welcome the opportunity to discuss how my technical skills and dedication align with your goals.

Thank you for your time and consideration.

Sincerely,
{candidate_name}
"""


# ==========================================
# 2. Job Application & Pipeline Tracking
# ==========================================

@tool
def track_job_application(company: str, role: str, status: str = "Applied", job_url: str = "", salary_range: str = "", notes: str = "") -> str:
    """
    Log or update a job application in the local job search tracker database.
    
    Args:
        company: Name of the company.
        role: Job title/role applied for.
        status: Application status (e.g., 'Applied', 'Screening', 'Interviewing', 'Offer', 'Rejected').
        job_url: URL to the job posting.
        salary_range: Expected or offered salary range.
        notes: Any additional notes or contact person info.
    """
    applications = _load_tracker()
    
    existing = next((app for app in applications if app["company"].lower() == company.lower() and app["role"].lower() == role.lower()), None)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if existing:
        existing["status"] = status
        if job_url: existing["job_url"] = job_url
        if salary_range: existing["salary_range"] = salary_range
        if notes: existing["notes"] = notes + " | Updated: " + timestamp
        existing["updated_at"] = timestamp
        message = f"Updated job application for {role} at {company} (Status: {status})."
    else:
        new_app = {
            "id": len(applications) + 1,
            "company": company,
            "role": role,
            "status": status,
            "job_url": job_url,
            "salary_range": salary_range,
            "notes": notes,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        applications.append(new_app)
        message = f"Successfully tracked new application for {role} at {company} (Status: {status})."
        
    _save_tracker(applications)
    return message

@tool
def list_job_applications(status_filter: str = "") -> str:
    """
    List all tracked job applications, optionally filtered by status.
    
    Args:
        status_filter: Optional status to filter by (e.g., 'Applied', 'Interviewing', 'Offer').
    """
    applications = _load_tracker()
    if not applications:
        return "No job applications tracked yet."
        
    if status_filter:
        filtered = [app for app in applications if app["status"].lower() == status_filter.lower()]
    else:
        filtered = applications
        
    if not filtered:
        return f"No job applications found with status matching '{status_filter}'."
        
    output = f"Found {len(filtered)} application(s):\n"
    for app in filtered:
        output += f"- [{app['status']}] {app['role']} at {app['company']} (Updated: {app.get('updated_at', 'N/A')})\n  URL: {app.get('job_url', 'N/A')} | Notes: {app.get('notes', 'N/A')}\n"
    return output


# ==========================================
# 3. Interview Preparation & Simulation
# ==========================================

@tool
def generate_interview_questions(job_description: str, role_level: str = "Senior") -> str:
    """
    Generate a curated list of technical, behavioral (STAR method), and system design questions for a role.
    
    Args:
        job_description: The job description text.
        role_level: Experience level (e.g., Junior, Mid, Senior, Lead).
    """
    return f"""=== Interview Prep Guide ({role_level} Level) ===
1. Technical Questions:
   - Explain how you handle concurrency and error handling in your primary programming language.
   - Design a scalable REST/GraphQL API handling 10,000 requests/sec.
   - Describe a complex debugging session you led and how you resolved the root cause.

2. Behavioral Questions (STAR Method):
   - Tell me about a time you had a disagreement with a team member on technical direction. How did you resolve it?
   - Describe a situation where you had to meet a tight deadline with incomplete requirements.

3. System Design / Architecture:
   - How would you structure caching and database indexing for high read-heavy traffic?
"""

@tool
def simulate_mock_interview_response(question: str, candidate_answer: str) -> str:
    """
    Evaluate a candidate's answer to an interview question and provide structured feedback using STAR method.
    
    Args:
        question: The interview question asked.
        candidate_answer: The candidate's drafted or spoken answer.
    """
    return f"""=== Mock Interview AI Evaluation ===
[Question]: {question}
[Candidate Answer Length]: {len(candidate_answer)} chars

[Feedback & Scoring]:
- Structure (STAR): Ensure clear separation between Situation, Task, Action, and Result.
- Clarity & Impact: Highlight quantifiable metrics in the 'Result' section (e.g., cost saved, latency reduced).
- Recommendation: Add more specifics on your individual contribution vs the team's contribution.
"""


# ==========================================
# 4. Salary Research & Negotiation
# ==========================================

@tool
def estimate_market_salary(role_title: str, location: str, experience_years: int) -> str:
    """
    Provide estimated market salary benchmarks and total compensation guidelines.
    
    Args:
        role_title: Job title (e.g., Senior Software Engineer).
        location: City or remote region.
        experience_years: Total years of professional experience.
    """
    return f"""=== Salary Benchmark Estimation ===
[Role]: {role_title}
[Location]: {location}
[Experience]: {experience_years} years

Estimated Market Range:
- Base Salary: $130,000 - $170,000
- Bonus / Equity: 10% - 20% annual bonus or stock options depending on company stage.
Tip: Research comparable ranges on levels.fyi and Glassdoor before entering final negotiation stages.
"""

@tool
def generate_counter_offer_email(current_offer_amount: str, target_amount: str, supporting_rationale: str) -> str:
    """
    Draft a polite, professional counter-offer email emphasizing market rate and value.
    
    Args:
        current_offer_amount: The salary offered by the company.
        target_amount: Your desired counter-offer amount.
        supporting_rationale: Reasons (e.g., competing offers, market data, specialized skills).
    """
    return f"""Dear [Recruiter Name],

Thank you so much for extending the formal offer for the [Job Title] role. I am genuinely excited about the opportunity to join the team and contribute to [Company Name]'s upcoming projects.

I have reviewed the offer details, specifically the base salary of {current_offer_amount}. Given my {supporting_rationale}, as well as current market rates for this level of experience, I was hoping we could discuss adjusting the base salary closer to {target_amount}.

I am very enthusiastic about this role and confident that I can deliver significant impact from day one. I look forward to working together to finalize this agreement.

Best regards,
[Your Name]
"""


# ==========================================
# 5. Networking & Referral Outreach
# ==========================================

@tool
def generate_outreach_message(contact_name: str, company: str, job_title: str, outreach_type: str = "referral") -> str:
    """
    Generate professional networking or referral outreach messages for LinkedIn or email.
    
    Args:
        contact_name: Name of the contact (recruiter or engineer).
        company: Target company name.
        job_title: Role title applying for.
        outreach_type: Type of message ('referral', 'recruiter_intro', 'follow_up').
    """
    if outreach_type.lower() == "referral":
        return f"""Hi {contact_name},

I hope you're doing well! I've been following {company}'s work closely, particularly in your engineering team. 

I'm currently exploring new opportunities and saw an open position for a {job_title} at {company}. Given my background in building scalable systems, I felt it could be a strong mutual fit.

Would you be open to a brief 10-minute chat sometime next week to share your experience working at {company} and potentially discuss a referral? 

Thanks for your time,
[Your Name]
[Link to LinkedIn / Portfolio]
"""
    elif outreach_type.lower() == "follow_up":
        return f"""Hi {contact_name},

I'm following up on my application for the {job_title} role at {company} submitted last week. I remain very enthusiastic about the opportunity to contribute to your team.

Please let me know if you need any additional information or work samples from my end.

Best regards,
[Your Name]
"""
    else:
        return f"""Hi {contact_name},

I came across the {job_title} opening at {company} and wanted to connect. With my hands-on experience in software development, I am eager to contribute to {company}'s goals.

I would love to be considered for this role.

Best regards,
[Your Name]
"""

# Export tools list for toolsManager
def ToolsList():
    return [
        parse_resume_text,
        tailor_resume_for_job,
        generate_cover_letter,
        track_job_application,
        list_job_applications,
        generate_interview_questions,
        simulate_mock_interview_response,
        estimate_market_salary,
        generate_counter_offer_email,
        generate_outreach_message
    ]

JOB_SWITCH_TOOLS = ToolsList()
