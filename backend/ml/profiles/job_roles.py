"""
A curated dictionary of job role profiles.
These profiles use descriptive natural language rather than pure keywords.
When embedded by the Transformer, this natural language yields a much richer semantic 
representation of the responsibilities and skills required for the role, 
which can then be compared against a user's resume embedding.
"""

JOB_ROLE_PROFILES = {
    "Software Engineer": (
        "A software engineer who designs, develops, and maintains software applications. "
        "Familiar with multiple programming languages such as Python, Java, or C++. "
        "Experience with version control (Git), software development lifecycles, debugging, "
        "and building scalable systems. Collaborates closely with product and design teams."
    ),
    "Data Scientist": (
        "A data scientist specializing in analyzing complex data to drive business decisions. "
        "Highly proficient in Python, Pandas, NumPy, and SQL. Uses statistical analysis, "
        "data visualization, and machine learning techniques to uncover insights. "
        "Experience with A/B testing and predictive modeling."
    ),
    "Machine Learning Engineer": (
        "An engineer focused on researching, building, and deploying machine learning models "
        "into production environments. Proficient in deep learning frameworks like TensorFlow "
        "and PyTorch. Strong software engineering skills in Python, and familiarity with "
        "MLOps practices, Docker, and cloud platforms like AWS or Azure."
    ),
    "Backend Developer": (
        "A backend developer responsible for server-side web application logic and integration. "
        "Builds robust APIs using frameworks like FastAPI, Django, or Spring Boot. "
        "Strong knowledge of database systems like PostgreSQL or MySQL. Focused on security, "
        "performance optimization, and scalable microservices architecture."
    ),
    "Frontend Developer": (
        "A frontend developer who builds interactive, accessible, and responsive user interfaces. "
        "Expert in HTML, CSS, JavaScript, and TypeScript. Extensive experience with modern "
        "frameworks like React or Vue.js. Understands UI/UX principles and consumes RESTful APIs."
    )
}

def get_role_profile(role_name: str) -> str:
    """Retrieve the natural language profile for a given role name."""
    profile = JOB_ROLE_PROFILES.get(role_name)
    if not profile:
        raise ValueError(f"Job role '{role_name}' is not currently supported.")
    return profile
