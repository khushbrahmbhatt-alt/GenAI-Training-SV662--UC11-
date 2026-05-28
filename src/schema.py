from pydantic import BaseModel, Field
from typing import List, Optional

class Location(BaseModel):
    city: Optional[str] = Field(description="City of the institution or company")
    country: Optional[str] = Field(description="Country of the institution or company")

class PersonalDetails(BaseModel):
    full_name: str = Field(description="Candidate's full name")
    headline: Optional[str] = Field(description="Professional headline or title")
    nationality: Optional[str] = Field(description="Candidate's nationality")
    date_of_birth: Optional[str] = Field(description="Format YYYY-MM-DD")
    marital_status: Optional[str] = Field(description="Marital status")
    current_country: Optional[str] = Field(description="Country of current residence")

class ContactInformation(BaseModel):
    email: Optional[str] = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number with country code if available")
    linkedin: Optional[str] = Field(description="LinkedIn profile URL")

class WorkExperience(BaseModel):
    company_name: str = Field(description="Name of the employer")
    job_title: str = Field(description="Job title held")
    location: Optional[Location] = Field(description="Location of the job")
    start_date: Optional[str] = Field(description="Format YYYY-MM")
    end_date: Optional[str] = Field(description="Format YYYY-MM, or null if currently employed")
    is_current: bool = Field(description="True if this is the current job, False otherwise")
    employment_type: Optional[str] = Field(description="E.g., Full-time, Internship, Contract")
    responsibilities: List[str] = Field(description="List of key responsibilities and achievements")

class Education(BaseModel):
    institution: str = Field(description="Name of the university or institution")
    degree: str = Field(description="Name of the degree or program")
    location: Optional[Location] = Field(description="Location of the institution")
    start_date: Optional[str] = Field(description="Format YYYY-MM")
    end_date: Optional[str] = Field(description="Format YYYY-MM")

class DerivedInsights(BaseModel):
    total_experience_years: float = Field(description="Total calculated years of professional experience")
    management_experience: bool = Field(description="True if the candidate has managed people or teams")
    international_experience: bool = Field(description="True if the candidate has worked in multiple countries")
    job_gaps: List[str] = Field(description="List of identified gaps in employment history, empty list if none")
    top_5_skills: List[str] = Field(description="The top 5 skills highly relevant to the specific job role being evaluated")

class AtsScoring(BaseModel):
    profile_score: float = Field(description="A score between 0.0 and 1.0 evaluating the candidate for the role")
    confidence_factors: List[str] = Field(description="List of reasons supporting the profile score")

class Metadata(BaseModel):
    file_name: str = Field(description="The original name of the parsed file")
    extraction_confidence: float = Field(description="Overall confidence score of the LLM extraction between 0.0 and 1.0")
    role: str = Field(description="The target job role the resume is being evaluated against (e.g., Architect, Arts, Civil Engineer, Consultant, Accountant)")

class ResumeExtractionSchema(BaseModel):
    """The master schema for the entire resume extraction and analysis output."""
    personal_details: PersonalDetails
    contact_information: ContactInformation
    professional_summary: Optional[str] = Field(description="A brief professional summary of the candidate")
    work_experience: List[WorkExperience]
    education: List[Education]
    skills: List[str] = Field(description="List of all technical and soft skills extracted")
    languages: List[str] = Field(description="List of spoken and written languages")
    derived_insights: DerivedInsights
    ats_scoring: AtsScoring
    metadata: Metadata