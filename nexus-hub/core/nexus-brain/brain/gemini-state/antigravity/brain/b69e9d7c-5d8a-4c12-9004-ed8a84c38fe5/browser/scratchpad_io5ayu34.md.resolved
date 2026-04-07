# Task: Find and summarize 'deploy.mp4' on stacknaut.com

## Progress Checklist
- [x] Visit stacknaut.com
- [x] Search for 'deploy.mp4' or deployment demonstration video
- [x] Watch the video (if found)
- [x] Summarize the content and deployment process

## Findings
- Found `https://stacknaut.com/deploy.mp4` embedded as a video on the home page.
- Video shows an AI agent (DROID) handling a full development cycle in a terminal (Ghostty + tmux).
- Project name: `myog/myog.social`.
- Deployment process:
    1. Agent plans tasks: review, commit, log, deploy.
    2. Agent edits code (`botDetector.ts`), runs `prettier` and `tsc --noEmit`.
    3. Agent logs the change using a custom script (`log-task.ts`).
    4. **Actual deploy step:** Agent executes `scripts/push-and-deploy.sh`.
    5. The script uses **Kamal 2** for zero-downtime deployment (verified by checking `docker ps` and `kamal deploy` documentation).
    6. Deployment seems very fast (finished the docker check in less than 1 second in the DEMO).
- Stack used: Vue, TypeScript, Fastify, PostgreSQL, Stripe, Hetzner, Terraform, Kamal 2.
