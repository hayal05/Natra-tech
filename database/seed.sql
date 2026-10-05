-- Optional sample jobs for testing. Safe to run more than once.
INSERT INTO jobs (title, slug, description, responsibilities, requirements, location, employment_type, status) VALUES
('Frontend Developer', 'frontend-developer', 'Build fast, beautiful interfaces for our client products.',
 E'Ship responsive UI\nCollaborate with designers\nKeep performance high', E'2+ years of HTML, CSS and JavaScript\nEye for detail', 'Addis Ababa', 'Full Time', 'published'),
('Python Developer', 'python-developer', 'Design and build reliable backend services and APIs.',
 E'Build Flask and API services\nModel data in PostgreSQL\nWrite clean, tested code', E'Strong Python skills\nExperience with SQL', 'Remote', 'Full Time', 'published'),
('UI/UX Designer', 'ui-ux-designer', 'Craft interfaces people remember.',
 E'Design flows and screens\nBuild design systems', E'Portfolio of product work\nFigma proficiency', 'Addis Ababa', 'Full Time', 'published')
ON CONFLICT (slug) DO NOTHING;
