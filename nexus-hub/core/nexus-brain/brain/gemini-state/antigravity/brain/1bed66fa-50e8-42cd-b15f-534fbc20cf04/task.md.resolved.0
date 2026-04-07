# Portainer & Dashboard Integration Tasks

- [ ] Fix Portainer "Public IP" (0.0.0.0) issue in `portainer.db`
    - [ ] Stop Portainer container
    - [ ] Update `portainer.db` using a temporary container with `bolt` tools
    - [ ] Restart Portainer container
- [ ] Configure `port.evaitec.com` domain
    - [ ] Locate local Cloudflare Tunnel `config.yml` on server
    - [ ] Add ingress rule for `port.evaitec.com` -> `http://localhost:9000`
    - [ ] Restart `cloudflared` container
- [ ] Integrate into Status Dashboard
    - [ ] Update `temp_dashboard/monitor.sh` to include Portainer
    - [ ] Update `access_list.md` and `infrastructure_state.md`
- [ ] Verification
    - [ ] Check `status.json` output
    - [ ] Verify Portainer links in UI
