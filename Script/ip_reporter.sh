#!/usr/bin/env bash
# =============================================================================
# IP Reporter — Reports current public IP to a GitLab repository file
# Retries up to 10 times with 10s delay on failure
# =============================================================================

set -euo pipefail

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
# Set these via environment variables or edit directly:
#   GITLAB_TOKEN        — Personal Access Token (api scope)
#   GITLAB_PROJECT_ID   — Numeric project ID or URL-encoded path (e.g. "group%2Fproject")
#   GITLAB_FILE_PATH    — Path to file in repo (e.g. "public_ip.txt")
#   GITLAB_BRANCH       — Target branch (default: "main")
#   GITLAB_API_URL      — GitLab instance (default: "https://gitlab.com/api/v4")
#   IP_SERVICES         — Space-separated list of IP lookup endpoints
#   MAX_RETRIES         — Max attempts (default: 10)
#   RETRY_DELAY         — Seconds between retries (default: 10)

GITLAB_TOKEN="${GITLAB_TOKEN:-}"
GITLAB_PROJECT_ID="${GITLAB_PROJECT_ID:-}"
GITLAB_FILE_PATH="${GITLAB_FILE_PATH:-public_ip.txt}"
GITLAB_BRANCH="${GITLAB_BRANCH:-main}"
GITLAB_API_URL="${GITLAB_API_URL:-https://gitlab.com/api/v4}"
IP_SERVICES="${IP_SERVICES:-https://api.ipify.org https://ifconfig.me https://icanhazip.com https://ipinfo.io/ip}"
MAX_RETRIES="${MAX_RETRIES:-10}"
RETRY_DELAY="${RETRY_DELAY:-10}"

# ─── VALIDATION ─────────────────────────────────────────────────────────────
if [[ -z "$GITLAB_TOKEN" || -z "$GITLAB_PROJECT_ID" ]]; then
    echo "ERROR: GITLAB_TOKEN and GITLAB_PROJECT_ID must be set" >&2
    echo "Export them or edit the script." >&2
    exit 1
fi

# ─── HELPERS ────────────────────────────────────────────────────────────────
log() { echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $*"; }
err() { log "ERROR: $*" >&2; }

# Check internet connectivity
check_internet() {
    # Try a quick DNS + TCP check
    if command -v curl >/dev/null 2>&1; then
        curl -sSf --max-time 5 "https://1.1.1.1/cdn-cgi/trace" >/dev/null 2>&1 && return 0
        curl -sSf --max-time 5 "https://8.8.8.8" >/dev/null 2>&1 && return 0
    elif command -v wget >/dev/null 2>&1; then
        wget -q --spider --timeout=5 "https://1.1.1.1/cdn-cgi/trace" 2>/dev/null && return 0
    fi
    return 1
}

# Fetch public IP from multiple services (first success wins)
fetch_ip() {
    local ip=""
    for svc in $IP_SERVICES; do
        if command -v curl >/dev/null 2>&1; then
            ip=$(curl -sSf --max-time 10 "$svc" 2>/dev/null | tr -d '[:space:]')
        elif command -v wget >/dev/null 2>&1; then
            ip=$(wget -qO- --timeout=10 "$svc" 2>/dev/null | tr -d '[:space:]')
        fi
        if [[ -n "$ip" && "$ip" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then
            echo "$ip"
            return 0
        fi
    done
    return 1
}

# Get current file content + SHA from GitLab (for update)
get_file_info() {
    local encoded_path
    encoded_path=$(printf '%s' "$GITLAB_FILE_PATH" | jq -sRr @uri)
    local url="${GITLAB_API_URL}/projects/${GITLAB_PROJECT_ID}/repository/files/${encoded_path}?ref=${GITLAB_BRANCH}"

    local response
    response=$(curl -sSf --max-time 15 \
        -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
        "$url" 2>/dev/null) || return 1

    echo "$response"
}

# Commit new IP to GitLab file
commit_ip() {
    local ip="$1"
    local timestamp
    timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    local content="${ip}  # Updated: ${timestamp}"
    local encoded_content
    encoded_content=$(printf '%s' "$content" | base64 -w0)

    # Try to get existing file SHA (for update)
    local file_info sha=""
    if file_info=$(get_file_info); then
        sha=$(printf '%s' "$file_info" | jq -r '.sha // empty')
    fi

    local action="create"
    [[ -n "$sha" ]] && action="update"

    local payload
    payload=$(jq -n \
        --arg branch "$GITLAB_BRANCH" \
        --arg path "$GITLAB_FILE_PATH" \
        --arg content "$content" \
        --arg commit_msg "chore: update public IP to ${ip} (${timestamp})" \
        --arg action "$action" \
        --argjson encoding '"base64"' \
        '{
            branch: $branch,
            start_branch: $branch,
            actions: [{
                action: $action,
                file_path: $path,
                content: $content,
                encoding: $encoding
            }],
            commit_message: $commit_msg
        }')

    local url="${GITLAB_API_URL}/projects/${GITLAB_PROJECT_ID}/repository/commits"
    local response
    response=$(curl -sSf --max-time 20 \
        -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "$payload" \
        "$url" 2>/dev/null) || return 1

    printf '%s' "$response" | jq -e '.id' >/dev/null
}

# ─── MAIN LOOP ──────────────────────────────────────────────────────────────
attempt=0
while (( attempt < MAX_RETRIES )); do
    attempt=$((attempt + 1))
    log "Attempt ${attempt}/${MAX_RETRIES}"

    # 1. Check internet
    if ! check_internet; then
        err "No internet connectivity"
    else
        log "Internet OK"

        # 2. Fetch IP
        if ip=$(fetch_ip); then
            log "Public IP: ${ip}"

            # 3. Send to GitLab
            if commit_ip "$ip"; then
                log "SUCCESS: IP committed to GitLab (${GITLAB_FILE_PATH} @ ${GITLAB_BRANCH})"
                exit 0
            else
                err "Failed to commit IP to GitLab"
            fi
        else
            err "Could not determine public IP"
        fi
    fi

    # Retry logic
    if (( attempt < MAX_RETRIES )); then
        log "Waiting ${RETRY_DELAY}s before retry..."
        sleep "$RETRY_DELAY"
    fi
done

err "Max retries (${MAX_RETRIES}) exceeded. Aborting."
exit 1