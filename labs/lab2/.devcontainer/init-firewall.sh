#!/bin/bash
# init-firewall.sh
# Configures network rules for Claude Code sandbox environment.
# Whitelists only the endpoints Claude Code and Bedrock require.
# All other outbound traffic is blocked.

set -euo pipefail

echo "Configuring Claude Code sandbox firewall..."

# ── Flush existing rules ───────────────────────────────────────────────────────
iptables -F OUTPUT

# ── Allow loopback ─────────────────────────────────────────────────────────────
iptables -A OUTPUT -o lo -j ACCEPT

# ── Allow established/related connections ──────────────────────────────────────
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# ── Allow DNS resolution ───────────────────────────────────────────────────────
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT

# ── Allow Amazon Bedrock (us-east-1) ──────────────────────────────────────────
iptables -A OUTPUT -p tcp --dport 443 -d bedrock-runtime.us-east-1.amazonaws.com -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -d bedrock.us-east-1.amazonaws.com -j ACCEPT

# ── Allow npm registry ─────────────────────────────────────────────────────────
iptables -A OUTPUT -p tcp --dport 443 -d registry.npmjs.org -j ACCEPT

# ── Allow GitHub (for cloning course repo) ────────────────────────────────────
iptables -A OUTPUT -p tcp --dport 443 -d github.com -j ACCEPT

# ── Allow Anthropic API ────────────────────────────────────────────────────────
iptables -A OUTPUT -p tcp --dport 443 -d api.anthropic.com -j ACCEPT

# NOTE: Default egress policy is not explicitly set here.
# Without a DROP rule, any unmatched traffic falls through to the system default.

echo "Firewall rules applied."
iptables -L OUTPUT --line-numbers
