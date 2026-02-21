--
-- PostgreSQL database dump
--

\restrict h5vCqRIUiSU3eNbbSxhckS1olOuDinH91iJdTmF0keoinSI2lv8SwZ3cyZ95qlq

-- Dumped from database version 18.2 (Debian 18.2-1.pgdg13+1)
-- Dumped by pg_dump version 18.2 (Debian 18.2-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: app; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA app;


--
-- Name: create_default_media_version(); Type: FUNCTION; Schema: app; Owner: -
--

CREATE FUNCTION app.create_default_media_version() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  INSERT INTO app.media_version (
    media_item_id,
    version_key,
    version_name
  )
  VALUES (
    NEW.media_item_id,
    'default',
    'Default/Theatrical'
  )
  ON CONFLICT (media_item_id, version_key) DO NOTHING;

  RETURN NEW;
END;
$$;


--
-- Name: set_watch_event_dedupe_hash(); Type: FUNCTION; Schema: app; Owner: -
--

CREATE FUNCTION app.set_watch_event_dedupe_hash() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  v_bucket timestamptz;
  v_payload text;
BEGIN
  IF NEW.dedupe_hash IS NULL OR NEW.dedupe_hash = '' THEN

    v_bucket := date_trunc('minute', NEW.watched_at);

    v_payload :=
      NEW.user_id::text || '|' ||
      NEW.media_item_id::text || '|' ||
      NEW.playback_source || '|' ||
      v_bucket::text || '|' ||
      COALESCE(NEW.media_version_id::text, '') || '|' ||
      COALESCE(NEW.completed::text, '') || '|' ||
      COALESCE(NEW.progress_percent::text, '') || '|' ||
      COALESCE(NEW.total_seconds::text, '') || '|' ||
      COALESCE(NEW.watched_seconds::text, '');

    NEW.dedupe_hash := encode(digest(v_payload, 'sha256'), 'hex');
  END IF;

  RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: import_batch; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.import_batch (
    import_batch_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source text NOT NULL,
    source_detail text,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    status text DEFAULT 'running'::text NOT NULL,
    watch_events_inserted integer DEFAULT 0 NOT NULL,
    media_items_inserted integer DEFAULT 0 NOT NULL,
    media_versions_inserted integer DEFAULT 0 NOT NULL,
    tags_added integer DEFAULT 0 NOT NULL,
    errors_count integer DEFAULT 0 NOT NULL,
    parameters jsonb DEFAULT '{}'::jsonb NOT NULL,
    notes text
);


--
-- Name: import_batch_error; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.import_batch_error (
    import_batch_error_id uuid DEFAULT gen_random_uuid() NOT NULL,
    import_batch_id uuid NOT NULL,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    severity text DEFAULT 'error'::text NOT NULL,
    entity_type text,
    entity_ref text,
    message text NOT NULL,
    details jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: media_item; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.media_item (
    media_item_id uuid DEFAULT gen_random_uuid() NOT NULL,
    type public.media_type NOT NULL,
    title text NOT NULL,
    year integer,
    tmdb_id integer,
    imdb_id text,
    tvdb_id integer,
    show_tmdb_id integer,
    season_number integer,
    episode_number integer,
    jellyfin_item_id text,
    kodi_item_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    base_runtime_seconds integer,
    metadata_source text,
    metadata_updated_at timestamp with time zone,
    show_id uuid
);


--
-- Name: media_version; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.media_version (
    media_version_id uuid DEFAULT gen_random_uuid() NOT NULL,
    media_item_id uuid NOT NULL,
    version_key public.citext NOT NULL,
    version_name text NOT NULL,
    runtime_seconds integer,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: shows; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.shows (
    show_id uuid DEFAULT gen_random_uuid() NOT NULL,
    tmdb_id integer NOT NULL,
    tvdb_id integer,
    imdb_id text,
    title text NOT NULL,
    year integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: tag; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.tag (
    tag_id uuid DEFAULT gen_random_uuid() NOT NULL,
    tag_key public.citext NOT NULL,
    description text,
    horrorfest_year integer GENERATED ALWAYS AS (
CASE
    WHEN ((tag_key)::text ~* '^horrorfest_[0-9]{4}$'::text) THEN ("right"((tag_key)::text, 4))::integer
    ELSE NULL::integer
END) STORED
);


--
-- Name: tmdb_metadata_cache; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.tmdb_metadata_cache (
    tmdb_type text NOT NULL,
    tmdb_id integer NOT NULL,
    sub_key text NOT NULL,
    payload jsonb NOT NULL,
    fetched_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    etag text,
    source_url text
);


--
-- Name: tmdb_movie_basic; Type: VIEW; Schema: app; Owner: -
--

CREATE VIEW app.tmdb_movie_basic AS
 SELECT tmdb_id,
    (payload ->> 'title'::text) AS title,
    ((payload ->> 'runtime'::text))::integer AS runtime_minutes,
    fetched_at
   FROM app.tmdb_metadata_cache
  WHERE ((tmdb_type = 'movie'::text) AND (sub_key IS NULL));


--
-- Name: users; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.users (
    user_id uuid DEFAULT gen_random_uuid() NOT NULL,
    username public.citext NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: watch_event; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.watch_event (
    watch_id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    media_item_id uuid NOT NULL,
    watched_at timestamp with time zone NOT NULL,
    playback_source text NOT NULL,
    total_seconds integer,
    watched_seconds integer,
    progress_percent numeric(5,2),
    completed boolean DEFAULT true NOT NULL,
    rating_value numeric(4,2),
    rating_scale text,
    import_batch_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    rewatch boolean DEFAULT false NOT NULL,
    media_version_id uuid,
    dedupe_hash text,
    created_by text,
    source_event_id text
);


--
-- Name: v_show_progress; Type: VIEW; Schema: app; Owner: -
--

CREATE VIEW app.v_show_progress AS
 WITH totals AS (
         SELECT mi.show_id,
            count(*) AS total_episodes
           FROM app.media_item mi
          WHERE ((mi.type = 'episode'::public.media_type) AND (mi.show_id IS NOT NULL))
          GROUP BY mi.show_id
        ), watched AS (
         SELECT we.user_id,
            mi.show_id,
            count(DISTINCT we.media_item_id) AS watched_episodes
           FROM (app.watch_event we
             JOIN app.media_item mi ON ((mi.media_item_id = we.media_item_id)))
          WHERE ((mi.type = 'episode'::public.media_type) AND (mi.show_id IS NOT NULL) AND (we.completed = true))
          GROUP BY we.user_id, mi.show_id
        )
 SELECT s.show_id,
    s.tmdb_id AS show_tmdb_id,
    s.title AS show_title,
    w.user_id,
    t.total_episodes,
    w.watched_episodes,
        CASE
            WHEN (t.total_episodes = 0) THEN (0)::numeric
            ELSE round((((w.watched_episodes)::numeric / (t.total_episodes)::numeric) * (100)::numeric), 2)
        END AS watched_percent
   FROM ((watched w
     JOIN totals t ON ((t.show_id = w.show_id)))
     JOIN app.shows s ON ((s.show_id = w.show_id)));


--
-- Name: watch_event_tag; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.watch_event_tag (
    watch_id uuid NOT NULL,
    tag_id uuid NOT NULL
);


--
-- Name: watch_event_enriched; Type: VIEW; Schema: app; Owner: -
--

CREATE VIEW app.watch_event_enriched AS
 WITH horrorfest_tags AS (
         SELECT wet.watch_id,
            min(t.horrorfest_year) AS horrorfest_year
           FROM (app.watch_event_tag wet
             JOIN app.tag t ON ((t.tag_id = wet.tag_id)))
          WHERE (t.horrorfest_year IS NOT NULL)
          GROUP BY wet.watch_id
        )
 SELECT w.watch_id,
    w.user_id,
    u.username,
    w.watched_at,
    (w.watched_at AT TIME ZONE 'America/Edmonton'::text) AS watched_local_ts,
    ((w.watched_at AT TIME ZONE 'America/Edmonton'::text))::date AS watched_local_date,
    (EXTRACT(year FROM (w.watched_at AT TIME ZONE 'America/Edmonton'::text)))::integer AS watched_local_year,
    (EXTRACT(month FROM (w.watched_at AT TIME ZONE 'America/Edmonton'::text)))::integer AS watched_local_month,
    w.playback_source,
    w.completed,
    w.rewatch,
    m.media_item_id,
    m.type AS media_type,
    m.title,
    m.year,
    m.tmdb_id,
    m.imdb_id,
    m.tvdb_id,
    m.show_tmdb_id,
    m.season_number,
    m.episode_number,
    m.jellyfin_item_id,
    m.kodi_item_id,
    w.media_version_id,
    COALESCE(v.version_key, 'default'::public.citext) AS version_key,
    COALESCE(v.version_name, 'Default/Theatrical'::text) AS version_name,
    COALESCE(v.runtime_seconds, w.total_seconds, m.base_runtime_seconds) AS effective_runtime_seconds,
        CASE
            WHEN (v.runtime_seconds IS NOT NULL) THEN 'version_override'::text
            WHEN (w.total_seconds IS NOT NULL) THEN 'player_total'::text
            WHEN (m.base_runtime_seconds IS NOT NULL) THEN 'base_runtime'::text
            ELSE 'unknown'::text
        END AS runtime_source,
    w.total_seconds,
    w.watched_seconds,
    w.progress_percent,
    w.rating_value,
    w.rating_scale,
    ((COALESCE(v.runtime_seconds, w.total_seconds, m.base_runtime_seconds))::numeric / 3600.0) AS effective_runtime_hours,
    ht.horrorfest_year,
    w.import_batch_id,
    w.created_at
   FROM ((((app.watch_event w
     JOIN app.users u ON ((u.user_id = w.user_id)))
     JOIN app.media_item m ON ((m.media_item_id = w.media_item_id)))
     LEFT JOIN app.media_version v ON ((v.media_version_id = w.media_version_id)))
     LEFT JOIN horrorfest_tags ht ON ((ht.watch_id = w.watch_id)));


--
-- Name: import_batch_error import_batch_error_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.import_batch_error
    ADD CONSTRAINT import_batch_error_pkey PRIMARY KEY (import_batch_error_id);


--
-- Name: import_batch import_batch_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.import_batch
    ADD CONSTRAINT import_batch_pkey PRIMARY KEY (import_batch_id);


--
-- Name: media_item media_item_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_item
    ADD CONSTRAINT media_item_pkey PRIMARY KEY (media_item_id);


--
-- Name: media_version media_version_item_version_uk; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_version
    ADD CONSTRAINT media_version_item_version_uk UNIQUE (media_item_id, media_version_id);


--
-- Name: media_version media_version_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_version
    ADD CONSTRAINT media_version_pkey PRIMARY KEY (media_version_id);


--
-- Name: shows shows_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.shows
    ADD CONSTRAINT shows_pkey PRIMARY KEY (show_id);


--
-- Name: tag tag_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (tag_id);


--
-- Name: tag tag_tag_key_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.tag
    ADD CONSTRAINT tag_tag_key_key UNIQUE (tag_key);


--
-- Name: tmdb_metadata_cache tmdb_metadata_cache_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.tmdb_metadata_cache
    ADD CONSTRAINT tmdb_metadata_cache_pkey PRIMARY KEY (tmdb_type, tmdb_id, sub_key);


--
-- Name: media_item uq_media_imdb; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_item
    ADD CONSTRAINT uq_media_imdb UNIQUE (type, imdb_id);


--
-- Name: media_item uq_media_tmdb; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_item
    ADD CONSTRAINT uq_media_tmdb UNIQUE (type, tmdb_id);


--
-- Name: media_version uq_media_version; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_version
    ADD CONSTRAINT uq_media_version UNIQUE (media_item_id, version_key);


--
-- Name: shows uq_shows_tmdb; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.shows
    ADD CONSTRAINT uq_shows_tmdb UNIQUE (tmdb_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: watch_event watch_event_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event
    ADD CONSTRAINT watch_event_pkey PRIMARY KEY (watch_id);


--
-- Name: watch_event_tag watch_event_tag_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event_tag
    ADD CONSTRAINT watch_event_tag_pkey PRIMARY KEY (watch_id, tag_id);


--
-- Name: ix_import_batch_error_batch; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_import_batch_error_batch ON app.import_batch_error USING btree (import_batch_id);


--
-- Name: ix_import_batch_error_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_import_batch_error_time ON app.import_batch_error USING btree (occurred_at DESC);


--
-- Name: ix_import_batch_started_at; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_import_batch_started_at ON app.import_batch USING btree (started_at DESC);


--
-- Name: ix_import_batch_status; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_import_batch_status ON app.import_batch USING btree (status);


--
-- Name: ix_media_item_show_id; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_media_item_show_id ON app.media_item USING btree (show_id);


--
-- Name: ix_media_item_show_tmdb; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_media_item_show_tmdb ON app.media_item USING btree (show_tmdb_id);


--
-- Name: ix_media_item_tmdb; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_media_item_tmdb ON app.media_item USING btree (tmdb_id);


--
-- Name: ix_media_version_item; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_media_version_item ON app.media_version USING btree (media_item_id);


--
-- Name: ix_shows_imdb_id; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_shows_imdb_id ON app.shows USING btree (imdb_id);


--
-- Name: ix_shows_tvdb_id; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_shows_tvdb_id ON app.shows USING btree (tvdb_id);


--
-- Name: ix_tmdb_cache_expires_at; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_tmdb_cache_expires_at ON app.tmdb_metadata_cache USING btree (expires_at);


--
-- Name: ix_tmdb_cache_fetched_at; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_tmdb_cache_fetched_at ON app.tmdb_metadata_cache USING btree (fetched_at DESC);


--
-- Name: ix_watch_event_source_event; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_watch_event_source_event ON app.watch_event USING btree (playback_source, source_event_id) WHERE (source_event_id IS NOT NULL);


--
-- Name: ix_watch_event_user_media_item_completed; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_watch_event_user_media_item_completed ON app.watch_event USING btree (user_id, media_item_id) WHERE (completed = true);


--
-- Name: ix_watch_event_user_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_watch_event_user_time ON app.watch_event USING btree (user_id, watched_at DESC);


--
-- Name: ix_watch_event_watched_at; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_watch_event_watched_at ON app.watch_event USING btree (watched_at DESC);


--
-- Name: ux_media_item_episode_key; Type: INDEX; Schema: app; Owner: -
--

CREATE UNIQUE INDEX ux_media_item_episode_key ON app.media_item USING btree (show_tmdb_id, season_number, episode_number) WHERE ((type = 'episode'::public.media_type) AND (show_tmdb_id IS NOT NULL));


--
-- Name: ux_watch_event_dedupe_hash; Type: INDEX; Schema: app; Owner: -
--

CREATE UNIQUE INDEX ux_watch_event_dedupe_hash ON app.watch_event USING btree (dedupe_hash) WHERE (dedupe_hash IS NOT NULL);


--
-- Name: media_item trg_create_default_media_version; Type: TRIGGER; Schema: app; Owner: -
--

CREATE TRIGGER trg_create_default_media_version AFTER INSERT ON app.media_item FOR EACH ROW EXECUTE FUNCTION app.create_default_media_version();


--
-- Name: watch_event trg_watch_event_set_dedupe_hash; Type: TRIGGER; Schema: app; Owner: -
--

CREATE TRIGGER trg_watch_event_set_dedupe_hash BEFORE INSERT ON app.watch_event FOR EACH ROW EXECUTE FUNCTION app.set_watch_event_dedupe_hash();


--
-- Name: media_item fk_media_item_show; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_item
    ADD CONSTRAINT fk_media_item_show FOREIGN KEY (show_id) REFERENCES app.shows(show_id) ON DELETE SET NULL;


--
-- Name: watch_event fk_watch_event_import_batch; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event
    ADD CONSTRAINT fk_watch_event_import_batch FOREIGN KEY (import_batch_id) REFERENCES app.import_batch(import_batch_id) ON DELETE SET NULL;


--
-- Name: import_batch_error import_batch_error_import_batch_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.import_batch_error
    ADD CONSTRAINT import_batch_error_import_batch_id_fkey FOREIGN KEY (import_batch_id) REFERENCES app.import_batch(import_batch_id) ON DELETE CASCADE;


--
-- Name: media_version media_version_media_item_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.media_version
    ADD CONSTRAINT media_version_media_item_id_fkey FOREIGN KEY (media_item_id) REFERENCES app.media_item(media_item_id) ON DELETE CASCADE;


--
-- Name: watch_event watch_event_media_item_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event
    ADD CONSTRAINT watch_event_media_item_id_fkey FOREIGN KEY (media_item_id) REFERENCES app.media_item(media_item_id) ON DELETE RESTRICT;


--
-- Name: watch_event watch_event_media_version_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event
    ADD CONSTRAINT watch_event_media_version_id_fkey FOREIGN KEY (media_version_id) REFERENCES app.media_version(media_version_id) ON DELETE SET NULL;


--
-- Name: watch_event_tag watch_event_tag_tag_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event_tag
    ADD CONSTRAINT watch_event_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES app.tag(tag_id) ON DELETE CASCADE;


--
-- Name: watch_event_tag watch_event_tag_watch_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event_tag
    ADD CONSTRAINT watch_event_tag_watch_id_fkey FOREIGN KEY (watch_id) REFERENCES app.watch_event(watch_id) ON DELETE CASCADE;


--
-- Name: watch_event watch_event_user_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event
    ADD CONSTRAINT watch_event_user_id_fkey FOREIGN KEY (user_id) REFERENCES app.users(user_id) ON DELETE CASCADE;


--
-- Name: watch_event watch_event_version_matches_item; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.watch_event
    ADD CONSTRAINT watch_event_version_matches_item FOREIGN KEY (media_item_id, media_version_id) REFERENCES app.media_version(media_item_id, media_version_id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict h5vCqRIUiSU3eNbbSxhckS1olOuDinH91iJdTmF0keoinSI2lv8SwZ3cyZ95qlq

