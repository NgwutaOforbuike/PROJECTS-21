from __future__ import annotations
import re

_PATTERNS=[
    re.compile(r"(?i)(api[_-]?key|secret|token|password|authorization)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+=*"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
]

def redact(value:str)->str:
    out=value
    for p in _PATTERNS:
        out=p.sub(lambda m:(m.group(1)+"=[REDACTED]") if m.lastindex and m.lastindex>=1 else "[REDACTED]",out)
    return out
