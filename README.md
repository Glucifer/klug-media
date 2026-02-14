Klug Media
Klug Media is a self-hosted media tracking and analytics platform.
It is designed as a full replacement for third-party tracking services, providing complete ownership of watch history, metadata, analytics, and integrations.
The system supports movies and TV, with a database-first architecture and API integrations for metadata and automation.
________________________________________
Goals
•	Full ownership of watch history and collection data
•	Advanced analytics and reporting
•	API-driven integrations (Radarr, Sonarr, Jellyfin, etc.)
•	Modular and extensible architecture
•	Clean internal schema without legacy naming constraints
•	Exportable and portable data
________________________________________
Architecture (Planned)
Backend
•	Python (FastAPI or Flask TBD)
•	REST API
•	Background workers for sync tasks
Database
•	postegresql
•	Clean schema with normalized tables
•	Views for reporting and analytics
Integrations
•	TMDB API
•	Jellyfin webhook sync
•	Radarr/Sonarr list import
•	Optional Trakt import (one-time migration)
Frontend (Phase 2)
•	Web dashboard
•	Statistics & visualizations
•	Manual watch logging
•	List management
________________________________________
Core Features (Phase 1)
•	User accounts
•	Watch logging (movies & TV episodes)
•	Ratings
•	Collection tracking
•	Metadata enrichment (TMDB)
•	Import existing watch history
•	API-first design
________________________________________
Planned Features (Phase 2+)
•	Advanced analytics dashboard
•	Custom lists
•	Tagging system
•	Smart filters
•	CSV export
•	Yearly statistics
•	Automated backups
•	HorrorFest tracking module

Database Design Philosophy
•	No external service naming in schema
•	Clear, concise table names (klug_user, media_item, watch_log)
•	Strict foreign key relationships
•	Views used for reporting, not application logic
•	All timestamps stored in UTC

Roadmap
•	Define database schema
•	Implement core models
•	Build watch logging API
•	TMDB metadata sync
•	Import legacy data
•	Basic CLI interface
•	Web frontend MVP

Philosophy

Klug Media exists to provide clarity, ownership, and flexibility in media tracking.

No feature restrictions.
No data lock-in.
No subscription volatility.

Just structured data, clean design, and long-term control.