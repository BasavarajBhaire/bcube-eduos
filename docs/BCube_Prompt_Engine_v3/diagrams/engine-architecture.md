# BCube Prompt Engine v3.0 architecture

```mermaid
flowchart TB
    A["Page data + curriculum intent"] --> B["Core engines 1-8"]
    B --> C["Quality Assurance Engine"]
    C --> D["Prompt Compiler"]
    D --> E["BCube Gold Production Prompt"]
    E --> F["Generated page + validation record"]
```

## Compilation order

```mermaid
flowchart TB
    P["Publishing"] --> D["Design"]
    D --> V["Visual Grammar"]
    V --> E["Educational"]
    E --> T["Teaching"]
    T --> PP["Parent Partnership"]
    PP --> I["Illustration"]
    I --> C["Character"]
    C --> Q["Quality Assurance"]
    Q --> PC["Prompt Compiler"]
```

Rules inherit from global to book to unit to page. More specific overrides are accepted only when their authority, rationale, and compatibility are valid and recorded.
