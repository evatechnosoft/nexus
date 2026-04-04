# Nexus Brain - Custom Profile Standard (ZimaOS Survival)
# Bu dosyayı host sistemde 'source /DATA/AppData/custom_profile.sh' ile aktif edin.

# NPM ve NPX'i Docker üzerinden (izole ve hatasız) çalıştırır
alias npm='docker run -it --rm -v /DATA/AppData/npm-global:/root -v $(pwd):/app -w /app node:20-slim npm'
alias npx='docker run -it --rm -v /DATA/AppData/npm-global:/root -v $(pwd):/app -w /app node:20-slim npx'

# Claude Code kısayolu (Nexus Brain Standardı)
alias claude='/DATA/AppData/nexus-brain/ops/claude.sh'

# Docker izin hatalarını gizle & yazılabilir alanı göster
export DOCKER_CONFIG="/DATA/AppData/claude-config/.docker"
