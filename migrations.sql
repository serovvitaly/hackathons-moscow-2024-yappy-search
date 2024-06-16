CREATE TABLE public.videos (
	id bigserial NOT NULL,
	link varchar NOT NULL,
	description varchar NULL,
	speech text NULL,
	pid int4 NULL,
	likes int4 NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT videos_link UNIQUE (link)
);
