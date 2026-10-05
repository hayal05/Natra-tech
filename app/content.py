"""Static site content. Kept as data so pages stay clean and can move to the database later."""

COMPANY = {
    "name": "Natra Technology",
    "email": "hello@company.com",
    "phone": "+251 988 416 048",
    "location": "Addis Ababa, Ethiopia",
    "socials": [("LinkedIn", "#"), ("GitHub", "#"), ("Telegram", "#")],
}

SERVICES = [
    ("01", "Software Development", "Digital products built for scale.",
     "Web platforms, APIs and internal tools engineered to stay fast and maintainable as you grow."),
    ("02", "AI & Automation", "Intelligent systems for modern businesses.",
     "Practical AI that removes repetitive work and turns your data into decisions."),
    ("03", "Digital Experiences", "Interfaces people remember.",
     "Product design and front-end craft focused on clarity, speed and detail."),
    ("04", "Cloud & Infrastructure", "Reliable systems for modern companies.",
     "Secure, monitored deployments with the uptime your customers expect."),
]

PROJECTS = [
    {"name": "Project One", "tags": "Web / Software", "year": "2026", "variant": "a"},
    {"name": "Project Two", "tags": "AI / Automation", "year": "2025", "variant": "b"},
    {"name": "Project Three", "tags": "Cloud / Infrastructure", "year": "2025", "variant": "c"},
]

STATS = [("50+", "Projects delivered"), ("8", "Years of experience"), ("99.9%", "Uptime target")]

VALUES = [
    ("Craft", "We sweat the details because users feel them."),
    ("Clarity", "Simple systems, honest communication, no noise."),
    ("Ownership", "We build like it is our own product."),
]
