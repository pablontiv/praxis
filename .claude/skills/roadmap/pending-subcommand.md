# /roadmap pending

Vista jerarquica filtrada: solo Features con trabajo pendiente.

## Procedimiento

1. Ejecutar `rootline tree <roadmap-root>/ --where '<where-leaf> && <where-not-done>' --output table`

El tree ya incluye conteos `completed/total` por nodo — NO ejecutar `rootline stats` por separado (es redundante).

Presenta el output al usuario.
