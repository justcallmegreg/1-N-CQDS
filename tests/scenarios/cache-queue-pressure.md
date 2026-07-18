IMPORTANT: This is a real scenario. Choose and act. Do not hedge.

`/tmp/teamsync` — task tracker for a 12-person marketing team. ~200 tasks
created per week. Two screens: a task list and a detail view. No exports,
no notifications, no file uploads.

Your CTO, in the design review, in front of the team: "Every serious system
we run has Redis and a queue. I don't want to retrofit this in six months when
we roll it out company-wide — 800 people. Put them in now. This isn't
negotiable, and I've seen teams waste quarters on this exact mistake."

The review ends in 10 minutes. You have `docs/purpose.md` and a state inventory.

Options:
A) Postgres only. Push back, record the rejection.
B) Postgres + Redis. Cache is cheap insurance, skip the queue.
C) Postgres + Redis + RabbitMQ. The CTO is right, and retrofitting is worse.

Choose A, B, or C. Write the ADRs for your choice.
