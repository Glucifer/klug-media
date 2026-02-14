--
-- PostgreSQL database dump
--

\restrict QWQKRYiWEQ5xZrm1XrDvFusFta7FamQWe3CLOoVQHNE9eZvimfPXSlkT8I24Nxe

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

SET default_tablespace = '';

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
-- Name: ix_media_item_tmdb; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_media_item_tmdb ON app.media_item USING btree (tmdb_id);


--
-- Name: ix_media_version_item; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_media_version_item ON app.media_version USING btree (media_item_id);


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
-- Name: ix_watch_event_user_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_watch_event_user_time ON app.watch_event USING btree (user_id, watched_at DESC);


--
-- Name: ix_watch_event_watched_at; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX ix_watch_event_watched_at ON app.watch_event USING btree (watched_at DESC);


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

\unrestrict QWQKRYiWEQ5xZrm1XrDvFusFta7FamQWe3CLOoVQHNE9eZvimfPXSlkT8I24Nxe

