# IgniteXT-E-Learning-Content-Management-
IgniteXT is an E-Learning Content Management System (CMS) designed to simplify the management and distribution of educational materials. It enables faculty to upload files and video lectures for students to access. Additionally, a built-in chatbot assists students in resolving queries, streamlining the learning process.



**Purpose and Scope**
This document provides a comprehensive overview of the IgniteXT E-Learning Content Management System, covering its core functionality, architecture, and user roles. IgniteXT is designed to facilitate educational content distribution from faculty to students through a web-based platform with integrated AI assistance.

For detailed backend implementation including Flask routes and database operations, see Backend Implementation. For frontend interfaces and styling components, see Frontend Implementation. For system architecture details, see System Architecture.

**System Description**

IgniteXT is a web-based E-Learning Content Management System built on Flask that enables educational institutions to manage and distribute learning materials. The system implements a dual-user architecture where faculty members can upload and manage educational content, while students can access, download, and interact with these materials.

The platform includes an AI-powered chatbot integration using Google Gemini to assist students with learning queries, making it a comprehensive solution for modern educational environments.



**User Role Architecture**

The system implements a strict role-based access control system with separated database storage and distinct permission sets:

Role-Based System Design

**Key Technical Components**

The IgniteXT system consists of several interconnected technical components that work together to provide the e-learning platform functionality:

Component ||	Technology ||	Purpose ||	Key Files
Web Framework	|| Flask	HTTP request handling, routing, session management ||	app.py
Database	|| MongoDB	User data, course content, and file metadata storage ||	CRV and TRV databases
Authentication	|| bcrypt + Flask sessions	Secure user login and role-based access control ||	app.py authentication routes
AI Integration	|| Google Gemini API	Intelligent chatbot assistance for students	 || config.py GEMINI_API_KEY
File Storage	|| Local filesystem	Educational content and media file storage	|| uploads/ directory
Configuration	|| Environment variables	External service keys and database connections	|| config.py

**User Interface Components**
The system provides role-specific interfaces through a comprehensive CSS framework and JavaScript interactions:

Interface Type	Target Users	Key Styling	Functionality
Authentication	All users	css/auth.css	Login/registration with role selection
Dashboard	All users	css/dashboard.css	Personalized user home interface
Course Management	Faculty/Students	css/courses.css, css/playlist.css	Content organization and access
Content Upload	Faculty only	css/upload.css	File and video upload interface
Video Viewing	All users	css/watchvideo.css	Video playback with comments
AI Chatbot	Students	css/chatbot.css	Interactive AI assistance
File Downloads	Students	css/download.css	Educational resource access
External Service Integration
IgniteXT integrates with external services to provide enhanced functionality:

MongoDB Atlas: Cloud database hosting for scalable data storage via MONGODB_URI configuration
Google Gemini AI: Advanced chatbot capabilities through GEMINI_API_KEY integration
bcrypt Library: Industry-standard password hashing for user security
These integrations are managed through the configuration system in config.py and accessed throughout the Flask application in app.py.
