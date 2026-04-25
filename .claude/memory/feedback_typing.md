---
name: No usar Any para tipado
description: El usuario prefiere tipos explícitos sobre Any en anotaciones de tipo Python
type: feedback
---

No usar `Any` de `typing` para resolver errores de tipo en Python. Usar tipos explícitos como `dict[str, str]`, `dict[str, str] | str`, `cast(str, ...)`, etc.

**Why:** El usuario quiere mantener el código bien tipado con tipos concretos, no recurrir a `Any` como escape.

**How to apply:** Cuando haya variables con tipos desconocidos de JSON o SQLAlchemy, inferir la estructura real del dato y tiparlo explícitamente en lugar de usar `Any`.
