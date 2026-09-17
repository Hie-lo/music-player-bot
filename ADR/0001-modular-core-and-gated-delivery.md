# ADR-0001: Modular Core and Gate-Based Delivery

- **Status:** Accepted
- **Date:** 2026-09-17
- **Decision owners:** Project owner and implementation agent

## Context

The product needs Telegram Bot API, an Assistant User Account for Voice Chat, FFmpeg, external media providers, persistent queues/playlists and a future path to additional platforms. Telegram Voice Chat and external provider behavior are not fully controlled by this repository.

A direct implementation that mixes Telegram handlers, media extraction, FFmpeg processes and queue state would be difficult to test and unsafe to extend.

## Decision

1. Use a modular monolith first, with explicit boundaries that can later become deployable services.
2. Keep Domain and Application logic independent from Telegram and any specific media provider.
3. Use ports/adapters for `PlaybackEngine`, `MediaResolver`, repositories and notifications.
4. Give every chat a single playback actor/single writer for serialized commands and idempotency.
5. Treat PostgreSQL as the durable source of truth and Redis as ephemeral coordination/cache.
6. Deliver through gates. The live Voice Chat Proof of Concept must pass before Audio MVP is declared and before Video is considered supported.
7. Classify providers as `GUARANTEED`, `BEST_EFFORT`, `METADATA_ONLY`, `EXPERIMENTAL` or `DISABLED`.
8. Never bypass DRM, paywalls, authentication, geo restrictions, rate limits or provider terms.

## Consequences

### Positive

- Queue and playlist rules can be tested without Telegram.
- The playback library can be replaced without rewriting the application core.
- A provider failure does not have to crash the bot.
- Multiple chats can be isolated and recovered independently.
- Future platform adapters have an explicit extension point.

### Negative

- More interfaces and tests are required before the first end-to-end feature.
- Some integrations cannot be guaranteed and need operational monitoring.
- Video and provider support may remain experimental until live tests pass.

## Rejected alternatives

### Telegram-only handlers with global state

Rejected because race conditions, restarts and multi-chat isolation would be difficult to control.

### Microservices from day one

Rejected because it adds deployment and distributed-systems complexity before the core behavior is proven.

### Treating every Provider as guaranteed

Rejected because provider APIs, policies, authentication requirements and extraction behavior change independently of this project.
